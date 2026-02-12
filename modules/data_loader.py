
import pandas as pd
import streamlit as st
import os

def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Loads the dataset from a CSV file with caching to improve performance.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded pandas DataFrame. Returns an empty DataFrame if file not found.
    """
    if not os.path.exists(filepath):
        st.error(f"File not found: {filepath}")
        return pd.DataFrame()

    @st.cache_data
    def _read_csv(path: str) -> pd.DataFrame:
        # Load only necessary columns if dataset is massive, but for 200k rows, 
        # loading all is generally fine. 
        # Optimize types if needed for performance.
        df = pd.read_csv(path, low_memory=False)
        
        # Standardize column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Parse Dates immediately for 'Timeliness' checks later
        if 'Crash Date/Time' in df.columns:
            df['Crash Date/Time'] = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
            
        return df

    return _read_csv(filepath)
