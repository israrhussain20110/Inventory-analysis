from sklearn.linear_model import LinearRegression
import pandas as pd
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import get_validated_data
from app.models import ForecastRequest, SalesRecord
from app.services.data_preprocessing import preprocess_for_forecasting

def forecast_inventory(request: ForecastRequest):
    """
    Forecasts inventory for a given store and product using Linear Regression.
    """
    query = {
        "Store ID": request.store_id,
        "Product ID": request.product_id
    }
    # Assuming get_data can fetch a comprehensive dataset for forecasting
    raw_data = get_validated_data("sales", SalesRecord, query)

    if not raw_data:
        return {"error": "No data found for the given store and product."}

    df = pd.DataFrame([record.dict() for record in raw_data])

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
    # Exclude 'date' if it's still present and not intended as a feature
    # Also exclude 'Inventory' if 'Sales' is the target, as 'Inventory' might be another target or related.
    # For now, let's assume all numerical columns except 'Sales' are features.
    # We need to be careful about the 'date' column. If it's a datetime object, it won't be included in select_dtypes(include=['number']).
    # If it's converted to a numerical representation (e.g., timestamp), it might be included.
    # For now, explicitly exclude 'date' from features.
    features = [col for col in processed_df.columns if col not in ['Sales', 'Date']]

    X = processed_df[features]
    y = processed_df['Sales']

    if X.empty:
        return {"error": "No features available for training the model after preprocessing."}

    # Initialize and fit the Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Make predictions
    # For future predictions, we would need to generate future 'X' values.
    # For now, we'll predict on the training data to demonstrate functionality.
    predictions = model.predict(X)
    processed_df['predicted_sales'] = predictions

    # Prepare output
    # We need to ensure 'date' is available for the output.
    # If 'date' was dropped during preprocessing, this will fail.
    # I've added a step to ensure 'date' is datetime before preprocessing,
    # so it should be preserved unless explicitly dropped by preprocess_for_forecasting.
    output_columns = ['Date', 'Sales', 'predicted_sales']
    if not all(col in processed_df.columns for col in output_columns):
        return {"error": "Required output columns (Date, Sales, predicted_sales) not found after processing."}

    output_df = processed_df[output_columns].copy()
    output_df.rename(columns={'Sales': 'actual_sales', 'predicted_sales': 'yhat'}, inplace=True)

    return output_df.to_dict(orient='records')