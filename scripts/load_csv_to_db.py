import sys
import os
import pandas as pd
from database import insert_data # Assuming database.py is now in the root

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python load_csv_to_db.py <csv_file_path> <collection_name>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    collection_name = sys.argv[2]

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_file_path)
        data = df.to_dict('records')
        if data:
            insert_data(data, collection_name)
            print(f"Data from {csv_file_path} loaded into '{collection_name}' collection successfully!")
        else:
            print(f"No data to load from {csv_file_path}.")
    except Exception as e:
        print(f"Error loading data from {csv_file_path} into {collection_name}: {e}")
