import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Depends
from app.database import get_data

def get_db_data():
    return get_data("sales") # Assuming 'sales' is the default collection for status checks