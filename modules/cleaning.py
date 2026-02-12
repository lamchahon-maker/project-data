
import pandas as pd
import numpy as np

def impute_column(df: pd.DataFrame, column: str, strategy: str) -> tuple[pd.DataFrame, str]:
    """
    Imputes missing values in a column based on the selected strategy.
    
    Args:
        df (pd.DataFrame): The dataframe to clean.
        column (str): The column to impute.
        strategy (str): One of 'Mean', 'Median', 'Mode', 'Drop Rows'.
        
    Returns:
        tuple[pd.DataFrame, str]: The cleaned dataframe and a log message.
    """
    df_clean = df.copy()
    initial_missing = df_clean[column].isnull().sum()
    
    if initial_missing == 0:
        return df_clean, f"No missing values in '{column}' to impute."

    log_msg = ""
    
    if strategy == 'Drop Rows':
        df_clean = df_clean.dropna(subset=[column])
        log_msg = f"Dropped {initial_missing} rows with missing '{column}'"
        
    elif strategy == 'Mean' and pd.api.types.is_numeric_dtype(df_clean[column]):
        mean_val = df_clean[column].mean()
        df_clean[column] = df_clean[column].fillna(mean_val)
        log_msg = f"Filled missing '{column}' with Mean: {mean_val:.2f}"
        
    elif strategy == 'Median' and pd.api.types.is_numeric_dtype(df_clean[column]):
        median_val = df_clean[column].median()
        df_clean[column] = df_clean[column].fillna(median_val)
        log_msg = f"Filled missing '{column}' with Median: {median_val:.2f}"
        
    elif strategy == 'Mode':
        mode_val = df_clean[column].mode()[0]
        df_clean[column] = df_clean[column].fillna(mode_val)
        log_msg = f"Filled missing '{column}' with Mode: {mode_val}"
        
    else:
        return df, f"Strategy '{strategy}' not applicable for column '{column}'"
        
    return df_clean, log_msg

def fix_date_format(df: pd.DataFrame, column: str) -> tuple[pd.DataFrame, str]:
    """
    Converts a column to datetime objects.
    
    Args:
        df (pd.DataFrame): The dataframe.
        column (str): The column to fix.
        
    Returns:
        tuple[pd.DataFrame, str]: The cleaned dataframe and a log message.
    """
    df_clean = df.copy()
    
    # Try converting to datetime
    # errors='coerce' will turn unparseable formats to NaT
    df_clean[column] = pd.to_datetime(df_clean[column], errors='coerce')
    
    # Count how many successful
    valid_count = df_clean[column].notnull().sum()
    total_count = len(df_clean)
    
    log_msg = f"Fixed format for '{column}'. {valid_count}/{total_count} valid dates."
    
    return df_clean, log_msg
