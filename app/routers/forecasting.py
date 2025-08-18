from fastapi import APIRouter, Depends, HTTPException
from app.services.forecasting import forecast_inventory
from app.models import ForecastRequest

router = APIRouter()

@router.post("/predict")
async def predict_inventory(request: ForecastRequest):
    forecast = forecast_inventory(request)
    if isinstance(forecast, dict) and "error" in forecast:
        raise HTTPException(status_code=404, detail=forecast["error"])
    return {"store_id": request.store_id, "product_id": request.product_id, "forecast": forecast.to_dict('records')}