import sys
import os
import pandas as pd

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import insert_data
from models import RetailData
from pydantic import BaseModel

COLUMN_RENAME_MAP = {
    'Inventory Level': 'Inventory',
    'Units Sold': 'Sales',
    'Units Ordered': 'Orders',
    'Demand Forecast': 'Demand',
    'Weather Condition': 'Weather',
    'Holiday/Promotion': 'Promotion',
    'Competitor Pricing': 'Competitor Price',
    'Store ID': 'StoreId',
    'Product ID': 'ProductID'
}

def convert_nan_to_none(df: pd.DataFrame, model: BaseModel) -> pd.DataFrame:
    for field_name, field in model.__fields__.items():
        if field.required is False and field_name in df.columns: # Check if it's an Optional field
            # Handle pandas.NA and numpy.nan for numeric and object types
            if pd.api.types.is_numeric_dtype(df[field_name]):
                df[field_name] = df[field_name].replace({pd.NA: None, float('nan'): None})
            elif pd.api.types.is_object_dtype(df[field_name]): # For string/object columns
                df[field_name] = df[field_name].replace({pd.NA: None, '': None, float('nan'): None})
            else: # Catch-all for other types, e.g., datetime if it somehow gets NaN
                df[field_name] = df[field_name].where(pd.notna(df[field_name]), None)
    return df

# Load retail_store_inventory.csv data and insert into MongoDB
try:
    df_retail = pd.read_csv('data/retail_store_inventory.csv')
    # Explicitly convert 'Date' column to datetime objects
    df_retail['Date'] = pd.to_datetime(df_retail['Date'], errors='coerce')

    # Apply column renaming
    df_retail.rename(columns={k: v for k, v in COLUMN_RENAME_MAP.items() if k in df_retail.columns}, inplace=True)

    # Convert NaN values to None for optional fields before insertion
    df_retail = convert_nan_to_none(df_retail, RetailData)

    # Insert into 'retail_data' collection
    print("Clearing existing data in 'retail_data' collection...")
    insert_data(df_retail.to_dict('records'), "retail_data")
    print("Retail inventory data loaded into 'retail_data' collection successfully!")

except Exception as e:
    print(f"Error loading retail_store_inventory.csv data: {e}")