from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["inventory_db"]
def insert_data(data, collection_name: str):
    """Insert data into a specified MongoDB collection."""
    try:
        collection = db[collection_name]
        collection.insert_many(data, ordered=False)
        print(f"Data inserted successfully into {collection_name}.")
    except Exception as e:
        print(f"Error inserting data into {collection_name}: {e}")

def get_data(collection_name: str, query=None):
    """Retrieve data from a specified MongoDB collection."""
    if query is None:
        query = {}
    collection = db[collection_name]
    return list(collection.find(query))