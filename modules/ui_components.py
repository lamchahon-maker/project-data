
import streamlit as st

def render_empty_state(image_path_or_icon: str, message: str):
    """
    Renders a styled empty state when no data is available.
    
    Args:
        image_path_or_icon (str): Path to an image or an emoji.
        message (str): The message to display.
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 50px;">
            <div style="font-size: 50px;">{image_path_or_icon}</div>
            <h3 style="color: #666;">{message}</h3>
            <p style="color: #999;">Try adjusting your filters or reloading the dataset.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_card(title: str, value: str, delta: str = None, color: str = "blue"):
    """
    Renders a metric card.
    
    Args:
        title (str): Title of the metric.
        value (str): Value to display.
        delta (str): The change/delta (optional).
        color (str): Accent color (not strictly used in native metric but good for custom styling if expanded).
    """
    st.metric(label=title, value=value, delta=delta)

def render_history_log(df_log):
    """
    Renders the history log table with styling.
    """
    if df_log.empty:
        render_empty_state("📝", "No cleaning history available.")
        return

    st.subheader("Traceability & Cleaning History")
    st.dataframe(df_log, use_container_width=True)
