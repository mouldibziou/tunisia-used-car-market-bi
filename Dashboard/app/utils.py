"""
Utility functions for the Tunisia Car Dashboard
"""

import pandas as pd
import numpy as np
from typing import List, Dict

def detect_outliers(df: pd.DataFrame, column: str, method='iqr', threshold=1.5):
    """
    Detect outliers using IQR or Z-score method.
    
    Parameters:
    - df: DataFrame
    - column: Column name to check for outliers
    - method: 'iqr' or 'zscore'
    - threshold: Multiplier for IQR or Z-score threshold
    
    Returns:
    - Boolean mask of outliers
    """
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (df[column] < lower_bound) | (df[column] > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        return z_scores > threshold
    
    return pd.Series([False] * len(df))

def calculate_yoy_growth(df: pd.DataFrame, value_col: str, year_col: str = 'year'):
    """
    Calculate year-over-year growth rates.
    
    Returns DataFrame with additional 'yoy_growth' column.
    """
    df_sorted = df.sort_values(year_col)
    df_sorted['yoy_growth'] = df_sorted[value_col].pct_change() * 100
    return df_sorted

def format_currency(value: float, currency: str = 'DT'):
    """Format number as currency string."""
    return f"{value:,.0f} {currency}"

def get_price_segments(price: float):
    """Categorize cars into price segments."""
    if price < 10000:
        return 'Budget'
    elif price < 25000:
        return 'Mid-Range'
    elif price < 50000:
        return 'Premium'
    else:
        return 'Luxury'

def calculate_depreciation_rate(initial_price: float, current_price: float, years: int):
    """Calculate annual depreciation rate."""
    if years == 0 or initial_price == 0:
        return 0
    return ((initial_price - current_price) / initial_price / years) * 100

def export_to_csv(df: pd.DataFrame, filename: str):
    """Export DataFrame to CSV with timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"data/processed/{filename}_{timestamp}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Data exported to {output_path}")
    return output_path