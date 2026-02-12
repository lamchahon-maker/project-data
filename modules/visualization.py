
import pandas as pd
import plotly.express as px
import streamlit as st

def plot_trend(df: pd.DataFrame, date_col: str, rolling_window: int = 7) -> None:
    """
    Plots a trend line chart over time.
    
    Args:
        df (pd.DataFrame): The dataframe.
        date_col (str): The date column name.
        rolling_window (int): Window size for rolling mean.
    """
    # Group by date (day)
    # Ensure date_col is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
         st.warning(f"Column '{date_col}' is not a datetime column.")
         return

    # Aggregate counts per day
    daily_counts = df.groupby(df[date_col].dt.date).size().reset_index(name='Counts')
    daily_counts[date_col] = pd.to_datetime(daily_counts[date_col])
    
    fig = px.line(daily_counts, x=date_col, y='Counts', title=f'Daily Trend ({date_col})')
    
    if rolling_window > 0:
        daily_counts['Rolling Mean'] = daily_counts['Counts'].rolling(window=rolling_window).mean()
        fig.add_scatter(x=daily_counts[date_col], y=daily_counts['Rolling Mean'], mode='lines', name=f'{rolling_window}-Day Rolling Mean')
        
    st.plotly_chart(fig, use_container_width=True)

def plot_distribution(df: pd.DataFrame, num_col: str, type: str = "Histogram", show_outliers: bool = True) -> None:
    """
    Plots distribution of a numeric column.
    
    Args:
        df (pd.DataFrame): The dataframe.
        num_col (str): Numeric column name.
        type (str): 'Histogram' or 'Boxplot'.
        show_outliers (bool): Whether to show outliers in boxplot.
    """
    # Sample if large for performance (for scatter/strip type plots, but prompt mainly mentioned scatter lag)
    # For Histogram/Boxplot, 200k is usually fine for Plotly, but we can sample if > 50k just to be safe and responsive
    plot_df = df
    title_suffix = ""
    
    if len(df) > 50000:
        plot_df = df.sample(n=10000)
        title_suffix = " (Sampled 10k)"
        
    if type == "Histogram":
        fig = px.histogram(plot_df, x=num_col, title=f"Distribution of {num_col}{title_suffix}", marginal="box" if show_outliers else None)
    elif type == "Boxplot":
        fig = px.box(plot_df, y=num_col, title=f"Boxplot of {num_col}{title_suffix}", points="all" if show_outliers else False)
    else:
        st.warning("Invalid plot type")
        return

    st.plotly_chart(fig, use_container_width=True)

def plot_categorical(df: pd.DataFrame, cat_col: str, top_n: int = 15) -> None:
    """
    Plots a bar chart for a categorical column.
    
    Args:
        df (pd.DataFrame): Dataframe.
        cat_col (str): Categorical column.
        top_n (int): Top N categories to show.
    """
    counts = df[cat_col].value_counts().nlargest(top_n).reset_index()
    counts.columns = [cat_col, 'Count']
    
    fig = px.bar(
        counts, 
        x=cat_col, 
        y='Count', 
        title=f"Top {top_n} {cat_col}",
        text='Count'
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)
