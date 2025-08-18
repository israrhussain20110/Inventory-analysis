from app.database import get_data


data = get_data()
if data:
    print(f"Successfully retrieved {len(data)} records from the database.")
else:
    print("No data found in the database.")
