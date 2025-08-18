import pandas as pd
from app.database import insert_data

# Load CSV and insert into MongoDB
df = pd.read_csv('data/retail_store_inventory.csv')
data = df.to_dict('records')
insert_data(data, "sales")

print("Data loaded into MongoDB successfully!")