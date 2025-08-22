import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_for_forecasting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the DataFrame for forecasting, including categorical encoding, and numerical scaling.
    """
    if df.empty:
        return df

    # 1. Categorical Feature Encoding
    categorical_cols = ['Category', 'Region', 'Weather', 'Seasonality', 'Promotion']
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str)) # Convert to string to handle NaNs if any

    # 2. Numerical Feature Scaling
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    numerical_cols = [col for col in numerical_cols if col not in categorical_cols]

    if numerical_cols:
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

    return df

def preprocess_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses inventory data DataFrame.
    - Fills missing 'Inventory' with 0.
    - Converts 'Inventory' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    """
    if df.empty:
        return df

    # Handle missing values
    if 'Inventory' in df.columns:
        df['Inventory'] = df['Inventory'].fillna(0)

    # Convert to numeric, coercing errors
    if 'Inventory' in df.columns:
        df['Inventory'] = pd.to_numeric(df['Inventory'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'Inventory' in df.columns:
        df = df.dropna(subset=['Inventory'])

    return df

def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses sales data DataFrame.
    - Converts 'Sales' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'Date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    df = df.copy() # Ensure we are working on a copy to avoid SettingWithCopyWarning

    # Convert to numeric, coercing errors
    if 'Sales' in df.columns:
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'Sales' in df.columns:
        df = df.dropna(subset=['Sales'])

    # Ensure date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

    return df

def preprocess_stockouts_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses stockouts data DataFrame.
    - Converts 'duration' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'Date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    df = df.copy() # Ensure we are working on a copy to avoid SettingWithCopyWarning

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