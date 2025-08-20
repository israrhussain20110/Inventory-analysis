import sys
import os
import pandas as pd

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import insert_data

# Load CSV and insert into MongoDB
df = pd.read_csv('data/inventory.csv')
data = df.to_dict('records')
insert_data(data, "inventory")

print("Inventory data loaded into MongoDB successfully!")