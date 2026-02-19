"""
COMP 3610: Big Data Analytics - Assignment 1
NYC Yellow Taxi Trip Data Dashboard

Student ID: 816034871

This Streamlit application provides an interactive dashboard for exploring
NYC Yellow Taxi trip data from January 2024.
"""

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import requests
from datetime import datetime, timedelta

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="NYC Taxi Dashboard",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Data Loading Functions
# =============================================================================

# Data URLs
TAXI_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Local data paths
LOCAL_RAW_PARQUET = Path("data/raw/yellow_tripdata_2024-01.parquet")
LOCAL_PROCESSED_PARQUET = Path("data/processed/taxi_data_processed.parquet")
LOCAL_LOOKUP_CSV = Path("data/raw/taxi_zone_lookup.csv")

@st.cache_data(show_spinner="Loading taxi data...", ttl=3600)
def download_data():
    """Download the taxi trip data and zone lookup table.
    Uses local files if available, otherwise downloads from URL.
    """
    # Try local processed data first (fastest)
    if LOCAL_PROCESSED_PARQUET.exists():
        taxi_df = pd.read_parquet(LOCAL_PROCESSED_PARQUET)
        zones_df = pd.read_csv(LOCAL_LOOKUP_CSV) if LOCAL_LOOKUP_CSV.exists() else pd.read_csv(ZONE_LOOKUP_URL)
        return taxi_df, zones_df, True  # True = already processed
    
    # Try local raw data
    if LOCAL_RAW_PARQUET.exists():
        taxi_df = pd.read_parquet(LOCAL_RAW_PARQUET)
        zones_df = pd.read_csv(LOCAL_LOOKUP_CSV) if LOCAL_LOOKUP_CSV.exists() else pd.read_csv(ZONE_LOOKUP_URL)
        return taxi_df, zones_df, False  # False = needs processing
    
    # Download from URL
    taxi_df = pd.read_parquet(TAXI_DATA_URL)
    zones_df = pd.read_csv(ZONE_LOOKUP_URL)
    
    return taxi_df, zones_df, False

@st.cache_data(ttl=3600)
def clean_and_transform_data(df):
    """Clean the data and add engineered features."""
    df = df.copy()
    
    # Define critical columns
    critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                        'trip_distance', 'fare_amount', 'total_amount',
                        'PULocationID', 'DOLocationID']
    
    # Remove nulls in critical columns
    df = df.dropna(subset=critical_columns)
    
    # Remove invalid trips
    df = df[df['trip_distance'] > 0]
    df = df[df['fare_amount'] > 0]
    df = df[df['total_amount'] > 0]
    
    # Calculate duration
    df['trip_duration_minutes'] = (
        (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime'])
        .dt.total_seconds() / 60
    ).round(2)
    
    # Filter valid durations (1 min to 24 hours)
    df = df[(df['trip_duration_minutes'] >= 1) & (df['trip_duration_minutes'] <= 1440)]
    
    # Calculate average speed
    df['trip_speed_mph'] = (
        df['trip_distance'] / (df['trip_duration_minutes'] / 60)
    ).round(2)
    
    # Remove unrealistic speeds
    df = df[df['trip_speed_mph'] <= 100]
    
    # Add temporal features
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    df['pickup_day_name'] = df['tpep_pickup_datetime'].dt.day_name()
    df['pickup_date'] = df['tpep_pickup_datetime'].dt.date
    
    # Map payment types
    payment_map = {
        1: 'Credit Card',
        2: 'Cash',
        3: 'No Charge',
        4: 'Dispute',
        5: 'Unknown',
        6: 'Voided Trip'
    }
    df['payment_method'] = df['payment_type'].map(payment_map).fillna('Other')
    
    return df

@st.cache_data(show_spinner="Preparing data...", ttl=3600)
def load_data():
    """Main function to load and prepare all data."""
    taxi_df, zones_df, already_processed = download_data()
    
    # Skip cleaning if already processed
    if already_processed:
        clean_df = taxi_df
    else:
        clean_df = clean_and_transform_data(taxi_df)
    
    # Ensure required temporal columns exist (even if loaded from processed file)
    if 'pickup_date' not in clean_df.columns:
        clean_df['pickup_date'] = pd.to_datetime(clean_df['tpep_pickup_datetime']).dt.date
    if 'pickup_hour' not in clean_df.columns:
        clean_df['pickup_hour'] = pd.to_datetime(clean_df['tpep_pickup_datetime']).dt.hour
    if 'pickup_day_name' not in clean_df.columns:
        clean_df['pickup_day_name'] = pd.to_datetime(clean_df['tpep_pickup_datetime']).dt.day_name()
    if 'pickup_day_of_week' not in clean_df.columns:
        clean_df['pickup_day_of_week'] = pd.to_datetime(clean_df['tpep_pickup_datetime']).dt.dayofweek
    if 'payment_method' not in clean_df.columns:
        payment_map = {1: 'Credit Card', 2: 'Cash', 3: 'No Charge', 4: 'Dispute', 5: 'Unknown', 6: 'Voided Trip'}
        clean_df['payment_method'] = clean_df['payment_type'].map(payment_map).fillna('Other')
    
    return clean_df, zones_df

# =============================================================================
# SQL Query Functions
# =============================================================================

def run_sql_query(df, zones_df, query_type):
    """Run SQL queries using DuckDB."""
    con = duckdb.connect()
    con.register('trips', df)
    con.register('zones', zones_df)
    
    queries = {
        'top_pickup_zones': """
            SELECT 
                z.Zone as pickup_zone,
                z.Borough as borough,
                COUNT(*) as trip_count
            FROM trips t
            JOIN zones z ON t.PULocationID = z.LocationID
            GROUP BY z.Zone, z.Borough
            ORDER BY trip_count DESC
            LIMIT 10
        """,
        'avg_fare_by_hour': """
            SELECT 
                pickup_hour,
                ROUND(AVG(fare_amount), 2) as avg_fare,
                COUNT(*) as trip_count
            FROM trips
            GROUP BY pickup_hour
            ORDER BY pickup_hour
        """,
        'payment_distribution': """
            SELECT 
                payment_method,
                COUNT(*) as trip_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 2) as percentage
            FROM trips
            GROUP BY payment_method
            ORDER BY trip_count DESC
        """,
        'tip_by_day': """
            SELECT 
                pickup_day_name as day_of_week,
                pickup_day_of_week as day_num,
                ROUND(AVG(tip_amount / NULLIF(fare_amount, 0) * 100), 2) as avg_tip_pct
            FROM trips
            WHERE payment_type = 1 AND fare_amount > 0
            GROUP BY pickup_day_name, pickup_day_of_week
            ORDER BY pickup_day_of_week
        """,
        'top_zone_pairs': """
            SELECT 
                pz.Zone as pickup_zone,
                dz.Zone as dropoff_zone,
                COUNT(*) as trip_count,
                ROUND(AVG(t.trip_distance), 2) as avg_distance,
                ROUND(AVG(t.total_amount), 2) as avg_total
            FROM trips t
            JOIN zones pz ON t.PULocationID = pz.LocationID
            JOIN zones dz ON t.DOLocationID = dz.LocationID
            GROUP BY pz.Zone, dz.Zone
            ORDER BY trip_count DESC
            LIMIT 5
        """
    }
    
    result = con.execute(queries[query_type]).fetchdf()
    con.close()
    return result

# =============================================================================
# Dashboard Layout
# =============================================================================

def main():
    # Title and Introduction
    st.title("🚕 NYC Yellow Taxi Trip Dashboard")
    st.markdown("""
    **COMP 3610: Big Data Analytics - Assignment 1**
    
    This interactive dashboard analyzes NYC Yellow Taxi trip data from **January 2024**, 
    containing approximately **3 million trip records**. Explore patterns in taxi usage, 
    fare trends, and popular pickup/dropoff locations across New York City.
    
    ---
    """)
    
    # Load Data
    with st.spinner("Loading and processing taxi trip data..."):
        df, zones_df = load_data()
    
    # ==========================================================================
    # Sidebar Filters
    # ==========================================================================
    st.sidebar.header("🔍 Filters")
    
    # Date Range Filter
    min_date = df['pickup_date'].min()
    max_date = df['pickup_date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Hour Range Filter
    hour_range = st.sidebar.slider(
        "Select Hour Range",
        min_value=0,
        max_value=23,
        value=(0, 23),
        step=1
    )
    
    # Payment Type Filter
    payment_types = df['payment_method'].unique().tolist()
    selected_payments = st.sidebar.multiselect(
        "Select Payment Types",
        options=payment_types,
        default=payment_types
    )
    
    # Apply Filters
    if len(date_range) == 2:
        mask = (
            (df['pickup_date'] >= date_range[0]) &
            (df['pickup_date'] <= date_range[1]) &
            (df['pickup_hour'] >= hour_range[0]) &
            (df['pickup_hour'] <= hour_range[1]) &
            (df['payment_method'].isin(selected_payments))
        )
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    st.sidebar.markdown(f"**Trips after filtering:** {len(filtered_df):,}")
    
    # ==========================================================================
    # Navigation Tabs
    # ==========================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview & Metrics",
        "📍 Location Analysis", 
        "💰 Fare & Payment Analysis",
        "📈 Temporal Patterns"
    ])
    
    # ==========================================================================
    # Tab 1: Overview & Metrics
    # ==========================================================================
    with tab1:
        st.header("Key Performance Metrics")
        
        # Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Trips",
                value=f"{len(filtered_df):,}"
            )
        
        with col2:
            st.metric(
                label="Average Fare",
                value=f"${filtered_df['fare_amount'].mean():.2f}"
            )
        
        with col3:
            st.metric(
                label="Total Revenue",
                value=f"${filtered_df['total_amount'].sum():,.0f}"
            )
        
        with col4:
            st.metric(
                label="Avg Distance",
                value=f"{filtered_df['trip_distance'].mean():.2f} mi"
            )
        
        with col5:
            st.metric(
                label="Avg Duration",
                value=f"{filtered_df['trip_duration_minutes'].mean():.1f} min"
            )
        
        st.markdown("---")
        
        # Trip Distance Distribution
        st.subheader("Trip Distance Distribution")
        
        fig_dist = px.histogram(
            filtered_df[filtered_df['trip_distance'] <= 30],
            x='trip_distance',
            nbins=50,
            title='Distribution of Trip Distances',
            labels={'trip_distance': 'Trip Distance (miles)', 'count': 'Number of Trips'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_dist.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Trip Distance (miles)",
            yaxis_title="Number of Trips"
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        
        st.info("""
        **💡 Insight:** The majority of taxi trips are short-distance journeys under 5 miles, 
        which is typical for urban transportation. The right-skewed distribution indicates 
        that while most trips are short, there are occasional longer trips, likely to airports 
        or outer boroughs.
        """)
    
    # ==========================================================================
    # Tab 2: Location Analysis
    # ==========================================================================
    with tab2:
        st.header("Pickup and Dropoff Location Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Pickup Zones
            st.subheader("Top 10 Busiest Pickup Zones")
            
            top_pickups = run_sql_query(filtered_df, zones_df, 'top_pickup_zones')
            
            fig_pickup = px.bar(
                top_pickups,
                x='pickup_zone',
                y='trip_count',
                color='borough',
                title='Top 10 Pickup Locations',
                labels={'pickup_zone': 'Zone', 'trip_count': 'Trips', 'borough': 'Borough'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pickup.update_layout(
                xaxis_tickangle=-45,
                height=450,
                showlegend=True,
                legend_title_text='Borough'
            )
            st.plotly_chart(fig_pickup, use_container_width=True)
        
        with col2:
            # Top Zone Pairs
            st.subheader("Most Common Trip Routes")
            
            zone_pairs = run_sql_query(filtered_df, zones_df, 'top_zone_pairs')
            zone_pairs['route'] = zone_pairs['pickup_zone'] + ' → ' + zone_pairs['dropoff_zone']
            
            fig_routes = px.bar(
                zone_pairs,
                x='trip_count',
                y='route',
                orientation='h',
                title='Top 5 Pickup-Dropoff Zone Pairs',
                labels={'route': 'Route', 'trip_count': 'Number of Trips'},
                color='avg_total',
                color_continuous_scale='Blues'
            )
            fig_routes.update_layout(
                height=450,
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_colorbar_title='Avg Fare'
            )
            st.plotly_chart(fig_routes, use_container_width=True)
        
        st.info("""
        **💡 Insight:** Manhattan dominates taxi pickups, with areas like Upper East Side, 
        Midtown, and Penn Station being the busiest. The most common routes are typically 
        within Manhattan, reflecting the borough's high population density and commercial activity.
        Many top routes connect transit hubs to residential or business districts.
        """)
    
    # ==========================================================================
    # Tab 3: Fare & Payment Analysis
    # ==========================================================================
    with tab3:
        st.header("Fare and Payment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Payment Type Distribution
            st.subheader("Payment Type Distribution")
            
            payment_dist = run_sql_query(filtered_df, zones_df, 'payment_distribution')
            
            fig_payment = px.pie(
                payment_dist,
                values='trip_count',
                names='payment_method',
                title='Payment Method Distribution',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_payment.update_traces(textposition='inside', textinfo='percent+label')
            fig_payment.update_layout(height=400)
            st.plotly_chart(fig_payment, use_container_width=True)
        
        with col2:
            # Tip Percentage by Day
            st.subheader("Average Tip % by Day (Credit Card)")
            
            tip_by_day = run_sql_query(filtered_df, zones_df, 'tip_by_day')
            
            fig_tip = px.bar(
                tip_by_day,
                x='day_of_week',
                y='avg_tip_pct',
                title='Average Tip Percentage by Day of Week',
                labels={'day_of_week': 'Day', 'avg_tip_pct': 'Tip %'},
                color='avg_tip_pct',
                color_continuous_scale='Greens'
            )
            fig_tip.update_layout(
                height=400,
                xaxis_tickangle=-45,
                showlegend=False
            )
            st.plotly_chart(fig_tip, use_container_width=True)
        
        st.info("""
        **💡 Insight:** Credit cards are overwhelmingly the preferred payment method in NYC taxis, 
        likely due to convenience and the prevalence of card-only payment systems. Tip percentages 
        remain relatively consistent throughout the week, hovering around 18-20%, which is typical 
        for service industries in New York.
        """)
        
        # Fare Distribution by Payment Type
        st.subheader("Fare Distribution by Payment Type")
        
        fig_fare_payment = px.box(
            filtered_df[filtered_df['fare_amount'] <= 100],
            x='payment_method',
            y='fare_amount',
            title='Fare Amount Distribution by Payment Type',
            labels={'payment_method': 'Payment Method', 'fare_amount': 'Fare ($)'},
            color='payment_method',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_fare_payment.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_fare_payment, use_container_width=True)
    
    # ==========================================================================
    # Tab 4: Temporal Patterns
    # ==========================================================================
    with tab4:
        st.header("Temporal Patterns Analysis")
        
        # Average Fare by Hour
        st.subheader("Average Fare by Hour of Day")
        
        fare_by_hour = run_sql_query(filtered_df, zones_df, 'avg_fare_by_hour')
        
        fig_hour = px.line(
            fare_by_hour,
            x='pickup_hour',
            y='avg_fare',
            title='Average Fare Throughout the Day',
            labels={'pickup_hour': 'Hour of Day', 'avg_fare': 'Average Fare ($)'},
            markers=True
        )
        fig_hour.update_layout(
            height=400,
            xaxis=dict(tickmode='linear', dtick=1)
        )
        st.plotly_chart(fig_hour, use_container_width=True)
        
        st.info("""
        **💡 Insight:** Average fares peak during early morning hours (4-6 AM), which typically 
        corresponds to airport trips and longer-distance travel. The afternoon and evening show 
        more moderate fares reflecting typical urban commuting patterns.
        """)
        
        # Heatmap: Trips by Day and Hour
        st.subheader("Trip Volume Heatmap: Day of Week vs Hour")
        
        heatmap_data = filtered_df.groupby(['pickup_day_of_week', 'pickup_hour']).size().reset_index(name='trips')
        heatmap_pivot = heatmap_data.pivot(index='pickup_day_of_week', columns='pickup_hour', values='trips').fillna(0)
        
        day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heatmap = px.imshow(
            heatmap_pivot.values,
            labels=dict(x='Hour of Day', y='Day of Week', color='Trip Count'),
            x=list(range(24)),
            y=day_labels,
            title='Trip Volume by Day and Hour',
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.info("""
        **💡 Insight:** The heatmap reveals clear patterns in taxi demand:
        - **Weekday Rush Hours:** Peak demand occurs during evening rush (5-7 PM) on weekdays
        - **Weekend Nights:** Friday and Saturday nights show elevated activity into late hours
        - **Early Morning Lull:** 3-5 AM consistently shows the lowest demand across all days
        - **Business Hours:** Steady demand throughout standard business hours on weekdays
        """)
        
        # Trips by Day of Week
        st.subheader("Trip Volume by Day of Week")
        
        daily_trips = filtered_df.groupby('pickup_day_name').size().reindex(day_labels).reset_index()
        daily_trips.columns = ['day', 'trips']
        
        fig_daily = px.bar(
            daily_trips,
            x='day',
            y='trips',
            title='Total Trips by Day of Week',
            labels={'day': 'Day', 'trips': 'Number of Trips'},
            color='trips',
            color_continuous_scale='Blues'
        )
        fig_daily.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # ==========================================================================
    # Footer
    # ==========================================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p><strong>COMP 3610: Big Data Analytics - Assignment 1</strong></p>
        <p>Data Source: NYC Taxi & Limousine Commission | January 2024</p>
        <p>Student ID: 816034871</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# Run Application
# =============================================================================
if __name__ == "__main__":
    main()
