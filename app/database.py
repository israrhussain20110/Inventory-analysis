from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Type
from pydantic import ValidationError
from app.models import InventoryItem, SalesRecord

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

def get_validated_data(collection_name: str, model: Type, query: dict = None) -> List:
    """
    Retrieves and validates data from a specified MongoDB collection
    using a Pydantic model.
    """
    if query is None:
        query = {}
    
    collection = db[collection_name]
    data = list(collection.find(query))
    
    validated_data = []
    for item in data:
        try:
            validated_data.append(model.parse_obj(item))
        except ValidationError as e:
            print(f"Skipping document due to validation error: {e}")
            continue
            
    return validated_data

def get_data(collection_name: str, query=None):
    """Retrieve data from a specified MongoDB collection."""
    if query is None:
        query = {}
    collection = db[collection_name]
    return list(collection.find(query))