"""
COMP 3610: Big Data Analytics - Assignment 1
Page 2: Visualizations - Interactive charts with user-driven filters

Student ID: 816034871
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils import load_data, load_zones, PAYMENT_TYPE_MAP

st.title("Interactive Visualizations")
st.markdown(
    "Five interactive charts built with **Plotly**, each responding to the "
    "filter controls below. Adjust the date range, hours, or payment types "
    "to slice the data in real time."
)

df = load_data()
zones = load_zones()

# ── Helpers ──────────────────────────────────────────────────────────────────

def apply_filters(df, start_date, end_date, hour_min, hour_max, payments):
    """Return a filtered copy of the dataframe."""
    mask = (
        (df['pickup_date'] >= start_date) &
        (df['pickup_date'] <= end_date) &
        (df['pickup_hour'] >= hour_min) &
        (df['pickup_hour'] <= hour_max)
    )
    filtered = df[mask]
    if payments:
        filtered = filtered[filtered['payment_type'].isin(payments)]
    else:
        filtered = filtered.head(0)
    return filtered


def top10_pickup(filtered, zones):
    """Top 10 pickup zones by trip count."""
    pu = filtered.groupby('PULocationID').size().reset_index(name='trip_count')
    pu = pu.merge(
        zones[['LocationID', 'Zone', 'Borough']],
        left_on='PULocationID', right_on='LocationID', how='left',
    )
    pu['label'] = pu['Borough'].fillna('') + ' — ' + pu['Zone'].fillna('')
    return pu.nlargest(10, 'trip_count')


# ── Filter panel (main-area expander, NOT sidebar) ───────────────────────────
payment_codes = sorted(df['payment_type'].dropna().unique().astype(int).tolist())
payment_labels = [f"{c} – {PAYMENT_TYPE_MAP.get(c, 'Other')}" for c in payment_codes]

jan_start = date(2024, 1, 1)
jan_end   = date(2024, 1, 31)

with st.expander("\U0001F50D  **Filter Controls**", expanded=False):
    fc1, fc2 = st.columns(2)
    with fc1:
        date_range = st.date_input(
            "Pickup date range",
            value=(jan_start, jan_end),
            min_value=jan_start,
            max_value=jan_end,
        )
        hour_range = st.slider("Hour window", 0, 23, (0, 23))
    with fc2:
        selected_labels = st.multiselect(
            "Payment types", options=payment_labels, default=payment_labels,
        )
        dist_cap = st.slider("Max trip distance shown (mi)", 5, 100, 50)

    apply_btn = st.button("Apply filters", type="primary", use_container_width=True)

# Persist applied filters across re-renders
if "vis_filters" not in st.session_state:
    st.session_state.vis_filters = {
        "date_range": (jan_start, jan_end),
        "hour_range": (0, 23),
        "payments": payment_labels,
        "dist_cap": 50,
    }

if apply_btn:
    st.session_state.vis_filters = {
        "date_range": date_range,
        "hour_range": hour_range,
        "payments": selected_labels,
        "dist_cap": dist_cap,
    }

af = st.session_state.vis_filters
selected_payments = [int(lbl.split(" – ")[0]) for lbl in af["payments"]]

filtered = apply_filters(
    df, af["date_range"][0], af["date_range"][1],
    af["hour_range"][0], af["hour_range"][1],
    selected_payments,
)

if len(filtered) == 0:
    st.warning("No trips match the current filters — try widening the criteria.")
    st.stop()

st.caption(f"Showing **{len(filtered):,}** trips after filtering.")

# Cap for performance
MAX_VIS = 300_000
if len(filtered) > MAX_VIS:
    st.info(f"Sampling {MAX_VIS:,} of {len(filtered):,} rows for rendering speed.")
    filtered = filtered.sample(n=MAX_VIS, random_state=42)

st.divider()

# ── Chart 1: Top 10 Pickup Zones ─────────────────────────────────────────────
st.markdown("#### 1 · Busiest Pickup Zones")

top10 = top10_pickup(filtered, zones)
fig1 = go.Figure([go.Bar(
    x=top10['label'].tolist(),
    y=top10['trip_count'].tolist(),
    marker_color='#636EFA',
)])
fig1.update_layout(
    xaxis_title="Zone", yaxis_title="Trip Count",
    xaxis_tickangle=-40, height=480,
)
st.plotly_chart(fig1, use_container_width=True)
st.caption(
    "Manhattan's core commercial districts — particularly Midtown and the Upper East Side — "
    "generate the highest pickup volumes. Airport zones (JFK, LaGuardia) also rank among "
    "the top ten, highlighting the significance of air-travel demand for taxi services."
)

st.divider()

# ── Chart 2: Average Fare by Hour ─────────────────────────────────────────────
st.markdown("#### 2 · Hourly Fare Pattern")

hourly = filtered.groupby('pickup_hour')['fare_amount'].mean().reset_index()
hourly.columns = ['hour', 'avg_fare']
hourly = hourly.sort_values('hour')

fig2 = go.Figure([go.Scatter(
    x=hourly['hour'].tolist(),
    y=hourly['avg_fare'].tolist(),
    mode='lines+markers',
    line=dict(color='#EF553B'),
)])
fig2.update_layout(
    xaxis_title="Hour of Day", yaxis_title="Avg Fare ($)",
    height=400,
)
st.plotly_chart(fig2, use_container_width=True)
st.caption(
    "Fares are notably higher around 5–6 AM, likely reflecting longer airport-bound trips "
    "before rush hour. The lowest averages appear during the 2–4 AM window, when both demand "
    "and trip lengths drop. A gradual evening uptick aligns with post-work and nightlife travel."
)

st.divider()

# ── Chart 3: Trip Distance Distribution ───────────────────────────────────────
st.markdown("#### 3 · Trip Distance Spread")

bin_width = 0.5
dist_sub = filtered[filtered['trip_distance'] <= af["dist_cap"]].copy()
dist_sub['bin'] = (dist_sub['trip_distance'] / bin_width).astype(int) * bin_width
hist = dist_sub.groupby('bin').size().reset_index(name='count')

fig3 = go.Figure([go.Bar(
    x=hist['bin'].tolist(), y=hist['count'].tolist(),
    marker_color='#00CC96',
)])
fig3.update_layout(
    xaxis_title="Distance (miles)", yaxis_title="Trip Count",
    height=400,
)
st.plotly_chart(fig3, use_container_width=True)
st.caption(
    "The distribution is heavily right-skewed: most rides cover fewer than 5 miles, "
    "consistent with intra-borough commuting. Longer trips taper off quickly, with sporadic "
    "outliers representing airport transfers or cross-borough journeys."
)

st.divider()

# ── Chart 4: Payment Breakdown ────────────────────────────────────────────────
st.markdown("#### 4 · Payment Method Mix")

pay = filtered.groupby('payment_method').size().reset_index(name='trips')
pay = pay.sort_values('trips', ascending=False)

fig4 = go.Figure([go.Pie(
    labels=pay['payment_method'].tolist(),
    values=pay['trips'].tolist(),
    hole=0.35,
    marker_colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3'],
)])
fig4.update_layout(height=420)
st.plotly_chart(fig4, use_container_width=True)
st.caption(
    "Credit-card transactions dominate at roughly 80 % of all rides, underscoring  "
    "the cashless trend in NYC taxis. Cash makes up the bulk of the remainder, while  "
    "disputes and no-charge trips are statistically negligible."
)

st.divider()

# ── Chart 5: Day × Hour Heatmap ──────────────────────────────────────────────
st.markdown("#### 5 · Weekly Demand Heatmap")

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dh = filtered.groupby(['pickup_day_of_week', 'pickup_hour']).size().reset_index(name='trips')
hours = list(range(24))
lookup = {(r['pickup_day_of_week'], r['pickup_hour']): r['trips'] for _, r in dh.iterrows()}
z = [[lookup.get((d, h), 0) for h in hours] for d in day_order]

fig5 = go.Figure(data=go.Heatmap(
    z=z, x=hours, y=day_order,
    colorscale='Viridis',
))
fig5.update_layout(
    xaxis_title="Hour of Day", yaxis_title="Day",
    height=420,
)
st.plotly_chart(fig5, use_container_width=True)
st.caption(
    "Weekday mornings (8–9 AM) and late afternoons (4–6 PM) display the sharpest demand spikes, "
    "mirroring typical commute windows. Weekend activity shifts later into the evening — "
    "especially on Fridays and Saturdays — while the 2–5 AM slot is consistently the quietest."
)
