import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_data


data = get_data("sales")
if data:
    print(f"Successfully retrieved {len(data)} records from the database.")
else:
    print("No data found in the database.")