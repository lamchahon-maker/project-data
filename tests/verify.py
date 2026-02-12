
import sys
import os
import pandas as pd
import numpy as np

# Add root to path
# Assuming verify.py is in tests/ and modules is in root (../modules)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Testing Imports...")
    # These imports will fail if modules folder is not found or dependencies missing
    from modules.data_loader import load_dataset
    from modules.data_processor import clean_dataset, HistoryLogger
    from modules.ui_components import render_empty_state
    print("Imports Successful.")

    print("Testing Data Loading (Mock)...")
    # mocked for speed/absence of file in test env if needed, but we have the file
    # We will just test the function existence and empty file handling
    df = load_dataset("non_existent_file.csv")
    assert df.empty, "Should return empty DF for missing file"
    print("Data Loader Empty State Verified.")

    print("Testing Enhanced Data Audit logic...")
    mock_df = pd.DataFrame({
        'Report Number': ['1', '2', '1'], # Duplicate ID
        'Crash Date/Time': [pd.Timestamp.now() + pd.Timedelta(days=1), pd.Timestamp('2020-01-01'), pd.Timestamp('2021-01-01')], # Future date
        'Latitude': [38.0, 100.0, 39.0], 
        'Longitude': [-77.0, -200.0, -76.0],
        'Vehicle Year': [2020, 1800, 2025] # 1800 invalid
    })
    
    from modules.data_audit import run_audit
    
    audit_results = run_audit(mock_df)
    score = audit_results['score']
    summary = audit_results['summary']
    
    print(f"Audit Score: {score}")
    assert score < 100, "Score should be < 100 due to issues"
    
    # Check if we caught the duplicate
    assert any("duplicate" in s.lower() for s in summary), "Should detect duplicates"
    
    # Check if we caught future date
    assert any("future" in s.lower() for s in summary), "Should detect future dates"
    
    print("Testing Interactive Cleaning logic...")
    from modules.cleaning import impute_column, fix_date_format
    
    # Create a specific df for cleaning test with missing values
    clean_mock = pd.DataFrame({'A': [1, np.nan, 3], 'D': ['2020-01-01', 'not a date', '2021-01-02']})
    
    # Test Imputation (Mean)
    res_mean, msg_mean = impute_column(clean_mock, 'A', 'Mean')
    assert res_mean['A'].isnull().sum() == 0, "Mean imputation on clean_mock failed"
    # Expected mean of [1, 3] is 2.0
    assert res_mean['A'].iloc[1] == 2.0, "Mean value incorrect"
    assert "Mean" in msg_mean, "Log message incorrect for mean imputation"

    # Test Drop
    clean_mock_2 = pd.DataFrame({'A': [1, np.nan, 3]})
    res_drop, msg_drop = impute_column(clean_mock_2, 'A', 'Drop Rows')
    assert len(res_drop) == 2, "Drop rows failed"
    assert "Dropped" in msg_drop, "Log message incorrect for drop"
    
    # Test Date Fixing
    res_date, msg_date = fix_date_format(clean_mock, 'D')
    assert pd.api.types.is_datetime64_any_dtype(res_date['D']), "Date conversion failed"
    assert pd.isna(res_date['D'].iloc[1]), "Invalid date should be NaT"
    
    print("Interactive Cleaning Logic Verified.")
    
    print("Testing Visualization Logic...")
    from modules.visualization import plot_trend, plot_distribution, plot_categorical
    
    # Mock data for plotting
    plot_df = pd.DataFrame({
        'Date': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-03']),
        'Value': [10, 20, 15],
        'Category': ['A', 'B', 'A']
    })
    
    # Just ensure they run without error (Streamlit will warn about context but not crash)
    try:
        plot_trend(plot_df, 'Date')
        plot_distribution(plot_df, 'Value', type='Histogram')
        plot_categorical(plot_df, 'Category')
        print("Visualization functions executed successfully.")
    except Exception as e:
        print(f"Visualization failed: {e}")
        raise e

    print("Testing Automated Insights...")
    from modules.insights import generate_insights
    # Use mock dataframe
    insight_df = pd.DataFrame({
        'Collision Type': ['Type A', 'Type A', 'Type B'],
        'Missing Col': [1, None, None]
    })
    insights = generate_insights(insight_df)
    assert len(insights) > 0, "No insights generated"
    assert "Type A" in insights[0], "Top performer logic failed"
    # assert "Missing Col" in insights[1], "Data quality logic failed" # Might be index 1
    
    # Check for specific formatting content
    assert "What (เกิดอะไรขึ้น):" in insights[0], "Markdown format check failed"
    
    print("Automated Insights Verified.")

    print("Testing History Logger...")
    logger = HistoryLogger()
    logger.add_entry("Test", "Details", 100)
    log_df = logger.get_log()
    assert not log_df.empty, "Log should not be empty"
    print("History Logger Verified.")

    print("ALL CHECKS PASSED.")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED: {e}")
    sys.exit(1)
