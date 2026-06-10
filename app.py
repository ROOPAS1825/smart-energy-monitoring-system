import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

# Set page config
st.set_page_config(
    page_title="SEMS | Smart Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Main font styling */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* Metric card container styling */
.metric-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    text-align: center;
    margin-bottom: 15px;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.35);
    border-color: rgba(255, 255, 255, 0.2);
}

.metric-title {
    font-size: 0.85rem;
    color: #b0b0b0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ff9800;
    line-height: 1.2;
}

.metric-subtitle {
    font-size: 0.8rem;
    color: #4caf50;
    margin-top: 8px;
    font-weight: 500;
}

.metric-subtitle-red {
    font-size: 0.8rem;
    color: #f44336;
    margin-top: 8px;
    font-weight: 500;
}

.metric-subtitle-blue {
    font-size: 0.8rem;
    color: #2196f3;
    margin-top: 8px;
    font-weight: 500;
}

/* Header style styling */
.main-header {
    background: linear-gradient(135deg, #1f4068, #162447);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
}

.header-subtitle {
    font-size: 1rem;
    color: #00adb5;
    margin: 5px 0 0 0;
}

/* Alert/insight box styling */
.insight-box {
    background: rgba(0, 173, 181, 0.1);
    border-left: 5px solid #00adb5;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    color: #e3f6f5;
}

.insight-box-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 5px;
    color: #00adb5;
}

/* Light theme overrides */
@media (prefers-color-scheme: light) {
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        color: #222222;
    }
    .metric-value {
        color: #e65100;
    }
    .metric-title {
        color: #555555;
    }
    .main-header {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .header-title {
        color: #0d47a1;
    }
    .header-subtitle {
        color: #1565c0;
    }
    .insight-box {
        background: rgba(21, 101, 192, 0.08);
        border-left: 5px solid #1565c0;
        color: #222222;
    }
    .insight-box-title {
        color: #1565c0;
    }
}
</style>
""", unsafe_allow_html=True)

# Synthetic data generator
@st.cache_data
def generate_energy_data(days=30):
    np.random.seed(42)
    end_date = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - datetime.timedelta(days=days)
    timestamps = pd.date_range(start=start_date, end=end_date, freq='h')
    
    data = []
    for ts in timestamps:
        hour = ts.hour
        day_name = ts.strftime('%A')
        is_weekend = ts.weekday() in [5, 6]
        
        # Base temperature cycle (higher in afternoon, lower in early morning)
        base_temp = 72 # F
        temp_variation = 12 * np.sin((hour - 6) / 24 * 2 * np.pi)
        temperature = base_temp + temp_variation + np.random.normal(0, 1.5)
        
        # Base Load (fridge, stand-by, etc.): constant cycling + small noise
        fridge = 0.15 + 0.03 * np.sin(hour * np.pi / 2) + np.random.normal(0, 0.01)
        fridge = max(0.05, fridge)
        
        # HVAC: depends on temperature deviation from 72F
        hvac_base = 0.2
        cooling_load = max(0, (temperature - 74) * 0.08) if temperature > 74 else 0
        heating_load = max(0, (68 - temperature) * 0.05) if temperature < 68 else 0
        hvac = hvac_base + cooling_load + heating_load + np.random.normal(0, 0.04)
        
        # HVAC away mode on weekday working hours
        if not is_weekend and (9 <= hour <= 17):
            hvac *= 0.6
        elif (23 <= hour or hour <= 5):
            hvac *= 0.8  # sleep mode
        hvac = max(0.1, hvac)
        
        # Lighting: high in evening (6 PM - 11 PM), moderate morning (6 AM - 8 AM)
        if 18 <= hour <= 22:
            lighting = 0.25 + np.random.normal(0, 0.02)
        elif 6 <= hour <= 8:
            lighting = 0.10 + np.random.normal(0, 0.01)
        elif 23 <= hour or hour <= 5:
            lighting = 0.02 + np.random.normal(0, 0.005)
        else:
            lighting = 0.01
        lighting = max(0.0, lighting)
        
        # EV Charger: high load (1.5 kW), active on Mon, Wed, Fri night starting at 8 PM for 4 hours
        ev = 0.0
        if ts.weekday() in [0, 2, 4] and (20 <= hour <= 23):
            ev = 1.4 + np.random.normal(0, 0.05)
            
        # Laundry (Washer/Dryer): active mostly on weekends daytime or weekday evening
        laundry = 0.0
        if is_weekend and (10 <= hour <= 15):
            if np.random.rand() < 0.4:
                laundry = 1.2 + np.random.normal(0, 0.1)
        elif not is_weekend and (19 <= hour <= 20):
            if np.random.rand() < 0.2:
                laundry = 1.0 + np.random.normal(0, 0.1)
                
        # Entertainment & Cooking (others): active evening (5 PM - 10 PM) and lunch time (12 PM - 1 PM)
        other = 0.05
        if 17 <= hour <= 21:
            other += 0.35 + np.random.normal(0, 0.04)
        elif 12 <= hour <= 13:
            other += 0.15 + np.random.normal(0, 0.02)
        elif 7 <= hour <= 8:
            other += 0.10 + np.random.normal(0, 0.02)
        other += np.random.normal(0, 0.02)
        other = max(0.01, other)
        
        # Total
        total = fridge + hvac + lighting + ev + laundry + other
        
        data.append({
            'timestamp': ts,
            'Total (kWh)': round(total, 3),
            'HVAC (kWh)': round(hvac, 3),
            'Refrigerator (kWh)': round(fridge, 3),
            'Lighting (kWh)': round(lighting, 3),
            'EV Charger (kWh)': round(ev, 3),
            'Laundry (kWh)': round(laundry, 3),
            'Other (kWh)': round(other, 3),
            'Temperature (°F)': round(temperature, 1),
            'Hour': hour,
            'Day of Week': day_name,
            'Is Weekend': is_weekend,
            'Date': ts.date()
        })
        
    return pd.DataFrame(data)

# Helper function to parse user uploaded energy data
def parse_uploaded_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Search for timestamp column
        ts_col = None
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower() or 'ts' in col.lower():
                ts_col = col
                break
        
        if ts_col is None:
            st.error("Could not find a timestamp column (e.g. 'time', 'date', 'timestamp') in the uploaded file.")
            return None
            
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df[ts_col])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Search for consumption column
        energy_col = None
        for col in df.columns:
            if 'kwh' in col.lower() or 'energy' in col.lower() or 'consumption' in col.lower() or 'usage' in col.lower() or 'power' in col.lower():
                energy_col = col
                break
        
        if energy_col is None:
            st.error("Could not find an energy consumption column (e.g. 'kwh', 'energy', 'consumption') in the uploaded file.")
            return None
            
        # Standardize columns
        df['Total (kWh)'] = pd.to_numeric(df[energy_col], errors='coerce')
        df['Hour'] = df['timestamp'].dt.hour
        df['Day of Week'] = df['timestamp'].dt.strftime('%A')
        df['Is Weekend'] = df['timestamp'].dt.weekday.isin([5, 6])
        df['Date'] = df['timestamp'].dt.date
        
        # Fill missing subcomponents if not present, to keep UI functional
        appliances = {
            'HVAC (kWh)': 0.40,
            'Refrigerator (kWh)': 0.12,
            'Lighting (kWh)': 0.15,
            'EV Charger (kWh)': 0.18,
            'Laundry (kWh)': 0.08,
            'Other (kWh)': 0.07
        }
        for app, pct in appliances.items():
            if app not in df.columns:
                df[app] = (df['Total (kWh)'] * pct).round(3)
                
        if 'Temperature (°F)' not in df.columns:
            # Generate fake temperature based on hour
            df['Temperature (°F)'] = 72 + 12 * np.sin((df['Hour'] - 6) / 24 * 2 * np.pi)
            
        return df
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return None

# Sidebar - Settings and Controls
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #ff9800; font-weight: 800; margin-bottom: 0;">⚡ SEMS</h2>
    <p style="color: #888888; font-size: 0.9rem; margin-top: 0;">Smart Energy Monitoring System</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("📂 Data Source")
data_source = st.sidebar.radio("Select Data Source:", ["Synthetic Demo Data", "Upload Energy CSV"])

# Load data based on source
raw_df = None
if data_source == "Synthetic Demo Data":
    days_to_gen = st.sidebar.slider("Days of historical data to generate:", min_value=7, max_value=90, value=30, step=7)
    raw_df = generate_energy_data(days=days_to_gen)
    st.sidebar.success(f"✓ Generated {days_to_gen} days of demo data.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload consumption CSV:", type=["csv"])
    if uploaded_file is not None:
        raw_df = parse_uploaded_file(uploaded_file)
        if raw_df is not None:
            st.sidebar.success("✓ Successfully loaded custom CSV data.")
    else:
        st.sidebar.warning("Please upload a CSV file. Falling back to 30 days of demo data.")
        raw_df = generate_energy_data(days=30)

# Apply filters
if raw_df is not None:
    min_date = raw_df['Date'].min()
    max_date = raw_df['Date'].max()
    
    st.sidebar.header("🗓️ Filter Period")
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter DataFrame
    df = raw_df[(raw_df['Date'] >= start_date) & (raw_df['Date'] <= end_date)].copy()
    
    # Electricity Pricing Config
    st.sidebar.header("💰 Tariff & Rate Settings")
    tariff_type = st.sidebar.selectbox("Pricing Model:", ["Flat Rate", "Time-of-Use (TOU)"])
    
    if tariff_type == "Flat Rate":
        flat_rate = st.sidebar.number_input("Flat Rate ($/kWh):", min_value=0.01, max_value=1.00, value=0.15, step=0.01)
        # Calculate cost
        df['Cost ($)'] = df['Total (kWh)'] * flat_rate
    else:
        st.sidebar.markdown("*Define Peak hours and rates*")
        peak_rate = st.sidebar.number_input("Peak Rate ($/kWh):", min_value=0.01, max_value=1.00, value=0.28, step=0.01)
        off_peak_rate = st.sidebar.number_input("Off-Peak Rate ($/kWh):", min_value=0.01, max_value=1.00, value=0.11, step=0.01)
        
        peak_start_hour = st.sidebar.slider("Peak Hours Start (Hour):", min_value=0, max_value=23, value=17) # 5 PM
        peak_end_hour = st.sidebar.slider("Peak Hours End (Hour):", min_value=0, max_value=23, value=21) # 9 PM
        
        # Cost helper
        def calculate_tou_cost(row):
            h = row['Hour']
            # If peak span crosses midnight (e.g. 22:00 to 2:00)
            if peak_start_hour <= peak_end_hour:
                is_peak = peak_start_hour <= h <= peak_end_hour
            else:
                is_peak = h >= peak_start_hour or h <= peak_end_hour
                
            rate = peak_rate if is_peak else off_peak_rate
            return row['Total (kWh)'] * rate
            
        df['Is Peak Hour'] = df['Hour'].apply(
            lambda h: (peak_start_hour <= h <= peak_end_hour) if peak_start_hour <= peak_end_hour 
            else (h >= peak_start_hour or h <= peak_end_hour)
        )
        df['Cost ($)'] = df.apply(calculate_tou_cost, axis=1)

    # Main Page Header
    st.markdown(f"""
    <div class="main-header">
        <div>
            <h1 class="header-title">⚡ Energy Usage Analysis Dashboard</h1>
            <p class="header-subtitle">Visualize historical patterns, identify peak usage periods, and simulate savings.</p>
        </div>
        <div style="text-align: right; color: #888888; font-size: 0.9rem;">
            <div>Active Period: <b>{start_date.strftime('%b %d, %Y')}</b> to <b>{end_date.strftime('%b %d, %Y')}</b></div>
            <div>Pricing Model: <b>{tariff_type}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pre-calculate main values
    total_consumption = df['Total (kWh)'].sum()
    total_cost = df['Cost ($)'].sum()
    avg_hourly = df['Total (kWh)'].mean()
    
    # Calculate Peak hour of day
    hourly_avg = df.groupby('Hour')['Total (kWh)'].mean().reset_index()
    peak_row = hourly_avg.loc[hourly_avg['Total (kWh)'].idxmax()]
    peak_hour = int(peak_row['Hour'])
    peak_val = peak_row['Total (kWh)']
    
    # Format hour display
    def format_hour(h):
        if h == 0: return "12:00 AM"
        elif h < 12: return f"{h}:00 AM"
        elif h == 12: return "12:00 PM"
        else: return f"{h-12}:00 PM"
        
    peak_hour_str = format_hour(peak_hour)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚡ Total Consumption</div>
            <div class="metric-value">{total_consumption:,.1f} <span style="font-size: 1.1rem; font-weight: 500; color: #888;">kWh</span></div>
            <div class="metric-subtitle">Across Selected Period</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💵 Estimated Bill</div>
            <div class="metric-value">${total_cost:,.2f}</div>
            <div class="metric-subtitle">Tariff: {tariff_type}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📉 Average Hourly Load</div>
            <div class="metric-value">{avg_hourly:.2f} <span style="font-size: 1.1rem; font-weight: 500; color: #888;">kWh</span></div>
            <div class="metric-subtitle-blue">Typical Base + Active Demand</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🔥 Daily Peak Hour</div>
            <div class="metric-value" style="color: #ff5722;">{peak_hour_str}</div>
            <div class="metric-subtitle-red">Highest average usage ({peak_val:.2f} kWh)</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview & Trends", 
        "🔥 Peak Hour Analysis", 
        "🔌 Appliance Breakdown", 
        "💡 Shift & Save Simulator",
        "📋 Conservation Recommendations"
    ])
    
    # Tab 1: Overview & Trends
    with tab1:
        st.subheader("Historical Energy Consumption Trends")
        st.write("View how your electricity usage changes over time. Double-click on the charts or zoom in to examine specific days.")
        
        # Group data by day for daily chart
        daily_df = df.groupby('Date').agg({
            'Total (kWh)': 'sum',
            'Cost ($)': 'sum',
            'Temperature (°F)': 'mean'
        }).reset_index()
        
        daily_df['Date_Str'] = daily_df['Date'].astype(str)
        
        # Daily Consumption Chart
        base = alt.Chart(daily_df).encode(x=alt.X('Date_Str:T', title='Date'))
        
        bar = base.mark_bar(color='#00adb5', opacity=0.75, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            y=alt.Y('Total (kWh):Q', title='Daily Consumption (kWh)'),
            tooltip=['Date_Str:T', 'Total (kWh):Q', 'Cost ($):Q']
        )
        
        line = base.mark_line(color='#ff9800', strokeWidth=2).encode(
            y=alt.Y('Temperature (°F):Q', title='Average Temperature (°F)', scale=alt.Scale(zero=False)),
            tooltip=['Date_Str:T', 'Temperature (°F):Q']
        )
        
        # Combine charts with dual y-axis
        daily_chart = alt.layer(bar, line).resolve_scale(
            y='independent'
        ).properties(
            width='container',
            height=350
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(daily_chart, use_container_width=True)
        
        # Heatmap of Daily Profile (Day of Week vs Hour)
        st.subheader("Weekly Usage Signature")
        st.write("This map shows the average energy load (kWh) for each hour of each day of the week. Darker colors represent periods of heavier usage.")
        
        signature_df = df.groupby(['Day of Week', 'Hour'])['Total (kWh)'].mean().reset_index()
        
        # Order days
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        heatmap = alt.Chart(signature_df).mark_rect().encode(
            x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(values=list(range(24)))),
            y=alt.Y('Day of Week:O', title='Day of Week', sort=day_order),
            color=alt.Color('Total (kWh):Q', scale=alt.Scale(scheme='yelloworange-red'), title='Avg kWh'),
            tooltip=['Day of Week', 'Hour', 'Total (kWh)']
        ).properties(
            width='container',
            height=280
        )
        
        st.altair_chart(heatmap, use_container_width=True)
        
    # Tab 2: Peak Hour Analysis
    with tab2:
        st.subheader("🔥 Time-of-Day Peak Usage Profile")
        st.write("To reduce costs, it is critical to know exactly when your energy consumption spikes. Below is the average hourly load profile over your selected period.")
        
        # Highlight Peak Hours
        # Add a column for color scale based on peak
        hourly_avg['Peak Type'] = 'Normal'
        
        # Find top 3 hours of highest usage
        top_hours = hourly_avg.nlargest(4, 'Total (kWh)')['Hour'].tolist()
        for idx, row in hourly_avg.iterrows():
            h = int(row['Hour'])
            if h == peak_hour:
                hourly_avg.at[idx, 'Peak Type'] = 'Absolute Peak'
            elif h in top_hours:
                hourly_avg.at[idx, 'Peak Type'] = 'High Usage'
                
        # Custom color scale
        color_scale = alt.Scale(
            domain=['Absolute Peak', 'High Usage', 'Normal'],
            range=['#ff3d00', '#ffb300', '#00adb5']
        )
        
        hourly_chart = alt.Chart(hourly_avg).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X('Hour:O', title='Hour of Day (24h clock)'),
            y=alt.Y('Total (kWh):Q', title='Average Hourly Consumption (kWh)'),
            color=alt.Color('Peak Type:N', scale=color_scale, legend=alt.Legend(title="Load Level")),
            tooltip=['Hour', 'Total (kWh)']
        ).properties(
            width='container',
            height=350
        )
        
        st.altair_chart(hourly_chart, use_container_width=True)
        
        # Peak vs Off-Peak Metrics
        st.markdown("### Peak vs. Off-Peak Comparison")
        
        # Let's group based on peak hours defined in the sidebar or a default peak window (e.g. 5 PM - 9 PM if Flat rate)
        p_start = peak_start_hour if tariff_type == "Time-of-Use (TOU)" else 17
        p_end = peak_end_hour if tariff_type == "Time-of-Use (TOU)" else 21
        
        # Calculate if row is in peak window
        if p_start <= p_end:
            df['In Peak Window'] = (df['Hour'] >= p_start) & (df['Hour'] <= p_end)
        else:
            df['In Peak Window'] = (df['Hour'] >= p_start) | (df['Hour'] <= p_end)
            
        peak_window_df = df[df['In Peak Window']]
        off_peak_window_df = df[~df['In Peak Window']]
        
        avg_peak_load = peak_window_df['Total (kWh)'].mean()
        avg_off_peak_load = off_peak_window_df['Total (kWh)'].mean()
        peak_percentage = (peak_window_df['Total (kWh)'].sum() / total_consumption) * 100
        
        p_col1, p_col2, p_col3 = st.columns(3)
        
        p_start_str = format_hour(p_start)
        p_end_str = format_hour(p_end)
        
        with p_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🔴 Peak Hours Avg Load</div>
                <div class="metric-value" style="color: #ff3d00;">{avg_peak_load:.2f} <span style="font-size: 1.1rem; font-weight: 500; color: #888;">kWh</span></div>
                <div class="metric-subtitle-red">Daily window: {p_start_str} - {p_end_str}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🟢 Off-Peak Hours Avg Load</div>
                <div class="metric-value" style="color: #4caf50;">{avg_off_peak_load:.2f} <span style="font-size: 1.1rem; font-weight: 500; color: #888;">kWh</span></div>
                <div class="metric-subtitle">Remaining hours of the day</div>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📊 Share of Total Energy</div>
                <div class="metric-value" style="color: #2196f3;">{peak_percentage:.1f}%</div>
                <div class="metric-subtitle-blue">Consumed during the {len(df[df['In Peak Window']]['Hour'].unique())}-hour peak window</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Explanatory Insight Box
        peak_hour_desc = f"{p_start_str} to {p_end_str}"
        ratio = avg_peak_load / avg_off_peak_load if avg_off_peak_load > 0 else 1
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-box-title">💡 Peak Consumption Signature Detected</div>
            Your electricity usage during peak hours (<b>{peak_hour_desc}</b>) is <b>{ratio:.1f}x higher</b> than during off-peak hours. 
            This spike is primarily driven by household appliances, lighting, heating/cooling, and cooking coinciding with returning home from work. 
            Under a <b>Time-of-Use</b> tariff model, this peak period accounts for a significant portion of your energy bill.
        </div>
        """, unsafe_allow_html=True)
        
        # Temperature Correlation
        st.subheader("🌡️ Temperature and Energy Load Correlation")
        st.write("Hotter afternoon temperatures can significantly increase cooling (HVAC) load, worsening the peak.")
        
        temp_chart = alt.Chart(df.sample(min(1500, len(df)))).mark_circle(size=60, opacity=0.6).encode(
            x=alt.X('Temperature (°F):Q', title='Temperature (°F)'),
            y=alt.Y('Total (kWh):Q', title='Hourly Consumption (kWh)'),
            color=alt.Color('In Peak Window:N', scale=alt.Scale(domain=[True, False], range=['#ff3d00', '#00adb5']), title='Is Peak Hour'),
            tooltip=['Hour', 'Temperature (°F)', 'Total (kWh)']
        ).properties(
            width='container',
            height=300
        )
        st.altair_chart(temp_chart, use_container_width=True)

    # Tab 3: Appliance Breakdown
    with tab3:
        st.subheader("🔌 Appliance-Level Breakdown")
        st.write("Understand which appliances are consuming the most power. Focus your savings efforts on the largest energy consumers.")
        
        # Calculate totals for each appliance
        appliance_cols = [c for c in df.columns if '(kWh)' in c and 'Total' not in c and 'Cost' not in c]
        
        appliance_totals = df[appliance_cols].sum().reset_index()
        appliance_totals.columns = ['Appliance', 'Total Consumption (kWh)']
        # Clean appliance name
        appliance_totals['Appliance'] = appliance_totals['Appliance'].str.replace(' (kWh)', '', regex=False)
        appliance_totals['Percentage'] = (appliance_totals['Total Consumption (kWh)'] / total_consumption) * 100
        
        app_col1, app_col2 = st.columns([1, 1])
        
        with app_col1:
            # Donut chart
            donut = alt.Chart(appliance_totals).mark_arc(innerRadius=80).encode(
                theta=alt.Theta(field="Total Consumption (kWh)", type="quantitative"),
                color=alt.Color(field="Appliance", type="nominal", scale=alt.Scale(scheme='tableau10')),
                tooltip=['Appliance', 'Total Consumption (kWh):Q', 'Percentage:Q']
            ).properties(
                title="Total Energy Breakdown by Appliance",
                height=300
            )
            st.altair_chart(donut, use_container_width=True)
            
        with app_col2:
            # Horizontal bar chart
            bar_chart = alt.Chart(appliance_totals).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                x=alt.X('Total Consumption (kWh):Q', title='Total Energy (kWh)'),
                y=alt.Y('Appliance:N', title='Appliance', sort='-x'),
                color=alt.Color('Appliance:N', scale=alt.Scale(scheme='tableau10'), legend=None),
                tooltip=['Appliance', 'Total Consumption (kWh):Q', 'Percentage:Q']
            ).properties(
                title="Consumption Ranking",
                height=300
            )
            st.altair_chart(bar_chart, use_container_width=True)
            
        # Detailed Stacked Area Chart over Time
        st.subheader("Hourly Energy Profile by Appliance")
        st.write("See how the components stack up across a typical 24-hour cycle.")
        
        # Melt data for visualization
        melt_cols = ['Hour'] + appliance_cols
        melt_df = df[melt_cols].melt(id_vars=['Hour'], var_name='Appliance', value_name='Consumption (kWh)')
        melt_df['Appliance'] = melt_df['Appliance'].str.replace(' (kWh)', '', regex=False)
        
        hourly_app_avg = melt_df.groupby(['Hour', 'Appliance'])['Consumption (kWh)'].mean().reset_index()
        
        area_chart = alt.Chart(hourly_app_avg).mark_area(opacity=0.85).encode(
            x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(values=list(range(24)))),
            y=alt.Y('Consumption (kWh):Q', title='Average Energy Consumption (kWh)'),
            color=alt.Color('Appliance:N', scale=alt.Scale(scheme='tableau10')),
            tooltip=['Hour', 'Appliance', 'Consumption (kWh)']
        ).properties(
            width='container',
            height=350
        )
        st.altair_chart(area_chart, use_container_width=True)

    # Tab 4: Shift & Save Simulator
    with tab4:
        st.subheader("💡 Load Shifting & Saving Simulator")
        st.write("Load shifting is one of the most effective strategies for saving energy costs. By moving flexible loads (like EV charging, laundry, or dishwashers) from Peak periods to Off-Peak hours, you can dramatically lower your electricity bill without using less energy.")
        
        if tariff_type == "Flat Rate":
            st.warning("⚠️ **Note:** You are currently on a **Flat Rate** tariff model. Shifting loads will not reduce your costs because the rate is the same ($0.15/kWh) all day. To explore the savings potential of load shifting, select **Time-of-Use (TOU)** in the sidebar pricing settings!")
            
        # Let's set up a simulator
        sim_col1, sim_col2 = st.columns([1, 2])
        
        # Default TOU rates if user has flat rate selected (for display in calculator)
        sim_p_rate = peak_rate if tariff_type == "Time-of-Use (TOU)" else 0.28
        sim_op_rate = off_peak_rate if tariff_type == "Time-of-Use (TOU)" else 0.11
        sim_p_start = peak_start_hour if tariff_type == "Time-of-Use (TOU)" else 17
        sim_p_end = peak_end_hour if tariff_type == "Time-of-Use (TOU)" else 21
        
        with sim_col1:
            st.markdown("#### **Configure Your Simulation**")
            app_to_shift = st.selectbox(
                "Select appliance to shift:",
                ["EV Charger", "Laundry", "Other / Entertainment"]
            )
            
            app_col_map = {
                "EV Charger": "EV Charger (kWh)",
                "Laundry": "Laundry (kWh)",
                "Other / Entertainment": "Other (kWh)"
            }
            app_col_name = app_col_map[app_to_shift]
            
            # Show stats of selected appliance
            app_peak_df = df[df['Hour'].between(sim_p_start, sim_p_end) if sim_p_start <= sim_p_end else (df['Hour'] >= sim_p_start) | (df['Hour'] <= sim_p_end)]
            app_peak_consumption = app_peak_df[app_col_name].sum()
            
            st.markdown(f"Total **{app_to_shift}** consumption during Peak hours: **{app_peak_consumption:.1f} kWh**")
            
            shift_percent = st.slider(
                "Percentage of peak consumption to shift to Off-Peak:",
                min_value=0,
                max_value=100,
                value=50,
                step=10,
                help="Shifting 50% means half of the energy this appliance consumes during peak hours will be simulated as consumed during cheap off-peak hours instead."
            )
            
        with sim_col2:
            st.markdown("#### **Estimated Savings Results**")
            
            # Calculations
            shifted_kwh = app_peak_consumption * (shift_percent / 100.0)
            cost_difference_per_kwh = sim_p_rate - sim_op_rate
            
            # Savings calculations
            estimated_savings = shifted_kwh * cost_difference_per_kwh
            
            # Extrapolate to monthly and yearly
            active_days = (end_date - start_date).days + 1
            daily_saving = estimated_savings / active_days if active_days > 0 else 0
            monthly_saving = daily_saving * 30.4
            yearly_saving = daily_saving * 365
            
            # Calculate current bill under TOU (if not already selected, calculate for display)
            if tariff_type == "Time-of-Use (TOU)":
                current_bill = total_cost
            else:
                # Mock a TOU cost for simulation
                def mock_tou(row):
                    h = row['Hour']
                    is_peak = sim_p_start <= h <= sim_p_end if sim_p_start <= sim_p_end else (h >= sim_p_start or h <= sim_p_end)
                    r = sim_p_rate if is_peak else sim_op_rate
                    return row['Total (kWh)'] * r
                current_bill = df.apply(mock_tou, axis=1).sum()
                
            simated_bill = current_bill - estimated_savings
            savings_pct = (estimated_savings / current_bill) * 100 if current_bill > 0 else 0
            
            # Metrics
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown(f"""
                <div class="metric-card" style="border-color: #4caf50; background: rgba(76, 175, 80, 0.05);">
                    <div class="metric-title" style="color: #4caf50;">Estimated Period Savings</div>
                    <div class="metric-value" style="color: #4caf50;">${estimated_savings:.2f}</div>
                    <div class="metric-subtitle">({savings_pct:.1f}% reduction in bill)</div>
                </div>
                """, unsafe_allow_html=True)
            with res_col2:
                st.markdown(f"""
                <div class="metric-card" style="border-color: #00adb5; background: rgba(0, 173, 181, 0.05);">
                    <div class="metric-title" style="color: #00adb5;">Projected Annual Savings</div>
                    <div class="metric-value" style="color: #00adb5;">${yearly_saving:.2f}</div>
                    <div class="metric-subtitle">Assuming similar patterns year-round</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Dynamic chart illustrating the shift
            st.markdown(f"**How the Shift Impacts Your Daily Bill (Average Profile)**")
            
            # Create average hourly profile for selected appliance
            avg_profile = df.groupby('Hour').agg({
                'Total (kWh)': 'mean',
                app_col_name: 'mean'
            }).reset_index()
            
            # Calculate new simulated total
            avg_profile['Simulated Total (kWh)'] = avg_profile['Total (kWh)'].copy()
            
            # Identify hours
            is_peak_hour = lambda h: sim_p_start <= h <= sim_p_end if sim_p_start <= sim_p_end else (h >= sim_p_start or h <= sim_p_end)
            
            peak_hours_list = [h for h in range(24) if is_peak_hour(h)]
            off_peak_hours_list = [h for h in range(24) if not is_peak_hour(h)]
            
            # Total amount to shift on average profile
            avg_peak_app_kwh = avg_profile.loc[avg_profile['Hour'].isin(peak_hours_list), app_col_name].sum()
            avg_shifted_kwh = avg_peak_app_kwh * (shift_percent / 100.0)
            
            # Subtract from peak hours
            for ph in peak_hours_list:
                val = avg_profile.loc[avg_profile['Hour'] == ph, app_col_name].values[0]
                portion_to_subtract = val * (shift_percent / 100.0)
                avg_profile.loc[avg_profile['Hour'] == ph, 'Simulated Total (kWh)'] -= portion_to_subtract
                
            # Add to off-peak hours (evenly distributed at night, e.g., 12 AM to 5 AM)
            night_hours = [0, 1, 2, 3, 4, 5]
            avg_add_per_hour = avg_shifted_kwh / len(night_hours)
            for nh in night_hours:
                avg_profile.loc[avg_profile['Hour'] == nh, 'Simulated Total (kWh)'] += avg_add_per_hour
                
            # Prepare data for plotting
            plot_df = avg_profile[['Hour', 'Total (kWh)', 'Simulated Total (kWh)']].melt(
                id_vars=['Hour'], 
                var_name='Scenario', 
                value_name='Consumption (kWh)'
            )
            
            sim_chart = alt.Chart(plot_df).mark_line(strokeWidth=3, interpolate='monotone').encode(
                x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(values=list(range(24)))),
                y=alt.Y('Consumption (kWh):Q', title='Average Consumption (kWh)'),
                color=alt.Color('Scenario:N', scale=alt.Scale(domain=['Total (kWh)', 'Simulated Total (kWh)'], range=['#ff5722', '#4caf50']), legend=alt.Legend(title="Scenario")),
                tooltip=['Hour', 'Scenario', 'Consumption (kWh)']
            ).properties(
                height=220
            )
            st.altair_chart(sim_chart, use_container_width=True)

    # Tab 5: Conservation Recommendations
    with tab5:
        st.subheader("📋 Personalized Energy Conservation Recommendations")
        st.write("Based on your actual electricity usage patterns, we have generated these actionable tips to help you reduce waste and lower your power bills.")
        
        # 1. Peak Hour Recommendation
        st.markdown(f"#### **1. Address the Daily peak at {peak_hour_str}**")
        st.write(f"Your highest electricity usage occurs around **{peak_hour_str}**. To reduce load during this critical window:")
        st.markdown(f"""
        * **Adjust HVAC Thermostat**: Set your thermostat 2-3 degrees higher during peak hours in the summer (78°F instead of 75°F) or lower in the winter (68°F instead of 71°F). Pre-cool or pre-heat your home before {format_hour(p_start)}.
        * **Delay Heavy Appliances**: Run your dishwasher and dryer before {format_hour(p_start)} or set them on a delay timer to start after {format_hour(p_end)}.
        * **Cook Smart**: Micro-waves, air-fryers, and outdoor grills use significantly less power than pre-heating and running a large electric oven during hot peak hours.
        """)
        
        # 2. EV Charger Recommendation (if EV is a large component)
        ev_pct = appliance_totals[appliance_totals['Appliance'] == 'EV Charger']['Percentage'].values[0] if 'EV Charger' in appliance_totals['Appliance'].values else 0
        if ev_pct > 10:
            st.markdown("#### **2. Optimize EV Charging Schedule**")
            st.write(f"EV charging accounts for **{ev_pct:.1f}%** of your total electricity usage and is currently contributing to peak loads on certain days.")
            st.markdown("""
            * **Schedule Charging**: Most electric vehicles allow you to schedule charging via an app or vehicle console. Set your vehicle to charge exclusively during super-off-peak hours (e.g., **12:00 AM to 5:00 AM**). 
            * **Utility Programs**: Check if your electricity provider offers a special EV tariff rate that provides extremely cheap rates overnight.
            """)
            
        # 3. HVAC Recommendation (based on temp correlation)
        hvac_pct = appliance_totals[appliance_totals['Appliance'] == 'HVAC']['Percentage'].values[0] if 'HVAC' in appliance_totals['Appliance'].values else 0
        st.markdown(f"#### **3. Manage Heating & Cooling ({hvac_pct:.1f}% of usage)**")
        st.write("Heating and air conditioning represent the largest share of your energy consumption.")
        st.markdown("""
        * **Smart Thermostat**: Install a smart thermostat (like Nest or Ecobee) to automate temperature adjustments when you are away or sleeping.
        * **Maintain Equipment**: Replace air filters monthly to improve airflow and HVAC efficiency by up to 15%.
        * **Seal Drafts**: Add weatherstripping around doors and windows to prevent conditioned air from escaping.
        """)
        
        # 4. Standby Load (Base Load) Recommendation
        off_peak_base_load = off_peak_window_df['Total (kWh)'].min()
        annual_base_cost = off_peak_base_load * 24 * 365 * (flat_rate if tariff_type == "Flat Rate" else off_peak_rate)
        st.markdown("#### **4. Target Your 'Vampire' Power Draw**")
        st.write(f"Even when you are asleep or away, your home draws a baseline of at least **{off_peak_base_load:.2f} kW**, costing you approximately **${annual_base_cost:.2f} annually** in idle power.")
        st.markdown("""
        * **Use Smart Power Strips**: Smart strips detect when a primary device (like a TV or computer) is turned off and automatically cut power to secondary devices (like game consoles, speakers, and streaming boxes).
        * **Unplug Idle Chargers**: Phone and laptop chargers draw small amounts of power (vampire load) even when no device is plugged into them.
        * **Energy Star Upgrades**: When replacing older appliances (especially refrigerators or freezers that run 24/7), look for the Energy Star logo to ensure minimum standby draw.
        """)

else:
    st.error("No energy data available to visualize. Please check the data source settings.")
