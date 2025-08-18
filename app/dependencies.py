from fastapi import Depends
from app.database import get_data

def get_db_data():
    return get_data("sales") # Assuming 'sales' is the default collection for status checks