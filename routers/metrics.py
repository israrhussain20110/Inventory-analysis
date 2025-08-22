from fastapi import APIRouter
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.metrics import calculate_metrics
from models import MetricRequest, RetailData
from database import get_validated_data

router = APIRouter()

@router.post("/all-metrics")
async def get_all_metrics(request: MetricRequest):
    query = {"StoreId": request.store_id, "ProductID": request.product_id}
    retail_data = get_validated_data(RetailData, "retail_data", query) # Fetch data directly

    metrics = calculate_metrics(request.store_id, request.product_id, retail_data)
    return {
        "store_id": request.store_id,
        "product_id": request.product_id,
        **metrics
    }