
import pandas as pd

def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Generates automated insights based on the dataframe.
    Returns a list of markdown strings formatted as requested.
    """
    insights = []
    
    if df.empty:
        return ["No data available to generate insights."]

    # 1. Top Performer Insight (Business Logic)
    # We try to find a relevant categorical column 'Collision Type' or 'Agency Name'
    # Default to finding the object column with the fewest unique values (likely manageable categories) but > 1
    target_col = None
    if 'Collision Type' in df.columns:
        target_col = 'Collision Type'
    elif 'Agency Name' in df.columns:
        target_col = 'Agency Name'
    
    if target_col:
        top_val_counts = df[target_col].value_counts()
        if not top_val_counts.empty:
            top_cat = top_val_counts.idxmax()
            top_count = top_val_counts.max()
            total_count = len(df)
            percent = (top_count / total_count) * 100
            
            insight_str = f"""
### 💡 Key Insight: Dominant Trend
* **What (เกิดอะไรขึ้น):** {target_col} '{top_cat}' is the most frequent, appearing {top_count:,} times.
* **Why (ทำไมถึงเป็นแบบนั้น):** This category accounts for {percent:.1f}% of all recorded events, indicating a significant pattern.
* **So What (สำคัญอย่างไร):** A high concentration in '{top_cat}' drives the majority of incident volume.
* **Now What (ทำอะไรต่อ):** Focus preventive measures and resource allocation specifically on mitigating '{top_cat}'.
            """
            insights.append(insight_str.strip())

    # 2. Main Pain Point (Data Quality Logic)
    # Find column with highest missing values
    missing_series = df.isnull().sum()
    if not missing_series.empty and missing_series.max() > 0:
        worst_col = missing_series.idxmax()
        missing_count = missing_series.max()
        missing_pct = (missing_count / len(df)) * 100
        
        # Only report if significant
        if missing_pct > 5:
            dq_str = f"""
### 🚨 Key Insight: Data Pain Point
* **What (เกิดอะไรขึ้น):** The column '{worst_col}' has {missing_count:,} missing values ({missing_pct:.1f}%).
* **Why (ทำไมถึงเป็นแบบนั้น):** Likely due to optional data entry or system integration gaps.
* **So What (สำคัญอย่างไร):** This high missing rate compromises analysis related to '{worst_col}'.
* **Now What (ทำอะไรต่อ):** Implement mandatory field checks or use the 'Data Cleaning' module to impute values.
            """
            insights.append(dq_str.strip())
            
    return insights
