import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_for_forecasting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the DataFrame for forecasting, including column renaming,
    categorical encoding, and numerical scaling.
    """
    if df.empty:
        return df

    # 1. Standardizing Column Names
    column_rename_map = {
        'InventoryLevel': 'Inventory',
        'UnitsSold': 'Sales',
        'Units Ordered': 'Orders',
        'DemandForecast': 'Demand',
        'WeatherCondition': 'Weather',
        'HolidayPromotion': 'Promotion',
        'CompetitorPricing': 'Competitor Price'
    }
    df.rename(columns=column_rename_map, inplace=True)

    # 2. Categorical Feature Encoding
    categorical_cols = ['Category', 'Region', 'Weather', 'Seasonality', 'Promotion']
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str)) # Convert to string to handle NaNs if any

    # 3. Numerical Feature Scaling
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    numerical_cols = [col for col in numerical_cols if col not in categorical_cols]

    if numerical_cols:
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

    return df

def preprocess_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses inventory data DataFrame.
    - Renames columns to match application's internal naming conventions.
    - Fills missing 'InventoryLevel' with 0.
    - Converts 'InventoryLevel' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    """
    if df.empty:
        return df

    # Rename columns to match Pydantic model field names
    column_rename_map = {
        'Product ID': 'ProductID',
        'Inventory Level': 'InventoryLevel',
        'Units Sold': 'UnitsSold',
        'Units Ordered': 'UnitsOrdered',
        'Demand Forecast': 'DemandForecast',
        'Weather Condition': 'WeatherCondition',
        'Holiday/Promotion': 'HolidayPromotion',
        'Competitor Pricing': 'CompetitorPricing',
        'Store ID': 'StoreId'
    }
    df.rename(columns={k: v for k, v in column_rename_map.items() if k in df.columns}, inplace=True)

    # Handle missing values
    if 'InventoryLevel' in df.columns:
        df['InventoryLevel'] = df['InventoryLevel'].fillna(0)

    # Convert to numeric, coercing errors
    if 'InventoryLevel' in df.columns:
        df['InventoryLevel'] = pd.to_numeric(df['InventoryLevel'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'InventoryLevel' in df.columns:
        df = df.dropna(subset=['InventoryLevel'])

    return df

def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses sales data DataFrame.
    - Renames columns to match application's internal naming conventions.
    - Converts 'UnitsSold' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'Date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    # Rename columns to match Pydantic model field names
    column_rename_map = {
        'Product ID': 'ProductID',
        'Units Sold': 'UnitsSold',
        'Store ID': 'StoreId'
    }
    df.rename(columns={k: v for k, v in column_rename_map.items() if k in df.columns}, inplace=True)

    # Convert to numeric, coercing errors
    if 'UnitsSold' in df.columns:
        df['UnitsSold'] = pd.to_numeric(df['UnitsSold'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'UnitsSold' in df.columns:
        df = df.dropna(subset=['UnitsSold'])

    # Ensure date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    return df

def preprocess_stockouts_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses stockouts data DataFrame.
    - Renames columns to match application's internal naming conventions.
    - Converts 'duration' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'Date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    # Rename columns to match Pydantic model field names (from SalesRecord)
    column_rename_map = {
        'Product ID': 'ProductID',
        'Units Sold': 'UnitsSold',
        'Store ID': 'StoreId'
    }
    df.rename(columns={k: v for k, v in column_rename_map.items() if k in df.columns}, inplace=True)

    # Convert to numeric, coercing errors
    if 'duration' in df.columns:
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'duration' in df.columns:
        df = df.dropna(subset=['duration'])

    # Ensure date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    return df