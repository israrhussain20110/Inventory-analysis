import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_validated_data
from models import RetailData
from datetime import datetime, timedelta
from services.data_preprocessing import preprocess_inventory_data, preprocess_sales_data, preprocess_stockouts_data
import json
from pydantic import BaseModel

# Load API descriptions
try:
    with open("api_descriptions.json", "r") as f:
        API_DESCRIPTIONS = json.load(f)
except FileNotFoundError:
    API_DESCRIPTIONS = {} # Handle case where file is not found
except json.JSONDecodeError:
    API_DESCRIPTIONS = {} # Handle case where JSON is invalid

def _add_description_to_output(output, metric_key: str):
    if not API_DESCRIPTIONS:
        return output

    metric_output_key = ""
    if metric_key in ["turnover", "stockout_rate", "days_of_supply", "carrying_cost"]:
        metric_output_key = "inventory_metrics_output"
    elif metric_key in ["slow_movers", "obsolete_items"]:
        metric_output_key = "slow_obsolete_items_output"
    else:
        return output # No description found

    if metric_output_key not in API_DESCRIPTIONS:
        return output

    sections = API_DESCRIPTIONS[metric_output_key].get("sections", [])
    
    target_section = None
    for section in sections:
        if section.get("key") == metric_key:
            target_section = section
            break
    
    if not target_section:
        return output

    description_to_add = target_section.get("description", "")

    if isinstance(output, dict):
        if "error" in output: # Don't add description to error messages
            return output
        output["description"] = description_to_add
    elif isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                item["description"] = description_to_add
    return output

def calculate_turnover(item_id: str = None, category: str = None, abc_class: str = None, period: str = 'monthly'):
    query = {}
    if item_id:
        query["ProductID"] = item_id
    if category:
        query["Category"] = category
    if abc_class:
        query["abc_class"] = abc_class

    retail_data = get_validated_data(RetailData, "retail_data", query)

    if not retail_data:
        return {"error": "Insufficient data for calculation."}

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df) # This preprocesses the entire dataframe

    # Ensure necessary columns exist after preprocessing
    if 'Inventory' not in df.columns or 'Sales' not in df.columns or 'Price' not in df.columns:
        return {"error": "Required columns (Inventory, Sales, Price) missing after preprocessing."}

    # Calculate COGS (Cost of Goods Sold)
    df['COGS'] = df['Sales'] * df['Price']

    # Calculate Average Inventory Value
    # Assuming 'cost' is already calculated and present in the dataframe from load_csv_to_db.py
    # If not, it needs to be calculated here or in preprocessing
    if 'cost' not in df.columns:
        df['cost'] = df['Price'] * 0.8 # Fallback if 'cost' is not present

    df['InventoryValue'] = df['Inventory'] * df['cost']
    avg_inventory_value = df['InventoryValue'].mean()

    if pd.isna(avg_inventory_value) or avg_inventory_value == 0:
        return {"error": "Average inventory value is zero or undefined, cannot calculate turnover."}

    # Resample COGS by period
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    cogs_over_time = df['COGS'].resample(period[0].upper()).sum()

    turnover_df = (cogs_over_time / avg_inventory_value).reset_index()
    turnover_df.rename(columns={0: 'turnover_ratio'}, inplace=True)
    turnover_df.replace([float('inf'), -float('inf')], None, inplace=True)

    results = turnover_df.to_dict('records')

    if item_id and results:
        return _add_description_to_output(results[0], "turnover")
    elif not item_id:
        return _add_description_to_output(results, "turnover")
    else:
        return {"turnover_ratio": 0, "message": "No data for the given item ID."}

def calculate_stockout_rate(item_id: str = None):
    """
    Calculates the stockout rate, frequency, and duration.
    Stockout Rate = (Number of Stockouts / Number of Sales) * 100
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    retail_data = get_validated_data(RetailData, "retail_data", query)

    if not retail_data:
        return {"error": "Insufficient data for calculation."}

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df) # Preprocess the entire dataframe

    # Identify stockout events: Inventory is 0 and there are Sales > 0
    stockout_events = df[(df['Inventory'] <= 0) & (df['Sales'] > 0)]

    num_stockouts = len(stockout_events)
    num_sales = len(df[df['Sales'] > 0]) # Total sales records where units were sold

    if num_sales == 0:
        return {"stockout_rate": 0, "message": "No sales, so stockout rate is 0."}

    stockout_rate = (num_stockouts / num_sales) * 100

    stockout_frequency = num_stockouts
    avg_duration = 0
    # If there's a 'duration' column in the original inventory data that indicates stockout duration
    if 'duration' in stockout_events.columns:
        avg_duration = stockout_events['duration'].mean()

    result = {
        "stockout_rate": stockout_rate,
        "stockout_frequency": stockout_frequency,
        "average_duration": avg_duration
    }
    return _add_description_to_output(result, "stockout_rate")

def calculate_stockout_heatmap_data(item_id: str = None):
    """
    Generates data for a stockout heatmap.
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    retail_data = get_validated_data(RetailData, "retail_data", query)

    if not retail_data:
        return []

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df) # Preprocess the entire dataframe

    # Identify stockout events
    stockout_events = df[(df['Inventory'] <= 0) & (df['Sales'] > 0)]

    if stockout_events.empty:
        return []

    df = stockout_events.copy()
    
    df['month'] = df['Date'].dt.to_period('M').astype(str)
    
    heatmap_data = df.groupby(['ProductID', 'month']).size().reset_index(name='stockout_count')
    
    return heatmap_data.to_dict('records')

def calculate_days_of_supply(item_id: str = None):
    """
    Calculates the days of supply for an item or all items.
    Days of Supply = Current Inventory / Avg Daily Demand
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    retail_data = get_validated_data(RetailData, "retail_data", query)

    if not retail_data:
        return {"error": "Insufficient data."}

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df) # Preprocess the entire dataframe

    if 'Inventory' not in df.columns or 'ProductID' not in df.columns:
        return {"error": "Inventory data missing 'Inventory' or 'ProductID'."}

    if 'Sales' not in df.columns or 'Date' not in df.columns or 'ProductID' not in df.columns:
        return {"error": "Sales data missing 'Sales', 'Date', or 'ProductID'."}
    
    if item_id:
        df = df[df['ProductID'] == item_id]

    if df.empty:
        return {"days_of_supply": 0, "message": "No data for the given item ID."}

    results = []
    for item in df['ProductID'].unique():
        # Use the last known inventory level as current inventory
        current_inventory = df[df['ProductID'] == item].sort_values(by='Date', ascending=False).iloc[0]['Inventory']
        
        item_sales = df[df['ProductID'] == item]
        if not item_sales.empty:
            total_days = (item_sales['Date'].max() - item_sales['Date'].min()).days
            if total_days == 0:
                total_days = 1
            avg_daily_demand = item_sales['Sales'].sum() / total_days
        else:
            avg_daily_demand = 0

        if avg_daily_demand == 0:
            days_of_supply = None
        else:
            days_of_supply = current_inventory / avg_daily_demand
        
        results.append({"item_id": item, "days_of_supply": days_of_supply})

    if item_id and results:
        return _add_description_to_output(results[0], "days_of_supply")
    elif not item_id:
        return _add_description_to_output(results, "days_of_supply")
    else:
        return {"days_of_supply": 0, "message": "No data for the given item ID."}

def calculate_carrying_cost(item_id: str = None, carrying_cost_rate: float = 0.20):
    """
    Calculates the carrying cost of inventory for an item or all items.
    Carrying Cost = Avg Inventory Value * Carrying Cost Rate
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    retail_data = get_validated_data(RetailData, "retail_data", query)

    if not retail_data:
        return {"error": "No inventory data found."}

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df) # Preprocess the entire dataframe

    if 'Inventory' not in df.columns or 'ProductID' not in df.columns:
        return {"error": "Inventory data missing required 'Inventory' or 'ProductID' columns."}

    if item_id:
        df = df[df['ProductID'] == item_id]

    if df.empty:
        return {"carrying_cost": 0, "message": "No data for the given item ID."}

    results = []
    for item in df['ProductID'].unique():
        item_inventory = df[df['ProductID'] == item]
        # Use the 'cost' field if available, otherwise default to 1
        inventory_value = item_inventory.get('cost', 1) * item_inventory['Inventory']
        avg_inventory_value = inventory_value.mean()
        if pd.isna(avg_inventory_value):
            avg_inventory_value = None
        
        if avg_inventory_value is None:
            carrying_cost = None
        else:
            carrying_cost = avg_inventory_value * carrying_cost_rate
        results.append({"item_id": item, "carrying_cost": carrying_cost})

    if item_id and results:
        return _add_description_to_output(results[0], "carrying_cost")
    elif not item_id:
        return _add_description_to_output(results, "carrying_cost")
    else:
        return {"carrying_cost": 0, "message": "No data for the given item ID."}

def detect_slow_obsolete_items(
    slow_turnover_threshold: float = 2.0,
    dos_threshold: int = 180,
    inactivity_days: int = 180
) -> dict:
    """
    Detects slow-moving and obsolete items based on given thresholds.
    """
    retail_data = get_validated_data(RetailData, "retail_data")
    if not retail_data:
        return {"error": "No inventory data found."}

    df = pd.DataFrame([item.dict() for item in retail_data]).copy()
    df = preprocess_inventory_data(df)
    df['Date'] = pd.to_datetime(df['Date'])

    # Calculate turnover ratio for each item
    df['COGS'] = df['Sales'] * df['Price']
    if 'cost' not in df.columns:
        df['cost'] = df['Price'] * 0.8
    df['InventoryValue'] = df['Inventory'] * df['cost']
    
    avg_inventory_value = df.groupby('ProductID')['InventoryValue'].mean()
    total_cogs = df.groupby('ProductID')['COGS'].sum()
    
    turnover_ratio = (total_cogs / avg_inventory_value).reset_index(name='turnover_ratio')
    turnover_ratio.replace([float('inf'), -float('inf')], None, inplace=True)
    turnover_ratio.fillna(float('inf'), inplace=True)


    # Calculate days of supply for each item
    current_inventory = df.loc[df.groupby('ProductID')['Date'].idxmax()][['ProductID', 'Inventory']]
    current_inventory.rename(columns={'Inventory': 'current_inventory'}, inplace=True)
    
    sales_data = df.groupby('ProductID').agg(
        total_sales=('Sales', 'sum'),
        min_date=('Date', 'min'),
        max_date=('Date', 'max')
    ).reset_index()

    sales_data['duration_days'] = (sales_data['max_date'] - sales_data['min_date']).dt.days
    sales_data['duration_days'] = sales_data['duration_days'].apply(lambda x: 1 if x == 0 else x)
    sales_data['avg_daily_demand'] = sales_data['total_sales'] / sales_data['duration_days']

    dos_df = pd.merge(current_inventory, sales_data, on='ProductID')
    dos_df['days_of_supply'] = dos_df['current_inventory'] / dos_df['avg_daily_demand']
    dos_df['days_of_supply'].replace([float('inf'), -float('inf')], None, inplace=True)
    dos_df.fillna(0, inplace=True)


    # Merge metrics
    metrics_df = pd.merge(turnover_ratio, dos_df[['ProductID', 'days_of_supply']], on='ProductID', how='left')
    metrics_df.rename(columns={'ProductID': 'item_id'}, inplace=True)

    # Detect slow movers
    slow_movers = metrics_df[
        (metrics_df['turnover_ratio'] < slow_turnover_threshold) |
        (metrics_df['days_of_supply'] > dos_threshold)
    ]['item_id'].tolist()

    # Detect obsolete items
    last_sale_dates = df.groupby('ProductID')['Date'].max().reset_index()
    obsolete_threshold_date = datetime.now() - timedelta(days=inactivity_days)
    obsolete_items = last_sale_dates[
        last_sale_dates['Date'] < obsolete_threshold_date
    ]['ProductID'].tolist()

    # Items with no sales data are also obsolete
    items_with_sales = df[df['Sales'] > 0]['ProductID'].unique()
    all_items = df['ProductID'].unique()
    items_without_sales = list(set(all_items) - set(items_with_sales))
    obsolete_items.extend(items_without_sales)

    return {"slow_movers": list(set(slow_movers)), "obsolete_items": list(set(obsolete_items))}