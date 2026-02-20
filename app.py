"""
COMP 3610: Big Data Analytics - Assignment 1
NYC Yellow Taxi Trip Data Dashboard

Student ID: 816034871

Interactive Streamlit dashboard for analyzing NYC Yellow Taxi
trip records from January 2024.
"""

import streamlit as st

st.set_page_config(
    page_title="Yellow Taxi Analytics | Jan 2024",
    page_icon="\U0001F695",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import load_data, clear_cache, PAYMENT_TYPE_MAP

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("\U0001F695 Yellow Taxi Analytics")
st.sidebar.markdown("**January 2024 · NYC TLC Data**")
st.sidebar.divider()

st.sidebar.markdown(
    "Browse the pages above to explore dataset statistics "
    "and interactive trip visualizations."
)

st.sidebar.divider()
st.sidebar.caption("Student ID: 816034871")
st.sidebar.caption("COMP 3610 · Big Data Analytics")

if st.sidebar.button("\U0001F504 Refresh data cache"):
    clear_cache()
    st.rerun()

# ── Main content ─────────────────────────────────────────────────────────────
st.title("NYC Yellow Taxi Trip Analysis")
st.markdown(
    "Welcome! This dashboard provides an interactive look at **~2.8 million** "
    "yellow taxi trips recorded in **New York City during January 2024**. "
    "The underlying data was downloaded programmatically from the NYC Taxi & "
    "Limousine Commission, cleaned, and enriched with derived features."
)

df = load_data()

# ── Headline numbers ─────────────────────────────────────────────────────────
st.markdown("### At a Glance")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Trips Recorded", f"{len(df):,}")
m2.metric("Avg Fare (\$)", f"{df['fare_amount'].mean():.2f}")
m3.metric(
    "Revenue (Total)",
    f"${df['total_amount'].sum() / 1_000_000:.2f}M",
)
m4.metric("Avg Distance", f"{df['trip_distance'].mean():.2f} mi")
m5.metric("Avg Duration", f"{df['trip_duration_minutes'].mean():.1f} min")

st.divider()

# ── Quick facts ──────────────────────────────────────────────────────────────
st.markdown("### Quick Facts")

left, right = st.columns(2)

with left:
    days_covered = df["pickup_date"].nunique()
    st.success(f"\U0001F4C5  **{days_covered} calendar days** of trip data (January 2024)")

with right:
    top_pay = int(df["payment_type"].value_counts().index[0])
    st.success(
        f"\U0001F4B3  **{PAYMENT_TYPE_MAP.get(top_pay, 'Other')}** is the most popular payment method"
    )

st.divider()

# ── Page guide ───────────────────────────────────────────────────────────────
st.markdown("### Explore the Dashboard")

col_a, col_b = st.columns(2)

with col_a:
    st.info(
        "**\U0001F4CA  Overview**\n\n"
        "Inspect dataset dimensions, column types, missing-value counts, "
        "and basic summary statistics."
    )

with col_b:
    st.info(
        "**\U0001F4C8  Visualizations**\n\n"
        "Five interactive Plotly charts with date, hour, and payment-type "
        "filters. Each chart includes a brief interpretation."
    )

st.markdown("---")
st.caption(
    "Data Source: NYC Taxi & Limousine Commission · January 2024  \n"
    "Built with Streamlit, Pandas, DuckDB, and Plotly  \n"
    "COMP 3610 — Big Data Analytics — Assignment 1"
)
