import pandas as pd

def preprocess_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses inventory data DataFrame.
    - Fills missing 'stock_level' with 0.
    - Fills missing 'avg_cost' with its mean.
    - Converts 'stock_level' and 'avg_cost' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    # Handle missing values
    if 'Inventory Level' in df.columns:
        df['Inventory Level'].fillna(0, inplace=True)

    # Convert to numeric, coercing errors
    if 'Inventory Level' in df.columns:
        df['Inventory Level'] = pd.to_numeric(df['Inventory Level'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    if 'Inventory Level' in df.columns:
        df.dropna(subset=['Inventory Level'], inplace=True)

    # Ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True) # Drop rows with invalid dates

    return df

def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses sales data DataFrame.
    - Converts 'COGS' and 'quantity' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    # Convert to numeric, coercing errors
    for col in ['COGS', 'quantity']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where critical numeric conversions failed
    df.dropna(subset=['COGS', 'quantity'], inplace=True)

    # Ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)

    return df

def preprocess_stockouts_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses stockouts data DataFrame.
    - Converts 'duration' to numeric, coercing errors.
    - Drops rows where critical numeric conversions failed.
    - Converts 'date' to datetime, dropping rows with invalid dates.
    """
    if df.empty:
        return df

    # Convert to numeric, coercing errors
    if 'duration' in df.columns:
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

    # Drop rows where critical numeric conversions failed
    df.dropna(subset=['duration'], inplace=True)

    # Ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)

    return df
