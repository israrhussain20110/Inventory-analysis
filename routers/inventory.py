import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from database import insert_data, db, get_validated_data # Added db import
from services import calculations
import pandas as pd
import io
from models import RetailData
import json

router = APIRouter()

# Load API descriptions
try:
    with open("api_descriptions.json", "r") as f:
        API_DESCRIPTIONS = json.load(f)
except FileNotFoundError:
    API_DESCRIPTIONS = {} # Handle case where file is not found
except json.JSONDecodeError:
    API_DESCRIPTIONS = {} # Handle case where JSON is invalid

@router.get("/all")
async def get_all_inventory(skip: int = 0, limit: int = 0):
    """
    Retrieves all inventory records from the database.
    A limit of 0 means no limit.

    Returns:
        List[RetailData]: A list of inventory records, where each record is a RetailData object
                         containing fields like Date, StoreId, ProductID, Category, Region,
                         Inventory, Sales, Orders, Demand, Price, Discount, Weather, Promotion,
                         CompetitorPrice, Seasonality, cost, and abc_class.
    """
    inventory_data = get_validated_data(RetailData, "retail_data", skip=skip, limit=limit)
    return inventory_data

@router.get("/stockouts/all")
async def get_all_stockouts(skip: int = 0, limit: int = 0):
    """
    Retrieves all stockout records from the database.
    A limit of 0 means no limit.

    Returns:
        List[RetailData]: A list of stockout records, where each record is a RetailData object
                         with 'Inventory' equal to 0 and 'Sales' greater than 0.
                         Fields include Date, StoreId, ProductID, Category, Region,
                         Inventory, Sales, Orders, Demand, Price, Discount, Weather, Promotion,
                         CompetitorPrice, Seasonality, cost, and abc_class.
    """
    stockouts_data = get_validated_data(RetailData, "retail_data", query={"Inventory": 0, "Sales": {"$gt": 0}}, skip=skip, limit=limit)
    return stockouts_data

COLUMN_RENAME_MAP = {
    'Inventory Level': 'Inventory',
    'Units Sold': 'Sales',
    'Units Ordered': 'Orders',
    'Demand Forecast': 'Demand',
    'Weather Condition': 'Weather',
    'Holiday/Promotion': 'Promotion',
    'Competitor Pricing': 'Competitor Price',
    'Store ID': 'StoreId',
    'Product ID': 'ProductID'
}

@router.post("/upload/inventory")
async def upload_inventory(file: UploadFile = File(...)):
    """
    Uploads inventory data from a CSV file to the database.
    Note: This endpoint will delete all existing data in the collection before inserting the new data.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Apply column renaming
        df.rename(columns={k: v for k, v in COLUMN_RENAME_MAP.items() if k in df.columns}, inplace=True)

        # Basic validation: check for expected columns after renaming
        expected_columns = ['Date', 'StoreId', 'ProductID', 'Category', 'Region', 'Inventory', 'Sales', 'Price']
        if not all(col in df.columns for col in expected_columns):
            raise HTTPException(status_code=400, detail=f"CSV is missing one or more expected columns after renaming. Required: {expected_columns}")

        data = df.to_dict('records')
        insert_data(data, "retail_data")
        return {"message": f"Successfully uploaded and inserted {len(data)} records from {file.filename} into retail_data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

@router.get("/metrics")
async def get_inventory_metrics(
    product_id: str = Query(None),
    category: str = Query(None),
    abc_class: str = Query(None),
    period: str = Query('monthly'),
    carrying_cost_rate: float = Query(0.2)
):
    """
    Computes and returns a dictionary of inventory metrics for a given product.

    Args:
        product_id (str, optional): The ID of the product.
        category (str, optional): The category of the product.
        abc_class (str, optional): The ABC classification of the product.
        period (str, optional): The period for turnover calculation (e.g., 'monthly').
        carrying_cost_rate (float, optional): The carrying cost rate.

    Returns:
        dict: A dictionary containing the following metrics:
            - 'turnover': Dictionary with 'turnover_ratio' for the specified product.
            - 'stockout_rate': Dictionary with 'stockout_rate', 'stockout_frequency', and 'average_duration'.
            - 'days_of_supply': Dictionary with 'days_of_supply' for the specified product.
            - 'carrying_cost': Dictionary with 'carrying_cost' for the specified product.
            - 'description': A detailed explanation of the output structure and analysis insights.
    """
    turnover = calculations.calculate_turnover(product_id, category, abc_class, period)
    stockout_rate = calculations.calculate_stockout_rate(product_id)
    days_of_supply = calculations.calculate_days_of_supply(product_id)
    carrying_cost = calculations.calculate_carrying_cost(product_id, carrying_cost_rate)

    response_data = {
        "turnover": turnover,
        "stockout_rate": stockout_rate,
        "days_of_supply": days_of_supply,
        "carrying_cost": carrying_cost
    }

    if "inventory_metrics_output" in API_DESCRIPTIONS:
        response_data["description"] = API_DESCRIPTIONS["inventory_metrics_output"]

    return response_data

@router.get("/slow_movers")
async def get_slow_movers(
    slow_turnover_threshold: float = Query(2.0),
    dos_threshold: int = Query(180),
    inactivity_days: int = Query(180)
):
    """
    Returns a list of slow-moving and obsolete items based on defined thresholds.

    Args:
        slow_turnover_threshold (float, optional): Threshold for slow turnover.
        dos_threshold (int, optional): Days of supply threshold.
        inactivity_days (int, optional): Number of days of inactivity to consider an item obsolete.

    Returns:
        dict: A dictionary containing two lists:
            - 'slow_movers': List of ProductIDs identified as slow-moving.
            - 'obsolete_items': List of ProductIDs identified as obsolete.
            - 'description': A detailed explanation of the output structure and analysis insights.
    """
    response_data = calculations.detect_slow_obsolete_items(
        slow_turnover_threshold, dos_threshold, inactivity_days
    )

    if "slow_obsolete_items_output" in API_DESCRIPTIONS:
        response_data["description"] = API_DESCRIPTIONS["slow_obsolete_items_output"]

    return response_data

@router.get("/stockouts")
async def get_stockouts(product_id: str = Query(None)):
    """
    Returns stockout history and rates for a given product.

    Args:
        product_id (str, optional): The ID of the product.

    Returns:
        dict: A dictionary containing:
            - 'stockout_rate': The calculated stockout rate.
            - 'stockout_frequency': The number of stockout events.
            - 'average_duration': The average duration of stockouts.
    """
    return calculations.calculate_stockout_rate(product_id)

@router.get("/stockouts/heatmap")
async def get_stockouts_heatmap(product_id: str = Query(None)):
    """
    Returns data suitable for generating a stockout heatmap.

    Args:
        product_id (str, optional): The ID of the product.

    Returns:
        List[dict]: A list of dictionaries, where each dictionary represents a stockout event
                    and contains:
                    - 'ProductID': The unique identifier for the product.
                    - 'month': The month of the stockout (e.g., 'YYYY-MM').
                    - 'stockout_count': The number of stockouts for that product in that month.
    """
    return calculations.calculate_stockout_heatmap_data(product_id)

@router.get("/slow_movers/report")
async def get_slow_movers_report():
    """
    Generates a CSV report of slow-moving and obsolete items.

    The output CSV will contain the following columns:
    - 'ProductID': The unique identifier for the product.
    - 'status': The status of the item, either 'slow-moving' or 'obsolete'.

    For a detailed JSON description of the slow-moving and obsolete items analysis,
    refer to the /inventory/slow_movers endpoint.
    """
    data = calculations.detect_slow_obsolete_items()
    if "error" in data:
        # If there's an error indicating no data, return an empty CSV
        if data["error"] == "No inventory data found.":
            df = pd.DataFrame(columns=['Product ID', 'status'])
            stream = io.StringIO()
            df.to_csv(stream, index=False)
            response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=slow_movers_report.csv"
            return response
        else:
            # For other errors, raise HTTPException
            raise HTTPException(status_code=500, detail=data["error"])

    slow_movers_df = pd.DataFrame(data['slow_movers'], columns=['ProductID'])
    slow_movers_df['status'] = 'slow-moving'

    obsolete_items_df = pd.DataFrame(data['obsolete_items'], columns=['ProductID'])
    obsolete_items_df['status'] = 'obsolete'

    df = pd.concat([slow_movers_df, obsolete_items_df])

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=slow_movers_report.csv"
    return response
