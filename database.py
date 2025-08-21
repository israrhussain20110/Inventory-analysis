from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
from typing import List, Type, Any
from models import InventoryItem, SalesRecord

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["inventory_db"]

def insert_data(data, collection_name: str):
    """Insert data into a specified MongoDB collection."""
    try:
        collection = db[collection_name]
        # Clear existing data in the collection
        collection.delete_many({})
        collection.insert_many(data, ordered=False)
        print(f"Data inserted successfully into {collection_name}.")
    except Exception as e:
        print(f"Error inserting data into {collection_name}: {e}")

def get_validated_data(collection_name: str, model: Type, query: dict = None) -> List:
    """
    Retrieves data from a specified MongoDB collection without Pydantic validation.
    """
    if query is None:
        query = {}
    
    collection = db[collection_name]
    data = list(collection.find(query))
    
    # Remove _id field from each item if present
    for item in data:
        if '_id' in item:
            del item['_id']
            
    return data

def get_data(collection_name: str, query=None):
    """
    Retrieve data from a specified MongoDB collection.
    This function is kept for compatibility but get_validated_data is preferred.
    """
    if query is None:
        query = {}
    collection = db[collection_name]
    return list(collection.find(query))