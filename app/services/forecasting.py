
from prophet import Prophet
import pandas as pd
from app.database import get_data
from app.models import ForecastRequest

def forecast_inventory(request: ForecastRequest):
    """
    Forecasts inventory for a given store and product.
    """
    query = {
        "store_id": request.store_id,
        "product_id": request.product_id
    }
    sales_data = get_data("sales", query)

    if not sales_data:
        return {"error": "No sales data found for the given store and product."}

    df = pd.DataFrame(sales_data)
    df = df[['date', 'quantity']].rename(columns={'date': 'ds', 'quantity': 'y'})

    # Basic preprocessing
    df['ds'] = pd.to_datetime(df['ds'])

    # Initialize and fit the model
    model = Prophet()
    model.fit(df)

    # Make future predictions
    future = model.make_future_dataframe(periods=request.days)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
