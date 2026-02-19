"""
COMP 3610: Big Data Analytics - Assignment 1
NYC Yellow Taxi Trip Data Dashboard

Student ID: 816034871

This Streamlit application provides an interactive dashboard for exploring
NYC Yellow Taxi trip data from January 2024.
"""

import streamlit as st

st.set_page_config(
    page_title="NYC Yellow Taxi Dashboard (Jan 2024)",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import load_data, clear_cache, PAYMENT_TYPE_MAP

# Sidebar - Clear cache button
with st.sidebar:
    if st.button("Clear cache + rerun"):
        clear_cache()
        st.rerun()

st.title("NYC Yellow Taxi Dashboard (January 2024)")

st.write(
    "This dashboard explores NYC Yellow Taxi trips for January 2024. "
    "Use the sidebar pages to view an overview of the cleaned dataset "
    "and interactive visualizations with filters."
)

# The dataset is programmatically downloaded and processed in utils.py,
# where cleaning and feature engineering are applied prior to visualization.

df = load_data()

# =============================================================================
# Key Metrics
# =============================================================================
st.subheader("Key Summary Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Trips",
    f"{len(df):,}"
)

col2.metric(
    "Average Fare",
    f"${df['fare_amount'].mean():.2f}"
)

total_rev = df["total_amount"].sum()
col3.metric(
    "Total Revenue",
    f"${total_rev/1_000_000:.2f}M"
)

col4.metric(
    "Average Distance",
    f"{df['trip_distance'].mean():.2f} miles"
)

col5.metric(
    "Average Duration",
    f"{df['trip_duration_minutes'].mean():.1f} mins"
)

st.divider()

# =============================================================================
# Data Coverage
# =============================================================================
st.subheader("Data Coverage")

c1, c2 = st.columns(2)

with c1:
    num_days = df["pickup_date"].nunique()
    st.info(f"**Days covered:** {num_days} days (January 2024)")

with c2:
    top_payment_code = int(df["payment_type"].value_counts().index[0])
    st.info(
        f"**Most common payment:** {top_payment_code} - {PAYMENT_TYPE_MAP.get(top_payment_code, 'Other')}"
    )

st.divider()

# =============================================================================
# Navigation Help
# =============================================================================
st.subheader("Navigation")

st.markdown("""
**Use the sidebar to navigate between pages:**

1. **Overview** - Dataset statistics, data quality checks, and column information
2. **Visualizations** - Interactive charts with filters:
   - Top 10 Pickup Zones
   - Average Fare by Hour
   - Trip Distance Distribution
   - Payment Type Breakdown
   - Day/Hour Heatmap
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>COMP 3610: Big Data Analytics - Assignment 1</strong></p>
    <p>Data Source: NYC Taxi & Limousine Commission | January 2024</p>
    <p>Student ID: 816034871</p>
</div>
""", unsafe_allow_html=True)
