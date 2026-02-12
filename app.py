import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data_loader import load_dataset
from modules.data_audit import run_audit
from modules.cleaning import impute_column, fix_date_format
from modules.visualization import plot_trend, plot_distribution, plot_categorical
from modules.insights import generate_insights
from modules.data_processor import clean_dataset, HistoryLogger
from modules.ui_components import render_empty_state, render_metric_card, render_history_log

# Page Config
st.set_page_config(
    page_title="Crash Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Data Quality Audit", "Data Cleaning", "Data History Log"])

# --- Load Data ---
DATA_FILE = "crash_data_v2.csv"

# แก้ไขจุดนี้: บังคับให้อ่านแบบแยกด้วย semicolon (;) และจัดการเรื่อง encoding เพื่อรองรับภาษาไทย/ตัวอักษรพิเศษ
try:
    raw_df = pd.read_csv(DATA_FILE, sep=';', engine='python')
except Exception as e:
    st.error(f"Error loading data: {e}")
    raw_df = pd.DataFrame()

# Initialize Logger and Clean Data
logger = HistoryLogger()
if not raw_df.empty:
    df = clean_dataset(raw_df, logger)
else:
    df = pd.DataFrame()

# --- DASHBOARD PAGE ---
if page == "Dashboard":
    st.title("🚗 High-Performance Crash Analysis")
    
    # Global Sidebar Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")
    
    filtered_df = df.copy()
    
    if not df.empty:
        # Year Filter
        if 'Vehicle Year' in df.columns:
            valid_years = sorted([int(float(y)) for y in df['Vehicle Year'].dropna().unique() if str(y).replace('.','').isdigit()])
            if valid_years:
                selected_years = st.sidebar.multiselect(
                    "Filter by Vehicle Year",
                    options=valid_years,
                    default=valid_years[-3:] if len(valid_years) > 3 else valid_years
                )
                if selected_years:
                    filtered_df = filtered_df[filtered_df['Vehicle Year'].isin(selected_years)]
        
        # Agency Filter
        if 'Agency Name' in df.columns:
            agencies = sorted(df['Agency Name'].astype(str).unique())
            picked_agencies = st.sidebar.multiselect("Filter by Agency", options=agencies)
            if picked_agencies:
                filtered_df = filtered_df[filtered_df['Agency Name'].isin(picked_agencies)]
    
    if filtered_df.empty:
        render_empty_state("🔍", "No records found for the selected filters.")
    else:
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Crashes", f"{len(filtered_df):,}")
        with col2:
             if 'Injury Severity' in filtered_df.columns:
                injury_count = len(filtered_df[filtered_df['Injury Severity'] != 'NO APPARENT INJURY'])
                render_metric_card("Injuries", f"{injury_count:,}")
        with col3:
             if 'Agency Name' in filtered_df.columns:
                 top_agency = filtered_df['Agency Name'].mode()[0] if not filtered_df['Agency Name'].empty else "N/A"
                 render_metric_card("Top Agency", str(top_agency))
        
        st.markdown("### 📊 Advanced Visualizations")
        
        if 'Crash Date/Time' in filtered_df.columns:
            st.subheader("Trend Analysis")
            rolling = st.slider("Rolling Mean Window (Days)", 0, 30, 7)
            plot_trend(filtered_df, 'Crash Date/Time', rolling_window=rolling)
            
        col_cat, col_dist = st.columns(2)
        with col_cat:
            st.subheader("Collision Analysis")
            if 'Collision Type' in filtered_df.columns:
                plot_categorical(filtered_df, 'Collision Type')
                
        with col_dist:
            st.subheader("Vehicle Year Distribution")
            if 'Vehicle Year' in filtered_df.columns:
                show_out_switch = st.checkbox("Show Outliers", value=True)
                plot_distribution(filtered_df, 'Vehicle Year', type="Boxplot", show_outliers=show_out_switch)

        st.markdown("---")
        st.subheader("🤖 Automated Insights")
        insights = generate_insights(filtered_df)
        for insight in insights:
            st.info(insight)

# --- DATA QUALITY AUDIT PAGE ---
elif page == "Data Quality Audit":
    st.title("🕵️ Data Quality Audit")
    if raw_df.empty:
        render_empty_state("⚠️", "Cannot perform audit. Dataset is empty or missing.")
    else:
        audit_results = run_audit(raw_df)
        score = audit_results["score"]
        col_score, col_summary = st.columns([1, 3])
        
        with col_score:
            st.metric("Data Health Score", f"{score}/100")
            if score >= 80: st.success("Data is in Good Health")
            elif score >= 50: st.warning("Data needs Cleaning")
            else: st.error("Critical Issues Found")
                
        with col_summary:
            st.subheader("Audit Summary")
            for msg in audit_results["summary"]:
                if "🔴" in msg: st.error(msg)
                elif "⚠️" in msg: st.warning(msg)
                else: st.info(msg)

        st.divider()
        st.subheader("Column Level Analysis")
        details_df = audit_results["details_table"]
        if not details_df.empty:
             st.dataframe(details_df, use_container_width=True)

# --- DATA HISTORY LOG PAGE ---
elif page == "Data History Log":
    st.title("📜 Data Usage & History Log")
    log_df = logger.get_log()
    render_history_log(log_df)

# --- DATA CLEANING PAGE ---
elif page == "Data Cleaning":
    st.title("🧹 Interactive Data Cleaning")
    if 'cleaning_log' not in st.session_state:
        st.session_state['cleaning_log'] = []
    if 'clean_df' not in st.session_state:
        st.session_state['clean_df'] = df.copy()

    current_df = st.session_state['clean_df']
    if current_df.empty:
        render_empty_state("⚠️", "No data to clean.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            target_col = st.selectbox("Select Column", current_df.columns)
            cleaning_action = st.radio("Action", ["Impute Missing Values", "Fix Date Format"])
            if cleaning_action == "Impute Missing Values":
                strategy = st.radio("Strategy", ["Mean", "Median", "Mode", "Drop Rows"])
                if st.button("Apply"):
                    new_df, msg = impute_column(current_df, target_col, strategy)
                    st.session_state['clean_df'] = new_df
                    st.session_state['cleaning_log'].append(msg)
                    st.rerun()
        with col2:
            st.metric("Missing Values", f"{current_df[target_col].isnull().sum()}")
            st.dataframe(current_df[[target_col]].head(10), use_container_width=True)

