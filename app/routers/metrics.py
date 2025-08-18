from fastapi import APIRouter
from app.services.metrics import calculate_metrics
from app.models import MetricRequest
from app.database import get_data

router = APIRouter()

@router.post("/all-metrics")
async def get_all_metrics(request: MetricRequest):
    query = {"Store_ID": request.store_id, "Product_ID": request.product_id}
    db_data = get_data("sales", query) # Fetch data directly

    metrics = calculate_metrics(request.store_id, request.product_id, db_data)
    return {
        "store_id": request.store_id,
        "product_id": request.product_id,
        **metrics
    }