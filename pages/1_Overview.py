"""
COMP 3610: Big Data Analytics - Assignment 1
Page 1: Overview - Dataset inspection and quality assessment

Student ID: 816034871
"""

import streamlit as st
import pandas as pd
from utils import load_data

st.title("Dataset Overview")
st.markdown(
    "This page summarises the cleaned and feature-engineered NYC Yellow Taxi "
    "dataset for **January 2024**. Use the sections below to explore dimensions, "
    "distributions, and data-quality indicators."
)

df = load_data()

# ── Headline metrics ─────────────────────────────────────────────────────────
st.markdown("#### Dataset Dimensions")

min_dt = df['tpep_pickup_datetime'].min()
max_dt = df['tpep_pickup_datetime'].max()
num_days = (max_dt.date() - min_dt.date()).days + 1

a, b, c, d = st.columns(4)
a.metric("Total Rows", f"{len(df):,}")
b.metric("Total Columns", f"{len(df.columns):,}")
c.metric("Day Span", f"{num_days} days")
d.metric("Memory Footprint", f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

st.caption(f"Earliest pickup: **{min_dt.date()}** — Latest pickup: **{max_dt.date()}**")
st.divider()

# ── Expandable sections instead of tabs ──────────────────────────────────────

with st.expander("Summary Statistics", expanded=True):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    defaults = [c for c in ["fare_amount", "trip_distance", "tip_amount",
                             "total_amount", "trip_duration_minutes", "trip_speed_mph"]
                if c in df.columns]
    chosen = st.multiselect(
        "Select numeric columns to describe:", numeric_cols, default=defaults, key="stats_cols"
    )
    if chosen:
        st.dataframe(df[chosen].describe(), width="stretch")
    else:
        st.warning("Pick at least one column to see statistics.")

with st.expander("Sample Rows"):
    row_count = st.slider("Number of rows to show", 5, 200, 15, step=5)
    cols_to_show = st.multiselect(
        "Columns:", df.columns.tolist(), default=df.columns[:8].tolist(), key="sample_cols"
    )
    if cols_to_show:
        st.dataframe(df[cols_to_show].head(row_count), width="stretch")
    else:
        st.warning("Pick at least one column.")

with st.expander("Column Types & Nulls"):
    info_rows = {
        "Column": df.columns.tolist(),
        "Dtype": [str(df[c].dtype) for c in df.columns],
        "Non-Null Count": [df[c].notna().sum() for c in df.columns],
        "Null %": [round(df[c].isna().sum() / len(df) * 100, 2) for c in df.columns],
    }
    st.dataframe(pd.DataFrame(info_rows), width="stretch")

st.divider()

# ── Data quality ─────────────────────────────────────────────────────────────
st.markdown("#### Data Quality Assessment")

left, right = st.columns(2)

with left:
    st.markdown("**Missing Values**")
    missing_info = {
        "Column": df.columns.tolist(),
        "Missing": [df[c].isna().sum() for c in df.columns],
        "Missing %": [round(df[c].isna().sum() / len(df) * 100, 2) for c in df.columns],
    }
    missing_df = pd.DataFrame(missing_info)
    missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)

    if len(missing_df) > 0:
        st.dataframe(missing_df, width="stretch")
    else:
        st.success("No missing values remain after cleaning.")

with right:
    st.markdown("**Numeric Ranges**")
    range_cols = [c for c in ["fare_amount", "trip_distance", "tip_amount",
                              "passenger_count", "trip_duration_minutes"]
                  if c in df.columns]
    if range_cols:
        rows = [{"Column": c, "Min": df[c].min(), "Max": df[c].max()} for c in range_cols]
        st.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.info("No numeric range columns found.")
