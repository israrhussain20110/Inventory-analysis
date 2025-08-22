import pandas as pd
from database import get_validated_data
from models import RetailData

def calculate_metrics(store_id: str, product_id: str, db_data: list):
    """
    Calculate inventory metrics (turnover, days of supply, stockouts, carrying cost, slow/obsolete).
    """
    if not db_data:
        return {
            "turnover": 0,
            "days_of_supply": 0,
            "stockout_count": 0,
            "stockout_rate": 0,
            "carrying_cost": 0,
            "is_slow_moving": False,
            "is_obsolete": False,
        }
    df = pd.DataFrame([item.dict() for item in db_data]).copy()
    df = df[(df['StoreId'] == store_id) & (df['ProductID'] == product_id)]
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
        pass # Handle this case or raise an error

    # Calculate metrics
    avg_sales = df['Sales'].mean()
    if pd.isna(avg_sales):
        avg_sales = None

    total_sales = df['Sales'].sum()
    
    avg_inventory = df['Inventory'].mean()
    if pd.isna(avg_inventory):
        avg_inventory = None

    current_inventory = df['Inventory'].iloc[-1] if not df.empty else 0 # Use last known inventory for current

    # 1. Inventory Turnover Rates (Time Series)
    turnover_data = []
    if 'Date' in df.columns and not df.empty:
        for date in df['Date'].unique():
            daily_df = df[df['Date'] == date]
            daily_sales = daily_df['Sales'].sum()
            daily_inventory = daily_df['Inventory'].mean()
            daily_turnover = daily_sales / daily_inventory if daily_inventory > 0 else None
            turnover_data.append({'date': date.isoformat(), 'turnover_ratio': daily_turnover})

    # Overall turnover for slow-moving/obsolete check
    turnover = total_sales / avg_inventory if avg_inventory is not None and avg_inventory > 0 else None

    # 2. Stockout Analysis
    stockout_count = (df['Inventory'] == 0).sum()
    total_records = len(df)
    stockout_rate = stockout_count / total_records if total_records > 0 else None

    # 3. Days of Supply (DoS)
    days_of_supply = current_inventory / avg_sales if avg_sales is not None and avg_sales > 0 else None

    # 4. Carrying Cost Analysis (assuming Inventory represents value or unit cost is 1)
    # Using a typical carrying cost rate of 25% annually
    carrying_cost_rate = 0.25
    carrying_cost = avg_inventory * carrying_cost_rate if avg_inventory is not None else None

    # 5. Slow-Moving & Obsolete Stock Identification
    is_slow_moving = False
    is_obsolete = False

    # Simple thresholds for demonstration
    if turnover is not None and turnover < 1 and total_sales > 0: # Low turnover but some sales
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