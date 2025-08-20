import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, HTTPException
from app.services.forecasting import forecast_inventory
from app.models import ForecastRequest
import pandas as pd

router = APIRouter()

@router.post("/predict")
async def predict_inventory(request: ForecastRequest):
    """
    This endpoint now returns a structured JSON response containing the forecast,
    and it gracefully handles cases where the forecast might not be a DataFrame.
    """
    forecast_result = forecast_inventory(request)
    
    if isinstance(forecast_result, dict) and "error" in forecast_result:
        raise HTTPException(status_code=404, detail=forecast_result["error"])
    
    # If the forecast is a DataFrame, convert it to a dictionary
    if isinstance(forecast_result, pd.DataFrame):
        forecast_data = forecast_result.to_dict('records')
    else:
        # Handle cases where the forecast is not a DataFrame (e.g., an error message)
        forecast_data = forecast_result

    return {
        "store_id": request.store_id,
        "product_id": request.product_id,
        "forecast": forecast_data
    }
