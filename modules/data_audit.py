
import pandas as pd
import numpy as np
import datetime

def run_audit(df: pd.DataFrame):
    """
    Performs a comprehensive data quality audit and returns a dictionary with:
    - score: Overall Data Health Score (0-100)
    - summary: Textual summary of issues
    - details_table: DataFrame for the detailed table display
    - timeliness_info: Info about date ranges
    """
    
    # 1. Setup & Definitions
    score = 100
    summary_logs = []
    
    # Key fields (Critical for analysis)
    key_fields = ['Report Number', 'Crash Date/Time', 'Latitude', 'Longitude']
    primary_key = 'Report Number'
    
    # Results container
    col_stats = []
    
    total_rows = len(df)
    if total_rows == 0:
        return {
            "score": 0,
            "summary": ["Dataset is empty."],
            "details_table": pd.DataFrame(),
            "timeliness_info": "No data"
        }

    # --- 2. Check Consistency (Duplicates) ---
    if primary_key in df.columns:
        duplicate_count = df.duplicated(subset=[primary_key]).sum()
        duplicate_rate = (duplicate_count / total_rows) * 100
        
        if duplicate_count > 0:
            score -= 20
            summary_logs.append(f"🔴 Found {duplicate_count} duplicate records based on '{primary_key}' ({duplicate_rate:.2f}%).")
        else:
            summary_logs.append("✅ No duplicates found in Primary Key.")
    else:
        summary_logs.append(f"⚠️ Primary Key '{primary_key}' not found in dataset.")
        
    # --- 3. Check Timeliness ---
    timeliness_status = "Unknown"
    if 'Crash Date/Time' in df.columns:
        # Ensure it's datetime
        if not pd.api.types.is_datetime64_any_dtype(df['Crash Date/Time']):
            try:
                temp_dates = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
            except:
                temp_dates = pd.Series([pd.NaT] * total_rows)
        else:
            temp_dates = df['Crash Date/Time']
            
        valid_dates = temp_dates.dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            timeliness_status = f"From {min_date.date()} to {max_date.date()}"
            
            # Future date check
            future_dates = valid_dates[valid_dates > pd.Timestamp.now()]
            if not future_dates.empty:
                score -= 10
                summary_logs.append(f"🔴 Found {len(future_dates)} records with future dates.")
            
            # "Currentness" check (arbitrary rule: if latest data is older than 1 year)
            if max_date < (pd.Timestamp.now() - pd.DateOffset(years=4)): # 4 years for this older dataset sample
                 summary_logs.append(f"⚠️ Data might be outdated. Latest record is from {max_date. year}.")
        else:
             summary_logs.append("⚠️ 'Crash Date/Time' column exists but contains no valid dates.")

    # --- 4. Column-wise Completeness & Accuracy Loop ---
    for col in df.columns:
        col_data = df[col]
        missing_count = col_data.isnull().sum()
        missing_pct = (missing_count / total_rows) * 100
        unique_vals = col_data.nunique()
        dtype = str(col_data.dtype)
        
        status = "Valid"
        
        # Completeness Rule
        if missing_pct > 0:
            if col in key_fields and missing_pct > 1.0:
                status = "Critical"
                score -= 5 # Deduct per critical column failure
                summary_logs.append(f"🔴 Critical Field '{col}' has {missing_pct:.1f}% missing values (High Risk).")
            elif missing_pct > 5.0:
                status = "Warning"
                # smaller deduction for non-critical
                score -= 1
            elif missing_pct > 0:
                 status = "Warning" # Minor warning
        
        # Specific Accuracy Checks per column
        # Vehicle Year
        if col == 'Vehicle Year':
            # coerce to numeric
            numeric_years = pd.to_numeric(col_data, errors='coerce')
            invalid_years = numeric_years[(numeric_years < 1900) | (numeric_years > datetime.datetime.now().year + 1)]
            if len(invalid_years) > 0:
                status = "Critical" if status != "Critical" else "Critical"
                score -= 5
                summary_logs.append(f"🔴 '{col}' contains {len(invalid_years)} invalid year values (<1900 or Future).")

        col_stats.append({
            "Column Name": col,
            "Type": dtype,
            "% Missing": f"{missing_pct:.2f}%",
            "Unique Values": unique_vals,
            "Status": status
        })

    # Final Score Constraints
    score = max(0, min(100, score))
    
    details_table = pd.DataFrame(col_stats)
    
    return {
        "score": score,
        "summary": summary_logs,
        "details_table": details_table,
        "timeliness_str": timeliness_status
    }
