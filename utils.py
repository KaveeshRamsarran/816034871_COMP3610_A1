"""
COMP 3610: Big Data Analytics - Assignment 1  
Utility Functions for Data Loading and Processing

Student ID: 816034871
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import requests

# =============================================================================
# Configuration
# =============================================================================

TAXI_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

DATA_DIR = Path("data/raw")
PARQUET_PATH = DATA_DIR / "yellow_tripdata_2024-01.parquet"
LOOKUP_PATH = DATA_DIR / "taxi_zone_lookup.csv"
PROCESSED_PATH = Path("data/processed/taxi_data_processed.parquet")

# Payment type mapping
PAYMENT_TYPE_MAP = {
    1: 'Credit Card',
    2: 'Cash',
    3: 'No Charge',
    4: 'Dispute',
    5: 'Unknown',
    6: 'Voided Trip'
}


def _ensure_data_files() -> None:
    """Download raw files if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download trip parquet if missing
    if not PARQUET_PATH.exists() or PARQUET_PATH.stat().st_size == 0:
        with requests.get(TAXI_DATA_URL, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(PARQUET_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
    
    # Download lookup CSV if missing
    if not LOOKUP_PATH.exists() or LOOKUP_PATH.stat().st_size == 0:
        r = requests.get(ZONE_LOOKUP_URL, timeout=60)
        r.raise_for_status()
        LOOKUP_PATH.write_bytes(r.content)


@st.cache_data(show_spinner="Loading trip data...", ttl=3600)
def load_data() -> pd.DataFrame:
    """Load and clean trip data (cached)."""
    # Use processed data if available
    if PROCESSED_PATH.exists():
        return pd.read_parquet(PROCESSED_PATH)
    
    # Otherwise load and process raw data
    _ensure_data_files()
    df = pd.read_parquet(PARQUET_PATH)
    
    # Cleaning
    critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                        'trip_distance', 'fare_amount', 'total_amount',
                        'PULocationID', 'DOLocationID']
    df = df.dropna(subset=critical_columns)
    df = df[df['trip_distance'] > 0]
    df = df[df['fare_amount'] > 0]
    df = df[df['total_amount'] > 0]
    
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
    """Load zone lookup table (cached)."""
    _ensure_data_files()
    return pd.read_csv(LOOKUP_PATH)


def clear_cache():
    """Clear all Streamlit caches."""
    st.cache_data.clear()
