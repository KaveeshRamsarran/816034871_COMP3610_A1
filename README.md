# COMP 3610: Big Data Analytics - Assignment 1
## NYC Yellow Taxi Trip Data Pipeline & Visualization Dashboard

**Student ID:** 816034871  
**Course:** COMP 3610 - Big Data Analytics  
**Due Date:** February 20, 2026

---

## 📋 Project Overview

This project implements an end-to-end data pipeline that ingests, transforms, and analyzes the **NYC Yellow Taxi Trip dataset** (~3 million records from January 2024), culminating in an **interactive visualization dashboard** deployed on Streamlit Community Cloud.

### 🔗 Live Dashboard
[View the deployed dashboard here](https://your-app-name.streamlit.app) *(Update with your deployed URL)*

---

## 📁 Repository Structure

```
816034871_COMP3610_A1/
├── assignment1.ipynb    # Jupyter notebook (Parts 1, 2, 3 prototypes)
├── app.py               # Streamlit dashboard application
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation (this file)
├── .gitignore           # Git ignore rules (excludes data/)
└── data/                # Data directory (not committed)
    ├── raw/             # Downloaded raw data files
    └── processed/       # Cleaned and transformed data
```

---

## 🗃️ Dataset

### Primary Dataset
- **NYC Yellow Taxi Trip Data (January 2024)**
- Source: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- URL: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
- Records: ~3 million trips
- Format: Parquet

### Reference Dataset
- **Taxi Zone Lookup Table**
- URL: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
- Contains zone names and boroughs for location IDs

---

## 🛠️ Technologies Used

| Category | Technology |
|----------|------------|
| **Data Processing** | Python, Pandas, PyArrow |
| **Database/SQL** | DuckDB |
| **Visualization** | Plotly |
| **Dashboard** | Streamlit |
| **Deployment** | Streamlit Community Cloud |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/816034871_COMP3610_A1.git
   cd 816034871_COMP3610_A1
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Jupyter Notebook**
   ```bash
   jupyter notebook assignment1.ipynb
   ```

5. **Run the Streamlit Dashboard**
   ```bash
   streamlit run app.py
   ```
   The dashboard will open at `http://localhost:8501`

---

## 📊 Assignment Components

### Part 1: Data Ingestion & Storage (20 marks)

- ✅ **Programmatic Download** (5 marks)
  - Downloads Parquet and CSV files using Python `requests` library
  - Progress tracking and error handling

- ✅ **Data Validation** (10 marks)
  - Verifies expected columns exist
  - Validates datetime types
  - Reports row counts
  - Raises exceptions on validation failure

- ✅ **File Organization** (5 marks)
  - Data saved to `data/raw/` directory
  - `.gitignore` excludes data directory

### Part 2: Data Transformation & Analysis (30 marks)

- ✅ **Data Cleaning** (10 marks)
  - Removes null values in critical columns
  - Filters invalid trips (zero/negative distance, fare, duration)
  - Documents all removals with statistics

- ✅ **Feature Engineering** (10 marks)
  - `trip_duration_minutes`: Trip duration in minutes
  - `trip_speed_mph`: Average speed in MPH
  - `pickup_hour`: Hour of pickup (0-23)
  - `pickup_day_of_week`: Day of week (0=Monday)

- ✅ **SQL Analysis with DuckDB** (10 marks)
  1. Top 10 busiest pickup zones
  2. Average fare by hour of day
  3. Payment type distribution (percentages)
  4. Average tip percentage by day (credit card only)
  5. Top 5 pickup-dropoff zone pairs

### Part 3: Visualization Dashboard (40 marks)

- ✅ **Dashboard Structure** (5 marks)
  - Clear title and introduction
  - Tab-based navigation (Overview, Locations, Payments, Temporal)

- ✅ **Key Metrics** (5 marks)
  - Total trips
  - Average fare
  - Total revenue
  - Average distance
  - Average duration

- ✅ **5 Visualizations** (20 marks)
  1. Bar chart: Top 10 pickup zones by borough
  2. Line chart: Average fare by hour
  3. Histogram: Trip distance distribution
  4. Pie chart: Payment type distribution
  5. Heatmap: Trips by day and hour

- ✅ **Interactive Filters** (5 marks)
  - Date range selector
  - Hour range slider
  - Payment type multi-select dropdown

- ✅ **Insights** (5 marks)
  - Each visualization includes 2-3 sentences of interpretation

### Part 4: Documentation & Code Quality (10 marks)

- ✅ Notebook documentation with markdown cells
- ✅ Clean, well-commented code
- ✅ Proper repository organization

---

## 🌐 Deployment to Streamlit Cloud

### Step-by-Step Deployment Guide

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit - Assignment 1"
   git push origin main
   ```

2. **Go to Streamlit Community Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click "New app"
   - Select your repository: `816034871_COMP3610_A1`
   - Set main file path: `app.py`
   - Click "Deploy!"

4. **Wait for deployment**
   - Streamlit will install dependencies and launch your app
   - This may take 2-5 minutes on first deployment

5. **Get your public URL**
   - Your app will be available at: `https://your-app-name.streamlit.app`
   - Update this README with your actual URL

---

## 📈 Key Findings

### Trip Patterns
- **Peak Hours:** Evening rush hour (5-7 PM) shows highest demand
- **Busiest Day:** Weekdays see more consistent traffic than weekends
- **Late Night:** Friday and Saturday nights have elevated late-night activity

### Location Insights
- **Manhattan Dominance:** Top pickup zones are concentrated in Manhattan
- **Common Routes:** Most trips are short-distance within Manhattan
- **Transit Hubs:** Penn Station, Grand Central areas are major pickup points

### Payment Analysis
- **Credit Card Preferred:** Vast majority of payments are by credit card
- **Consistent Tipping:** Average tip percentages hover around 18-20%
- **Cash Declining:** Cash payments represent a small minority

---

## 📚 References

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Plotly Python Documentation](https://plotly.com/python/)

---

## 👤 Contact

- **Student:** 816034871
- **Course:** COMP 3610 - Big Data Analytics
- **Lecturer:** Mr. Sergio Mathurin (sergio.mathurin@uwi.edu)
- **Tutor:** Mr. Anton Greenridge (anton.greenridge@my.uwi.edu)

---

*This project was completed as part of COMP 3610: Big Data Analytics at The University of the West Indies.*
