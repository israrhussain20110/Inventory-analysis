from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor # New import
from sklearn.svm import SVR # New import
import pandas as pd
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import get_validated_data
from app.models import ForecastRequest, SalesRecord
from app.services.data_preprocessing import preprocess_for_forecasting

def forecast_inventory(request: ForecastRequest, granularity: str = "monthly"):
    """
    Forecasts inventory for a given store and product using Linear Regression, Random Forest, or SVM.
    """
    query = {
        "Store ID": request.store_id,
        "Product ID": request.product_id
    }
    # Assuming get_data can fetch a comprehensive dataset for forecasting
    raw_data = get_validated_data("sales", SalesRecord, query)

    if not raw_data:
        return {"error": "No data found for the given store and product."}

    df = pd.DataFrame(raw_data)

    # Ensure 'Date' column is in datetime format before resampling
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.set_index('Date')

    # Resample data based on granularity
    if granularity == "daily":
        df = df.resample('D').sum()
    elif granularity == "monthly":
        df = df.resample('M').sum()
    elif granularity == "quarterly":
        df = df.resample('Q').sum()
    elif granularity == "yearly":
        df = df.resample('Y').sum()
    else:
        return {"error": "Invalid granularity specified. Choose from 'daily', 'monthly', 'quarterly', 'yearly'."}

    df = df.reset_index() # Reset index after resampling

    # Ensure 'date' column is in datetime format before preprocessing
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    # Apply the new preprocessing function
    processed_df = preprocess_for_forecasting(df.copy())

    # Prepare data for Linear Regression
    # Assuming 'Sales' is the target variable after preprocessing
    if 'Sales' not in processed_df.columns:
        return {"error": "Processed data does not contain 'Sales' column for forecasting."}

    # Separate features (X) and target (y)
    features = [col for col in processed_df.columns if col not in ['Sales', 'Date']]

    X = processed_df[features]
    y = processed_df['Sales']

    if X.empty:
        return {"error": "No features available for training the model after preprocessing."}

    # Model selection based on request.model_type
    model = None
    if request.model_type == "linear_regression":
        model = LinearRegression()
    elif request.model_type == "random_forest":
        model = RandomForestRegressor(n_estimators=100, random_state=42) # Example parameters
    elif request.model_type == "svm":
        model = SVR(kernel='rbf') # Example parameters
    else:
        return {"error": "Invalid model type specified. Choose from 'linear_regression', 'random_forest', 'svm'."}

    model.fit(X, y)

    # Make predictions
    predictions = model.predict(X)
    processed_df['predicted_sales'] = predictions

    # Prepare output
    output_columns = ['Date', 'Sales', 'predicted_sales']
    if not all(col in processed_df.columns for col in output_columns):
        return {"error": "Required output columns (Date, Sales, predicted_sales) not found after processing."}

    output_df = processed_df[output_columns].copy()
    output_df.rename(columns={'Sales': 'actual_sales', 'predicted_sales': 'yhat'}, inplace=True)

    return output_df.to_dict(orient='records')