from fastapi import APIRouter
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.metrics import calculate_metrics
from app.models import MetricRequest
from app.database import get_data

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