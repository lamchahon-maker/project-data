
import pandas as pd
import datetime

class HistoryLogger:
    """
    Logs data processing steps for traceability.
    """
    def __init__(self):
        self.log = []
        
    def add_entry(self, action: str, details: str, row_count: int):
        self.log.append({
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": action,
            "Details": details,
            "Rows Remaining": row_count
        })
        
    def get_log(self) -> pd.DataFrame:
        return pd.DataFrame(self.log)

def clean_dataset(df: pd.DataFrame, logger: HistoryLogger) -> pd.DataFrame:
    """
    Applies cleaning steps to the dataset and logs them.
    
    Args:
        df (pd.DataFrame): Raw dataframe
        logger (HistoryLogger): Logger instance
        
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    df_clean = df.copy()
    initial_rows = len(df_clean)
    logger.add_entry("Load", "Initial Data Load", initial_rows)
    
    # Example Cleaning Step 1: Drop duplicates
    df_clean = df_clean.drop_duplicates()
    logger.add_entry("Clean", "Drop Duplicates", len(df_clean))
    
    # Example Cleaning Step 2: Fill Missing Values for critical columns
    # Specific logic can be expanded based on exact needs, 
    # for now we'll fill generic 'Unknown' for categorical
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    df_clean[categorical_cols] = df_clean[categorical_cols].fillna('Unknown')
    logger.add_entry("Clean", "Fill Missing Categorical with 'Unknown'", len(df_clean))
    
    # Example Cleaning Step 3: Filter invalid years if any
    current_year = pd.Timestamp.now().year
    df_clean = df_clean[
        (df_clean['Vehicle Year'] >= 1900) & 
        (df_clean['Vehicle Year'] <= current_year + 1)
    ]
    logger.add_entry("Filter", "Remove Invalid Vehicle Years (<1900 or >Current)", len(df_clean))
    
    return df_clean
