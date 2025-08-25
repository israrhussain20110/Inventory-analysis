import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
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

def calculate_abc_class(df):
    df['sales_value'] = df['Sales'] * df['Price']
    total_sales_value = df['sales_value'].sum()
    df = df.sort_values(by='sales_value', ascending=False)
    df['cumulative_sales'] = df['sales_value'].cumsum()
    df['cumulative_percentage'] = (df['cumulative_sales'] / total_sales_value) * 100

    def assign_abc_class(percentage):
        if percentage <= 80:
            return 'A'
        elif percentage <= 95:
            return 'B'
        else:
            return 'C'

    df['ABC Class'] = df['cumulative_percentage'].apply(assign_abc_class)
    return df

def convert_nan_to_none(df: pd.DataFrame, model: BaseModel) -> pd.DataFrame:
    for field_name, field in model.model_fields.items():
        if not field.is_required() and field_name in df.columns: # Check if it's an Optional field
            # Handle pandas.NA and numpy.nan for numeric and object types
            if pd.api.types.is_numeric_dtype(df[field_name]):
                df[field_name] = df[field_name].replace({pd.NA: None, float('nan'): None})
            elif pd.api.types.is_object_dtype(df[field_name]): # For string/object columns
                df[field_name] = df[field_name].replace({pd.NA: None, '': None, float('nan'): None})
            else: # Catch-all for other types, e.g., datetime if it somehow gets NaN
                df[field_name] = df[field_name].where(pd.notna(df[field_name]), None)
    return df

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_csv_to_db.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_file_path)

        # Convert data types
        df['Date'] = pd.to_datetime(df['Date'])

        # Apply column renaming
        df.rename(columns={k: v for k, v in COLUMN_RENAME_MAP.items() if k in df.columns}, inplace=True)

        # Add 'cost' and calculate abc_class
        df['cost'] = df['Price'] * 0.8 # Assuming cost is 80% of price
        df = calculate_abc_class(df)
        df.rename(columns={"ABC Class": "abc_class"}, inplace=True)

        # Convert NaN values to None for optional fields before insertion
        df = convert_nan_to_none(df, RetailData)

        # Insert data into a single collection
        print("Clearing existing data in 'retail_data' collection...")
        insert_data(df.to_dict('records'), "retail_data")

        print(f"Data from {csv_file_path} loaded into 'retail_data' collection successfully!")

    except Exception as e:
        print(f"Error loading data from {csv_file_path}: {e}")
