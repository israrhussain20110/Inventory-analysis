import pandas as pd
from app.database import get_data
from datetime import datetime, timedelta
from app.services.data_preprocessing import preprocess_inventory_data, preprocess_sales_data, preprocess_stockouts_data

def calculate_turnover(item_id: str = None, period: str = 'monthly'):
    """
    Calculates the inventory turnover ratio over a specified period.
    Turnover = COGS / Avg Inventory
    """
    query = {}
    if item_id:
        query["item_id"] = item_id

    inventory_data = get_data("inventory", query)
    sales_data = get_data("sales", query)

    if not inventory_data or not sales_data:
        return {"error": "Insufficient data for calculation."}
    df_inventory = pd.DataFrame(inventory_data)
    df_inventory = preprocess_inventory_data(df_inventory)
    df_sales = pd.DataFrame(sales_data)
    df_sales = preprocess_sales_data(df_sales)

    if 'Inventory Level' not in df_inventory.columns:
        return {"error": "Inventory data is missing required 'Inventory Level' column."}

    if 'COGS' not in df_sales.columns or 'date' not in df_sales.columns:
        return {"error": "Sales data is missing required 'COGS' or 'date' columns."}

    df_sales['date'] = pd.to_datetime(df_sales['date'])
    df_sales.set_index('date', inplace=True)

    # Resample COGS based on the period
    cogs_over_time = df_sales['COGS'].resample(period[0].upper()).sum()

    # For simplicity, we'll use the mean of the entire inventory as the average for each period.
    # A more complex implementation could calculate the average inventory for each period.
    avg_inventory = df_inventory['Inventory Level'].mean()

    if avg_inventory == 0:
        return pd.DataFrame({'turnover_ratio': [float('inf')] * len(cogs_over_time)}, index=cogs_over_time.index)

    turnover_df = (cogs_over_time / avg_inventory).reset_index()
    turnover_df.rename(columns={0: 'turnover_ratio'}, inplace=True)

    return turnover_df.to_dict('records')

def calculate_stockout_rate(item_id: str = None):
    """
    Calculates the stockout rate, frequency, and duration.
    Stockout Rate = (Number of Stockouts / Number of Sales) * 100
    """
    query = {}
    if item_id:
        query["item_id"] = item_id

    stockouts_data = get_data("stockouts", query)
    sales_data = get_data("sales", query)

    if not sales_data:
        return {"error": "No sales data found for the given query."}

    # Preprocess dataframes
    df_stockouts_raw = pd.DataFrame(stockouts_data)
    df_stockouts = preprocess_stockouts_data(df_stockouts_raw)

    df_sales_raw = pd.DataFrame(sales_data)
    df_sales = preprocess_sales_data(df_sales_raw)

    num_stockouts = len(df_stockouts) # Use preprocessed df
    num_sales = len(df_sales) # Use preprocessed df

    if num_sales == 0:
        return {"stockout_rate": 0, "message": "No sales, so stockout rate is 0."}

    stockout_rate = (num_stockouts / num_sales) * 100

    # For now, frequency and duration are just the number of stockouts
    # and the average duration from the stockouts data.
    stockout_frequency = num_stockouts
    avg_duration = 0
    if not df_stockouts.empty: # Use preprocessed df
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
        query["item_id"] = item_id

    stockouts_data = get_data("stockouts", query)

    if not stockouts_data:
        return []

    df_raw = pd.DataFrame(stockouts_data)
    df = preprocess_stockouts_data(df_raw)
    
    # For the heatmap, we can group by item and date (or month, week)
    # Here, we'll group by month for a higher-level view
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    heatmap_data = df.groupby(['Product ID', 'month']).size().reset_index(name='stockout_count')
    
    return heatmap_data.to_dict('records')

def calculate_days_of_supply(item_id: str = None):
    """
    Calculates the days of supply for an item or all items.
    Days of Supply = Current Inventory / Avg Daily Demand
    """
    inventory_data = get_data("inventory")
    sales_data = get_data("sales")

    if not inventory_data or not sales_data:
        return {"error": "Insufficient data."}

    df_inventory_raw = pd.DataFrame(inventory_data)
    df_inventory = preprocess_inventory_data(df_inventory_raw)
    df_sales_raw = pd.DataFrame(sales_data)
    df_sales = preprocess_sales_data(df_sales_raw)

    if 'Inventory Level' not in df_inventory.columns or 'Product ID' not in df_inventory.columns:
        return {"error": "Inventory data missing 'stock_level' or 'Product ID'."}

    if 'quantity' not in df_sales.columns or 'date' not in df_sales.columns or 'Product ID' not in df_sales.columns:
        return {"error": "Sales data missing 'quantity', 'date', or 'Product ID'."}
    
    if item_id:
        df_inventory = df_inventory[df_inventory['Product ID'] == item_id]
        df_sales = df_sales[df_sales['Product ID'] == item_id]

    if df_inventory.empty or df_sales.empty:
        return {"days_of_supply": 0, "message": "No data for the given item ID."}

    # Calculate for all items if no item_id is specified
    results = []
    for item in df_inventory['Product ID'].unique():
        current_inventory = df_inventory[df_inventory['Product ID'] == item]['Inventory Level'].sum()
        
        item_sales = df_sales[df_sales['Product ID'] == item]
        if not item_sales.empty:
            total_days = (item_sales['date'].max() - item_sales['date'].min()).days
            if total_days == 0:
                total_days = 1
            avg_daily_demand = item_sales['quantity'].sum() / total_days
        else:
            avg_daily_demand = 0

        if avg_daily_demand == 0:
            days_of_supply = float('inf')
        else:
            days_of_supply = current_inventory / avg_daily_demand
        
        results.append({"item_id": item, "days_of_supply": days_of_supply})

    if item_id and results:
        return results[0]
    
    return results

def calculate_carrying_cost(item_id: str = None, carrying_cost_rate: float = 0.20):
    """
    Calculates the carrying cost of inventory for an item or all items.
    Carrying Cost = Avg Inventory Value * Carrying Cost Rate
    """
    inventory_data = get_data("inventory")

    if not inventory_data:
        return {"error": "No inventory data found."}

    df_inventory_raw = pd.DataFrame(inventory_data)
    df_inventory = preprocess_inventory_data(df_inventory_raw)

    if 'Inventory Level' not in df_inventory.columns or 'Product ID' not in df_inventory.columns:
        return {"error": "Inventory data missing required 'Inventory Level' or 'Product ID' columns."}

    if item_id:
        df_inventory = df_inventory[df_inventory['Product ID'] == item_id]

    if df_inventory.empty:
        return {"carrying_cost": 0, "message": "No data for the given item ID."}

    results = []
    for item in df_inventory['Product ID'].unique():
        item_inventory = df_inventory[df_inventory['Product ID'] == item]
        inventory_value = 1 * item_inventory['Inventory Level'] # Assuming avg_cost is 1 as it's not available in data
        avg_inventory_value = inventory_value.mean()
        carrying_cost = avg_inventory_value * carrying_cost_rate
        results.append({"item_id": item, "carrying_cost": carrying_cost})

    if item_id and results:
        return results[0]
        
    return results

def detect_slow_obsolete_items(
    slow_turnover_threshold: float = 2.0,
    dos_threshold: int = 180,
    inactivity_days: int = 180
):
    """
    Detects slow-moving and obsolete items based on given thresholds.
    """
    inventory_data = get_data("inventory")
    if not inventory_data:
        return {"error": "No inventory data found."}

    df_inventory = pd.DataFrame(inventory_data)
    all_item_ids = df_inventory['Product ID'].unique()

    slow_movers = []
    obsolete_items = []

    for item_id in all_item_ids:
        # Check for slow-moving items
        turnover_result = calculate_turnover(item_id)
        dos_result = calculate_days_of_supply(item_id)

        if not isinstance(turnover_result, dict) or 'error' in turnover_result:
            continue # Skip if there was an error calculating turnover

        if not isinstance(dos_result, dict) or 'error' in dos_result:
            continue # Skip if there was an error calculating days of supply

        if turnover_result.get('turnover_ratio', float('inf')) < slow_turnover_threshold or \
           dos_result.get('days_of_supply', 0) > dos_threshold:
            slow_movers.append(item_id)

        # Check for obsolete items
        sales_data = get_data("sales", {"item_id": item_id})
        if not sales_data:
            obsolete_items.append(item_id)
            continue

        df_sales = pd.DataFrame(sales_data)
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        last_sale_date = df_sales['date'].max()

        if last_sale_date < datetime.now() - timedelta(days=inactivity_days):
            obsolete_items.append(item_id)

    return {"slow_movers": slow_movers, "obsolete_items": obsolete_items}