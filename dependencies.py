import os
import sys
from fastapi import Depends
from database import get_data

def get_db_data():
    return get_data("sales") # Assuming 'sales' is the default collection for status checks