import pandas as pd

def calculate_metrics(store_id: int, product_id: int, db_data: list):
    """Calculate inventory metrics (turnover, days of supply, stockouts, carrying cost, slow/obsolete)."""
    df = pd.DataFrame(db_data)
    df = df[(df['Store ID'] == store_id) & (df['Product ID'] == product_id)]
    if df.empty:
        return {
            "turnover": 0,
            "days_of_supply": 0,
            "stockout_count": 0,
            "stockout_rate": 0,
            "carrying_cost": 0,
            "is_slow_moving": False,
            "is_obsolete": False
        }

    # Ensure 'Date' column is datetime and sort
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')
    else:
        # If no Date column, some metrics will be less accurate
        pass # Handle this case or raise an error

    # Calculate metrics
    avg_sales = df['Units Sold'].mean()
    total_sales = df['Units Sold'].sum()
    avg_inventory = df['Inventory Level'].mean()
    current_inventory = df['Inventory Level'].iloc[-1] if not df.empty else 0 # Use last known inventory for current

    # 1. Inventory Turnover Rates (Time Series)
    turnover_data = []
    if 'Date' in df.columns and not df.empty:
        for date in df['Date'].unique():
            daily_df = df[df['Date'] == date]
            daily_sales = daily_df['Units Sold'].sum()
            daily_inventory = daily_df['Inventory Level'].mean()
            daily_turnover = daily_sales / daily_inventory if daily_inventory > 0 else 0
            turnover_data.append({'date': date.isoformat(), 'turnover_ratio': daily_turnover})

    # Overall turnover for slow-moving/obsolete check
    turnover = total_sales / avg_inventory if avg_inventory > 0 else 0

    # 2. Stockout Analysis
    stockout_count = (df['Inventory Level'] == 0).sum()
    total_records = len(df)
    stockout_rate = stockout_count / total_records if total_records > 0 else 0

    # 3. Days of Supply (DoS)
    days_of_supply = current_inventory / avg_sales if avg_sales > 0 else 0

    # 4. Carrying Cost Analysis (assuming Inventory represents value or unit cost is 1)
    # Using a typical carrying cost rate of 25% annually
    carrying_cost_rate = 0.25
    carrying_cost = avg_inventory * carrying_cost_rate # This assumes avg_inventory is average inventory value

    # 5. Slow-Moving & Obsolete Stock Identification
    is_slow_moving = False
    is_obsolete = False

    # Simple thresholds for demonstration
    if turnover < 1 and total_sales > 0: # Low turnover but some sales
        is_slow_moving = True
    elif total_sales == 0 and total_records > 0: # No sales over the period
        is_obsolete = True

    return {
        "turnover": turnover_data,
        "days_of_supply": days_of_supply,
        "stockout_count": stockout_count,
        "stockout_rate": stockout_rate,
        "carrying_cost": carrying_cost,
        "is_slow_moving": is_slow_moving,
        "is_obsolete": is_obsolete
    }

def check_data_status(db_data: list):
    """Check if data is loaded and return record count."""
    return {"is_loaded": len(db_data) > 0, "record_count": len(db_data)}