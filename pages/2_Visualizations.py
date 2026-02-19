"""
COMP 3610: Big Data Analytics - Assignment 1
Page 2: Visualizations - Interactive charts with filters

Student ID: 816034871
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils import load_data, load_zones, PAYMENT_TYPE_MAP

st.title("Visualizations")

df = load_data()
zones = load_zones()

# =============================================================================
# Helper Functions
# =============================================================================

def apply_filters(df, start_date, end_date, hour_min, hour_max, payments):
    """Filter dataset by date range, hour range, and payment types."""
    filtered = df[
        (df['pickup_date'] >= start_date) &
        (df['pickup_date'] <= end_date) &
        (df['pickup_hour'] >= hour_min) &
        (df['pickup_hour'] <= hour_max)
    ]
    
    if payments:
        filtered = filtered[filtered['payment_type'].isin(payments)]
    else:
        filtered = filtered.head(0)
    
    return filtered


def top10_pickup(filtered, zones):
    """Get top 10 pickup zones by trip count."""
    pickup_counts = filtered.groupby('PULocationID').size().reset_index(name='trip_count')
    pickup_counts = pickup_counts.merge(
        zones[['LocationID', 'Zone', 'Borough']], 
        left_on='PULocationID', 
        right_on='LocationID', 
        how='left'
    )
    pickup_counts['pickup_zone_label'] = pickup_counts['Borough'] + ' - ' + pickup_counts['Zone']
    return pickup_counts.nlargest(10, 'trip_count')


# =============================================================================
# Sidebar Filters
# =============================================================================
st.sidebar.header("Filters")

# Payment type labels
payment_codes = sorted(df['payment_type'].dropna().unique().astype(int).tolist())
payment_labels = [f"{code} - {PAYMENT_TYPE_MAP.get(code, 'Other')}" for code in payment_codes]

# Date range
jan_start = date(2024, 1, 1)
jan_end = date(2024, 1, 31)

with st.sidebar.form("filters_form"):
    date_range = st.date_input(
        "Pickup date range (January 2024 only)",
        value=(jan_start, jan_end),
        min_value=jan_start,
        max_value=jan_end,
    )
    
    hour_range = st.slider("Pickup hour range", 0, 23, (0, 23))
    
    selected_labels = st.multiselect(
        "Payment type",
        options=payment_labels,
        default=payment_labels,
    )
    
    dist_cap = st.slider("Max distance to display (miles)", 5, 100, 50)
    
    apply_btn = st.form_submit_button("Apply filters")

# Initialize applied filters
if "applied_filters" not in st.session_state:
    st.session_state.applied_filters = {
        "date_range": (jan_start, jan_end),
        "hour_range": (0, 23),
        "payments": payment_labels,
        "dist_cap": 50,
    }

# When user clicks Apply, save filters
if apply_btn:
    st.session_state.applied_filters = {
        "date_range": date_range,
        "hour_range": hour_range,
        "payments": selected_labels,
        "dist_cap": dist_cap,
    }

# Use saved filters
applied = st.session_state.applied_filters
date_range = applied["date_range"]
hour_range = applied["hour_range"]
selected_labels = applied["payments"]
dist_cap = applied["dist_cap"]

# Extract payment codes from labels
selected_payments = [int(lbl.split(" - ")[0]) for lbl in selected_labels]

# Apply filters
filtered = apply_filters(
    df,
    date_range[0],
    date_range[1],
    hour_range[0],
    hour_range[1],
    selected_payments,
)

if len(filtered) == 0:
    st.warning("No trips match your selected filters. Try widening the date range or hours.")
    st.stop()

st.sidebar.caption(f"Filtered trips: {len(filtered):,}")

# Limit data for visualization performance
MAX_ROWS = 300_000
if len(filtered) > MAX_ROWS:
    st.warning(
        f"Large result ({len(filtered):,} rows). "
        f"Sampling {MAX_ROWS:,} rows for visualization."
    )
    filtered = filtered.sample(n=MAX_ROWS, random_state=42)

st.divider()

# =============================================================================
# Visualization 1: Top 10 Pickup Zones
# =============================================================================
st.subheader("Top 10 Pickup Zones by Trip Count")

top10_pu = top10_pickup(filtered, zones)

fig_r = go.Figure([go.Bar(
    x=top10_pu['pickup_zone_label'].tolist(),
    y=top10_pu['trip_count'].tolist()
)])
fig_r.update_layout(
    title="Top 10 Pickup Zones",
    xaxis_title="Pickup Zone",
    yaxis_title="Trips",
    xaxis_tickangle=-35,
)
st.plotly_chart(fig_r, use_container_width=True)

st.caption(
    "Midtown Manhattan and Upper East Side zones dominate pickup activity, indicating strong demand "
    "in central business and residential areas. JFK and LaGuardia Airport also appear in the top 10, "
    "confirming that airport traffic is a major contributor to total NYC taxi volume."
)

st.divider()

# =============================================================================
# Visualization 2: Average Fare by Hour of Day
# =============================================================================
st.subheader("Average Fare by Hour of Day")

avg_fare_by_hour = filtered.groupby('pickup_hour')['fare_amount'].mean().reset_index()
avg_fare_by_hour.columns = ['pickup_hour', 'avg_fare']
avg_fare_by_hour = avg_fare_by_hour.sort_values('pickup_hour')

fig_s = go.Figure([go.Scatter(
    x=avg_fare_by_hour['pickup_hour'].tolist(),
    y=avg_fare_by_hour['avg_fare'].tolist(),
    mode="lines+markers"
)])
fig_s.update_layout(
    title="Average Fare by Hour",
    xaxis_title="Hour of Day",
    yaxis_title="Average Fare ($)",
)
st.plotly_chart(fig_s, use_container_width=True)

st.caption(
    "Average fares spike sharply around 5 AM, likely reflecting airport trips or longer early-morning rides. "
    "Fares are lowest between 2–4 AM, when demand and trip distances are typically shorter. "
    "A moderate increase in the evening suggests higher pricing during post-work and nightlife hours."
)

st.divider()

# =============================================================================
# Visualization 3: Trip Distance Distribution
# =============================================================================
st.subheader("Distribution of Trip Distances")

bin_size = 0.5
dist_filtered = filtered[filtered['trip_distance'] <= dist_cap].copy()
dist_filtered['bin'] = (dist_filtered['trip_distance'] / bin_size).astype(int) * bin_size

hist_data = dist_filtered.groupby('bin').size().reset_index(name='count')

fig_t = go.Figure([go.Bar(
    x=hist_data['bin'].tolist(),
    y=hist_data['count'].tolist()
)])
fig_t.update_layout(
    title=f"Trip Distance Distribution (0–{dist_cap} miles)",
    xaxis_title="Distance bin (miles)",
    yaxis_title="Trips",
)
st.plotly_chart(fig_t, use_container_width=True)

st.caption(
    "The vast majority of taxi trips are short-distance rides under 5 miles, indicating that taxis are "
    "primarily used for local travel within boroughs. The long right tail shows that longer trips do occur "
    "but are relatively rare, likely representing airport or inter-borough travel."
)

st.divider()

# =============================================================================
# Visualization 4: Payment Type Breakdown
# =============================================================================
st.subheader("Payment Type Breakdown")

pay_breakdown = filtered.groupby('payment_method').size().reset_index(name='trips')
pay_breakdown['percent'] = (pay_breakdown['trips'] / pay_breakdown['trips'].sum() * 100).round(2)
pay_breakdown = pay_breakdown.sort_values('trips', ascending=False)

fig_u = go.Figure([go.Pie(
    labels=pay_breakdown['payment_method'].tolist(),
    values=pay_breakdown['trips'].tolist()
)])
fig_u.update_layout(title="Payment Type Share")
st.plotly_chart(fig_u, use_container_width=True)

st.caption(
    "Credit card payments account for roughly 80% of all trips, showing a strong shift toward digital payments "
    "in NYC taxis. Cash represents a much smaller share, while disputes and no-charge trips are extremely rare. "
    "This suggests modern taxi usage is largely cashless."
)

st.divider()

# =============================================================================
# Visualization 5: Heatmap - Trips by Day of Week and Hour
# =============================================================================
st.subheader("Trips by Day of Week and Hour (Heatmap)")

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

dow_hour = filtered.groupby(['pickup_day_name', 'pickup_hour']).size().reset_index(name='trips')

hours = list(range(24))
lookup = {(r['pickup_day_name'], r['pickup_hour']): r['trips'] for _, r in dow_hour.iterrows()}

z = [[lookup.get((d, h), 0) for h in hours] for d in day_order]

fig_v = go.Figure(data=go.Heatmap(z=z, x=hours, y=day_order, colorscale='Blues'))
fig_v.update_layout(
    title="Trips by Day of Week and Hour",
    xaxis_title="Hour of Day",
    yaxis_title="Day of Week",
)
st.plotly_chart(fig_v, use_container_width=True)

st.caption(
    "Weekdays show clear commuting peaks in the morning around 8–9 AM and late afternoon around 4–6 PM, "
    "reflecting work-related travel. Weekend demand shifts toward later hours, particularly Friday and Saturday "
    "evenings, likely driven by social and nightlife activity. Early morning hours consistently show the lowest "
    "activity across all days."
)
