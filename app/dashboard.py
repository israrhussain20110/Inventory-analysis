
import streamlit as st
import requests
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="Inventory Analysis Dashboard",
    page_icon="📦",
    layout="wide",
)

# --- API Base URL ---
API_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def get_metrics(item_id=None, period='monthly'):
    """Fetches metrics from the API."""
    endpoint = f"{API_URL}/inventory/metrics"
    params = {"item_id": item_id, "period": period} if item_id else {"period": period}
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching metrics: {e}")
        return None

def get_slow_movers():
    """Fetches slow-moving and obsolete items from the API."""
    endpoint = f"{API_URL}/inventory/slow_movers"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching slow movers: {e}")
        return None

def get_stockout_heatmap_data(item_id=None):
    """Fetches stockout heatmap data from the API."""
    endpoint = f"{API_URL}/inventory/stockouts/heatmap"
    params = {"item_id": item_id} if item_id else {}
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stockout heatmap data: {e}")
        return None

# --- Main Dashboard ---
st.title("📦 Inventory Analysis Dashboard")
st.write("An interactive dashboard to analyze inventory levels, turnover, and stockouts.")

# --- Sidebar ---
st.sidebar.header("Filters")
item_id_input = st.sidebar.text_input("Enter Item ID (optional)")
period_input = st.sidebar.selectbox("Select Period for Turnover", ['daily', 'weekly', 'monthly'])

# --- Data Loading ---
if st.sidebar.button("Load Data"):
    st.session_state.metrics = get_metrics(item_id_input, period_input)
    st.session_state.slow_movers = get_slow_movers()
    st.session_state.stockout_heatmap_data = get_stockout_heatmap_data(item_id_input)

# --- Display Metrics ---
if 'metrics' in st.session_state and st.session_state.metrics:
    st.header("Key Metrics")
    metrics = st.session_state.metrics
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        
        turnover_data = metrics.get('turnover', [])
        if turnover_data:
            # Assuming turnover_data is a list of dicts, e.g., [{'date': '...', 'turnover_ratio': X}]
            # Extract turnover_ratio values and calculate the average
            turnover_ratios = [item['turnover_ratio'] for item in turnover_data if 'turnover_ratio' in item]
            if turnover_ratios:
                avg_turnover = sum(turnover_ratios) / len(turnover_ratios)
                st.metric("Average Turnover Ratio", f"{avg_turnover:.2f}")
            else:
                st.metric("Average Turnover Ratio", "N/A")
        else:
            st.metric("Average Turnover Ratio", "N/A")
    with col2:
        st.metric("Stockout Rate", f"{metrics.get('stockout_rate', {}).get('stockout_rate', 0):.2f}%")
    with col3:
        st.metric("Days of Supply", f"{metrics.get('days_of_supply', {}).get('days_of_supply', 0):.2f}")
    with col4:
        st.metric("Carrying Cost", f"${metrics.get('carrying_cost', {}).get('carrying_cost', 0):,.2f}")

# --- Display Slow Movers & Obsolete Items ---
if 'slow_movers' in st.session_state and st.session_state.slow_movers:
    st.header("Slow-Moving & Obsolete Items")
    slow_movers = st.session_state.slow_movers
    
    slow_df = pd.DataFrame(slow_movers.get('slow_movers', []), columns=['Item ID'])
    obsolete_df = pd.DataFrame(slow_movers.get('obsolete_items', []), columns=['Item ID'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Slow Movers")
        st.dataframe(slow_df)
    with col2:
        st.subheader("Obsolete Items")
        st.dataframe(obsolete_df)

# --- Charts ---
st.header("Visualizations")

# Turnover Trend
st.subheader("Turnover Trend")
if 'metrics' in st.session_state and st.session_state.metrics and st.session_state.metrics.get('turnover'):
    turnover_data_for_df = st.session_state.metrics['turnover']
    if isinstance(turnover_data_for_df, dict):
        turnover_data_for_df = [turnover_data_for_df] # Wrap single dict in a list
    turnover_df = pd.DataFrame(turnover_data_for_df)
    if not turnover_df.empty and 'Date' in turnover_df.columns:
        chart = alt.Chart(turnover_df).mark_line().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('turnover_ratio:Q', title='Turnover Ratio'),
            tooltip=['date:T', 'turnover_ratio:Q']
        ).properties(
            title='Turnover Ratio Over Time'
        )
        st.altair_chart(chart, use_container_width=True) # This line was already present
    else:
        st.write("No turnover data to display.")
else:
    st.write("Load data to see the turnover trend.")

# Placeholder for Stockout Heatmap
st.subheader("Stockout Heatmap")
st.write("Chart placeholder - coming soon!")

# Days of Supply (DoS) Distribution
st.subheader("Days of Supply (DoS) Distribution")
if 'metrics' in st.session_state and st.session_state.metrics and st.session_state.metrics.get('days_of_supply'):
    dos_df = pd.DataFrame.from_dict(st.session_state.metrics['days_of_supply'], orient='index', columns=['days_of_supply_value'])
    if not dos_df.empty:
        chart = alt.Chart(dos_df).mark_bar().encode(
            alt.X("days_of_supply_value:Q", bin=True, title="Days of Supply"),
            alt.Y('count()', title="Number of Items"),
            tooltip=['count()']
        ).properties(
            title="Distribution of Days of Supply"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No Days of Supply data to display.")
else:
    st.write("Load data to see the DoS distribution.")

# Carrying Cost Breakdown
st.subheader("Carrying Cost Breakdown")
if 'metrics' in st.session_state and st.session_state.metrics and st.session_state.metrics.get('carrying_cost'):
    carrying_cost_data = st.session_state.metrics['carrying_cost']
    if isinstance(carrying_cost_data, dict):
        # Assuming carrying_cost_data is a dict like {'item_id1': cost1, 'item_id2': cost2}
        carrying_cost_df = pd.DataFrame.from_dict(carrying_cost_data, orient='index', columns=['carrying_cost']).reset_index()
        carrying_cost_df.rename(columns={'index': 'item_id'}, inplace=True)
    else:
        # Assuming carrying_cost_data is already a list of dicts or similar
        carrying_cost_df = pd.DataFrame(carrying_cost_data)

    if not carrying_cost_df.empty:
        chart = alt.Chart(carrying_cost_df).mark_bar().encode(
            x=alt.X('item_id:N', sort='-y', title='Item ID'),
            y=alt.Y('carrying_cost:Q', title='Carrying Cost'),
            tooltip=['item_id', 'carrying_cost']
        ).properties(
            title='Carrying Cost Breakdown by Item'
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No Carrying Cost data to display.")
else:
    st.write("Load data to see the Carrying Cost Breakdown.")

# Slow/Obsolete Alerts
st.subheader("Slow/Obsolete Alerts")
if 'slow_movers' in st.session_state and st.session_state.slow_movers:
    slow_movers = st.session_state.slow_movers.get('slow_movers', [])
    obsolete_items = st.session_state.slow_movers.get('obsolete_items', [])

    if slow_movers or obsolete_items:
        if slow_movers:
            st.warning(f"**{len(slow_movers)}** Slow-Moving Items: {', '.join(slow_movers)}")
        if obsolete_items:
            st.error(f"**{len(obsolete_items)}** Obsolete Items: {', '.join(obsolete_items)}")
    else:
        st.info("No slow-moving or obsolete items detected.")
else:
    st.write("Load data to check for slow-moving and obsolete items.")
