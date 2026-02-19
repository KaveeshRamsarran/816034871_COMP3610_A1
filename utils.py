"""
COMP 3610: Big Data Analytics - Assignment 1  
Utility Functions for Data Loading and Processing

Student ID: 816034871
"""

import pandas as pd
import streamlit as st
import requests

# =============================================================================
# Configuration
# =============================================================================

TAXI_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Payment type mapping
PAYMENT_TYPE_MAP = {
    0: 'Unknown',
    1: 'Credit Card',
    2: 'Cash',
    3: 'No Charge',
    4: 'Dispute',
    5: 'Unknown',
    6: 'Voided Trip'
}


@st.cache_data(show_spinner="Loading trip data...", ttl=3600)
def load_data() -> pd.DataFrame:
    """Load and clean trip data (cached). Downloads directly from URL."""
    df = pd.read_parquet(TAXI_DATA_URL)
    
    # Cleaning
    critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                        'trip_distance', 'fare_amount', 'total_amount',
                        'PULocationID', 'DOLocationID']
    df = df.dropna(subset=critical_columns)
    df = df[df['trip_distance'] > 0]
    df = df[df['fare_amount'] > 0]
    df = df[df['total_amount'] > 0]
    
    # Keep only January 2024 data
    df = df[(df['tpep_pickup_datetime'] >= '2024-01-01') & 
            (df['tpep_pickup_datetime'] < '2024-02-01')]
    
    # Calculate duration
    df['trip_duration_minutes'] = (
        (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime'])
        .dt.total_seconds() / 60
    ).round(2)
    
    df = df[(df['trip_duration_minutes'] >= 1) & (df['trip_duration_minutes'] <= 1440)]
    
    # Calculate speed
    df['trip_speed_mph'] = (
        df['trip_distance'] / (df['trip_duration_minutes'] / 60)
    ).round(2)
    df = df[df['trip_speed_mph'] <= 100]
    
    # Add temporal features
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    df['pickup_day_name'] = df['tpep_pickup_datetime'].dt.day_name()
    df['pickup_date'] = df['tpep_pickup_datetime'].dt.date
    
    # Map payment types
    df['payment_method'] = df['payment_type'].map(PAYMENT_TYPE_MAP).fillna('Other')
    
    return df


@st.cache_data(show_spinner="Loading zone lookup...", ttl=3600)
def load_zones() -> pd.DataFrame:
    """Load zone lookup table (cached). Downloads directly from URL."""
    return pd.read_csv(ZONE_LOOKUP_URL)


def clear_cache():
    """Clear all Streamlit caches."""
    st.cache_data.clear()
    st.cache_data.clear()
