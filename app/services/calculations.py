import pandas as pd
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_validated_data
from app.models import InventoryItem, SalesRecord
from datetime import datetime, timedelta
from app.services.data_preprocessing import preprocess_inventory_data, preprocess_sales_data, preprocess_stockouts_data

def calculate_turnover(item_id: str = None, period: str = 'monthly'):
    """
    Calculates the inventory turnover ratio over a specified period.
    Turnover = COGS / Avg Inventory
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    inventory_data = get_validated_data("inventory", InventoryItem, query)
    sales_data = get_validated_data("sales", SalesRecord, query)

    if not inventory_data or not sales_data:
        return {"error": "Insufficient data for calculation."}

    df_inventory = pd.DataFrame(inventory_data).copy()
    df_inventory = preprocess_inventory_data(df_inventory)
    df_sales = pd.DataFrame(sales_data).copy()
    df_sales = preprocess_sales_data(df_sales)

    if 'InventoryLevel' not in df_inventory.columns:
        return {"error": "Inventory data is missing required 'InventoryLevel' column."}

    if 'UnitsSold' not in df_sales.columns or 'Price' not in df_sales.columns or 'Date' not in df_sales.columns:
        return {"error": "Sales data is missing required 'UnitsSold', 'Price', or 'Date' columns."}

    df_sales['COGS'] = df_sales['Price'] * df_sales['UnitsSold']
    df_sales['Date'] = pd.to_datetime(df_sales['Date'])
    df_sales.set_index('Date', inplace=True)

    cogs_over_time = df_sales['COGS'].resample(period[0].upper()).sum()
    avg_inventory = df_inventory['InventoryLevel'].mean()

    if avg_inventory == 0:
        return pd.DataFrame({'turnover_ratio': [float('inf')] * len(cogs_over_time)}, index=cogs_over_time.index)

    turnover_df = (cogs_over_time / avg_inventory).reset_index()
    turnover_df.rename(columns={0: 'turnover_ratio'}, inplace=True)

    results = turnover_df.to_dict('records')

    if item_id and results:
        return results[0]
    elif not item_id:
        return results
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

    stockouts_data = get_validated_data("stockouts", SalesRecord, query) # Assuming stockouts are also sales records
    sales_data = get_validated_data("sales", SalesRecord, query)

    if not sales_data:
        return {"error": "No sales data found for the given query."}

    df_stockouts = pd.DataFrame([item.dict() for item in stockouts_data]).copy()
    df_stockouts = preprocess_stockouts_data(df_stockouts)

    df_sales = pd.DataFrame(sales_data).copy()
    df_sales = preprocess_sales_data(df_sales)

    num_stockouts = len(df_stockouts)
    num_sales = len(df_sales)

    if num_sales == 0:
        return {"stockout_rate": 0, "message": "No sales, so stockout rate is 0."}

    stockout_rate = (num_stockouts / num_sales) * 100

    stockout_frequency = num_stockouts
    avg_duration = 0
    if not df_stockouts.empty:
        if 'duration' in df_stockouts.columns:
            avg_duration = df_stockouts['duration'].mean()

    return {
        "stockout_rate": stockout_rate,
        "stockout_frequency": stockout_frequency,
        "average_duration": avg_duration
    }

def calculate_stockout_heatmap_data(item_id: str = None):
    """
    Generates data for a stockout heatmap.
    """
    query = {}
    if item_id:
        query["ProductID"] = item_id

    stockouts_data = get_validated_data("stockouts", SalesRecord, query)

    if not stockouts_data:
        return []

    df = pd.DataFrame([item.dict() for item in stockouts_data]).copy()
    df = preprocess_stockouts_data(df)
    
    df['month'] = df['Date'].dt.to_period('M').astype(str)
    
    heatmap_data = df.groupby(['ProductID', 'month']).size().reset_index(name='stockout_count')
    
    return heatmap_data.to_dict('records')

def calculate_days_of_supply(item_id: str = None):
    """
    Calculates the days of supply for an item or all items.
    Days of Supply = Current Inventory / Avg Daily Demand
    """
    inventory_data = get_validated_data("inventory", InventoryItem)
    sales_data = get_validated_data("sales", SalesRecord)

    if not inventory_data or not sales_data:
        return {"error": "Insufficient data."}

    df_inventory = pd.DataFrame(inventory_data).copy()
    df_inventory = preprocess_inventory_data(df_inventory)
    df_sales = pd.DataFrame(sales_data).copy()
    df_sales = preprocess_sales_data(df_sales)

    if 'InventoryLevel' not in df_inventory.columns or 'ProductID' not in df_inventory.columns:
        return {"error": "Inventory data missing 'InventoryLevel' or 'ProductID'."}

    if 'UnitsSold' not in df_sales.columns or 'Date' not in df_sales.columns or 'ProductID' not in df_sales.columns:
        return {"error": "Sales data missing 'UnitsSold', 'Date', or 'ProductID'."}
    
    if item_id:
        df_inventory = df_inventory[df_inventory['ProductID'] == item_id]
        df_sales = df_sales[df_sales['ProductID'] == item_id]

    if df_inventory.empty or df_sales.empty:
        return {"days_of_supply": 0, "message": "No data for the given item ID."}

    results = []
    for item in df_inventory['ProductID'].unique():
        current_inventory = df_inventory[df_inventory['ProductID'] == item]['InventoryLevel'].sum()
        
        item_sales = df_sales[df_sales['ProductID'] == item]
        if not item_sales.empty:
            total_days = (item_sales['Date'].max() - item_sales['Date'].min()).days
            if total_days == 0:
                total_days = 1
            avg_daily_demand = item_sales['UnitsSold'].sum() / total_days
        else:
            avg_daily_demand = 0

        if avg_daily_demand == 0:
            days_of_supply = float('inf')
        else:
            days_of_supply = current_inventory / avg_daily_demand
        
        results.append({"item_id": item, "days_of_supply": days_of_supply})

    if item_id and results:
        return results[0]
    elif not item_id:
        return results
    else:
        return {"days_of_supply": 0, "message": "No data for the given item ID."}

def calculate_carrying_cost(item_id: str = None, carrying_cost_rate: float = 0.20):
    """
    Calculates the carrying cost of inventory for an item or all items.
    Carrying Cost = Avg Inventory Value * Carrying Cost Rate
    """
    inventory_data = get_validated_data("inventory", InventoryItem)

    if not inventory_data:
        return {"error": "No inventory data found."}

    df_inventory = pd.DataFrame(inventory_data).copy()
    df_inventory = preprocess_inventory_data(df_inventory)

    if 'InventoryLevel' not in df_inventory.columns or 'ProductID' not in df_inventory.columns:
        return {"error": "Inventory data missing required 'InventoryLevel' or 'ProductID' columns."}

    if item_id:
        df_inventory = df_inventory[df_inventory['ProductID'] == item_id]

    if df_inventory.empty:
        return {"carrying_cost": 0, "message": "No data for the given item ID."}

    results = []
    for item in df_inventory['ProductID'].unique():
        item_inventory = df_inventory[df_inventory['ProductID'] == item]
        inventory_value = 1 * item_inventory['InventoryLevel']
        avg_inventory_value = inventory_value.mean()
        carrying_cost = avg_inventory_value * carrying_cost_rate
        results.append({"item_id": item, "carrying_cost": carrying_cost})

    if item_id and results:
        return results[0]
    elif not item_id:
        return results
    else:
        return {"carrying_cost": 0, "message": "No data for the given item ID."}

def detect_slow_obsolete_items(
    slow_turnover_threshold: float = 2.0,
    dos_threshold: int = 180,
    inactivity_days: int = 180
):
    """
    Detects slow-moving and obsolete items based on given thresholds.
    """
    inventory_data = get_validated_data("inventory", InventoryItem)
    if not inventory_data:
        return {"error": "No inventory data found."}

    df_inventory = pd.DataFrame(inventory_data).copy()
    print("Columns before preprocessing:", df_inventory.columns) # Debug print
    df_inventory = preprocess_inventory_data(df_inventory)
    print("Columns after preprocessing:", df_inventory.columns) # Debug print
    all_item_ids = df_inventory['ProductID'].unique()

    slow_movers = []
    obsolete_items = []

    for item_id in all_item_ids:
        turnover_result = calculate_turnover(item_id)
        dos_result = calculate_days_of_supply(item_id)

        if not isinstance(turnover_result, dict) or 'error' in turnover_result:
            continue

        if not isinstance(dos_result, dict) or 'error' in dos_result:
            continue

        if turnover_result.get('turnover_ratio', float('inf')) < slow_turnover_threshold or \
           dos_result.get('days_of_supply', 0) > dos_threshold:
            slow_movers.append(item_id)

        sales_data = get_validated_data("sales", SalesRecord, {"ProductID": item_id})
        if not sales_data:
            obsolete_items.append(item_id)
            continue

        df_sales = pd.DataFrame(sales_data).copy()
        df_sales['Date'] = pd.to_datetime(df_sales['Date'])
        last_sale_date = df_sales['Date'].max()

        if last_sale_date < datetime.now() - timedelta(days=inactivity_days):
            obsolete_items.append(item_id)

    return {"slow_movers": slow_movers, "obsolete_items": obsolete_items}