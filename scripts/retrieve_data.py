import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db # Import the db object directly

def retrieve_and_display_data():
    print("\n--- Retrieving ALL Retail Data ---")
    retail_collection = db["retail_data"]
    retail_data = list(retail_collection.find({}))
    if retail_data:
        print(f"Total retail_data documents: {len(retail_data)}")
        for i, item in enumerate(retail_data):
            if i < 10:
                print(item)
            else:
                break
    else:
        print("No retail_data found.")

if __name__ == "__main__":
    retrieve_and_display_data()
