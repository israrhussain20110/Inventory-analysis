from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys
from typing import List, Type, Any
from models import RetailData

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# It is recommended to manage the client's lifecycle with the application's lifespan.
# For FastAPI, you can use a dependency injection system to manage the database connection.
client = MongoClient(MONGO_URI)
db = client["inventory_db"]


def create_indexes():
    """
    Create indexes for the collections.
    """
    db.retail_data.create_index([("ProductID", 1)])
    db.retail_data.create_index([("Category", 1)])
    db.retail_data.create_index([("abc_class", 1)])
    db.retail_data.create_index([("Store ID", 1)])
    db.retail_data.create_index([("Date", 1)])
    print("Indexes created successfully.")


def insert_data(data, collection_name: str):
    """Insert data into a specified MongoDB collection."""
    try:
        collection = db[collection_name]
        # Clear existing data in the collection
        collection.delete_many({})
        collection.insert_many(data, ordered=False)
        print(f"Data inserted successfully into {collection_name}.")
    except Exception as e:
        # It is better to catch more specific exceptions.
        print(f"Error inserting data into {collection_name}: {e}")


def get_validated_data(model: Type, collection_name: str = "retail_data", query: dict = None, skip: int = 0, limit: int = 0) -> List:
    """
    Retrieves data from a specified MongoDB collection and validates it against a Pydantic model.
    A limit of 0 means no limit.
    """
    if query is None:
        query = {}
    
    collection = db[collection_name]
    cursor = collection.find(query).skip(skip)
    if limit > 0:
        cursor = cursor.limit(limit)
    raw_data = list(cursor)
    
    validated_data = []
    for item in raw_data:
        if '_id' in item:
            del item['_id']
        try:
            validated_data.append(model(**item))
        except Exception as e:
            print(f"Error validating data against model {model.__name__}: {e} for item: {item}")
            # Optionally, handle invalid data, e.g., skip or log
            continue
            
    return validated_data


def get_data(collection_name: str = "retail_data", query=None, skip: int = 0, limit: int = 100):
    """
    Retrieve data from a specified MongoDB collection.
    This function is kept for compatibility but get_validated_data is preferred.
    It is recommended to deprecate and remove this function.
    """
    if query is None:
        query = {}
    collection = db[collection_name]
    return list(collection.find(query).skip(skip).limit(limit))