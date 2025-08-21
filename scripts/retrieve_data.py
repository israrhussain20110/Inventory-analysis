import sys
import os

from database import db # Import the db object directly

def retrieve_and_display_data():
    print("\n--- Retrieving Inventory Data ---")
    inventory_collection = db["inventory"]
    inventory_data = list(inventory_collection.find({}).limit(5)) # Retrieve first 5 documents for demonstration
    if inventory_data:
        for item in inventory_data:
            print(item)
    else:
        print("No inventory data found.")

    print("\n--- Retrieving Stockouts Data ---")
    stockouts_collection = db["stockouts"]
    stockouts_data = list(stockouts_collection.find({}).limit(5)) # Retrieve first 5 documents for demonstration
    if stockouts_data:
        for item in stockouts_data:
            print(item)
    else:
        print("No stockouts data found.")

if __name__ == "__main__":
    retrieve_and_display_data()