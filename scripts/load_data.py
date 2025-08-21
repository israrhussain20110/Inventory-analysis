import sys
import os
import pandas as pd

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import insert_data

# Load retail_store_inventory.csv data and insert into MongoDB
try:
    df_retail = pd.read_csv('data/retail_store_inventory.csv')
    # Explicitly convert 'Date' column to datetime objects
    df_retail['Date'] = pd.to_datetime(df_retail['Date'], errors='coerce')

    # Insert into 'inventory' collection
    inventory_data = df_retail.to_dict('records')
    insert_data(inventory_data, "inventory")
    print("Retail inventory data loaded into 'inventory' collection successfully!")

    # Insert into 'sales' collection (assuming it contains sales-related data)
    sales_data = df_retail.to_dict('records')
    insert_data(sales_data, "sales")
    print("Retail sales data loaded into 'sales' collection successfully!")

except Exception as e:
    print(f"Error loading retail_store_inventory.csv data: {e}")
