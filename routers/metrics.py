from fastapi import APIRouter
import os
import sys
from services.metrics import calculate_metrics
from models import MetricRequest
from database import get_data

router = APIRouter()

@router.post("/all-metrics")
async def get_all_metrics(request: MetricRequest):
    query = {"Store ID": request.store_id, "Product ID": request.product_id}
    db_data = get_data("sales", query) # Fetch data directly

    metrics = calculate_metrics(request.store_id, request.product_id, db_data)
    return {
        "store_id": request.store_id,
        "product_id": request.product_id,
        **metrics
    }