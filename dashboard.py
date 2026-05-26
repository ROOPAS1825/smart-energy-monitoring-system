import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Energy Monitoring Dashboard",
    page_icon="⚡",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 15px;
}

.stDataFrame {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("⚡ Smart Energy Monitoring System")

st.markdown("""
### Real-Time IoT Energy Analytics Dashboard

Monitor, analyze, and visualize smart energy consumption using IoT devices and AI-powered analytics.
""")

st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Dashboard Controls")

selected_days = st.sidebar.slider(
    "Select Number of Days",
    min_value=1,
    max_value=30,
    value=7
)

selected_device = st.sidebar.selectbox(
    "Select Device",
    [
        "ESP32 Device 1",
        "ESP32 Device 2",
        "ESP32 Device 3"
    ]
)

refresh_rate = st.sidebar.selectbox(
    "Refresh Rate",
    ["5 sec", "10 sec", "30 sec"]
)

# ---------------- DATE RANGE ----------------
dates = pd.date_range(
    end=datetime.now(),
    periods=selected_days * 24,
    freq="h"
)

# ---------------- DEVICE CONFIGURATION ----------------
device_profiles = {
    "ESP32 Device 1": {
        "base_energy": 60,
        "voltage": 220
    },
    "ESP32 Device 2": {
        "base_energy": 80,
        "voltage": 230
    },
    "ESP32 Device 3": {
        "base_energy": 100,
        "voltage": 240
    }
}

profile = device_profiles[selected_device]

# ---------------- DATA GENERATION FUNCTION ----------------
def generate_energy_data(dates, profile):

    np.random.seed(42)

    base_energy = profile["base_energy"]

    energy_usage = (
        base_energy
        + 15 * np.sin(np.linspace(0, 3*np.pi, len(dates)))
        + np.random.normal(0, 5, len(dates))
    )

    voltage = (
        profile["voltage"]
        + np.random.normal(0, 3, len(dates))
    )

    current = (
        energy_usage / 12
        + np.random.normal(0, 0.5, len(dates))
    )

    power_factor = np.clip(
        np.random.normal(0.92, 0.03, len(dates)),
        0.75,
        1.0
    )

    return pd.DataFrame({
        "Timestamp": dates,
        "Energy Usage (kWh)": np.round(energy_usage, 2),
        "Voltage (V)": np.round(voltage, 2),
        "Current (A)": np.round(current, 2),
        "Power Factor": np.round(power_factor, 2)
    })

# ---------------- GENERATE DATA ----------------
df = generate_energy_data(dates, profile)

# ---------------- METRICS ----------------
st.subheader("📊 Live Energy Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Usage",
        f"{df['Energy Usage (kWh)'].iloc[-1]} kWh",
        f"{round(df['Energy Usage (kWh)'].iloc[-1] - df['Energy Usage (kWh)'].iloc[-2], 2)} kWh"
    )

with col2:
    st.metric(
        "Average Usage",
        f"{round(df['Energy Usage (kWh)'].mean(), 2)} kWh"
    )

with col3:
    st.metric(
        "Peak Voltage",
        f"{round(df['Voltage (V)'].max(), 2)} V"
    )

with col4:
    st.metric(
        "Power Factor",
        f"{round(df['Power Factor'].mean(), 2)}"
    )

st.divider()

# ---------------- ENERGY CHART ----------------
st.subheader("📈 Energy Consumption Trend")

fig1, ax1 = plt.subplots(figsize=(12, 4))

ax1.plot(
    df["Timestamp"],
    df["Energy Usage (kWh)"],
    linewidth=2,
    marker="o",
    markersize=3
)

ax1.set_xlabel("Time")
ax1.set_ylabel("Energy Usage (kWh)")
ax1.grid(True)

st.pyplot(fig1)

# ---------------- VOLTAGE + CURRENT ----------------
st.subheader("🔌 Voltage & Current Monitoring")

col5, col6 = st.columns(2)

with col5:
    fig2, ax2 = plt.subplots(figsize=(6, 4))

    ax2.plot(
        df["Timestamp"],
        df["Voltage (V)"],
        linewidth=2
    )

    ax2.set_title("Voltage Monitoring")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Voltage (V)")
    ax2.grid(True)

    st.pyplot(fig2)

with col6:
    fig3, ax3 = plt.subplots(figsize=(6, 4))

    ax3.plot(
        df["Timestamp"],
        df["Current (A)"],
        linewidth=2
    )

    ax3.set_title("Current Monitoring")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Current (A)")
    ax3.grid(True)

    st.pyplot(fig3)

# ---------------- ENERGY DISTRIBUTION ----------------
st.subheader("⚡ Energy Usage Distribution")

fig4, ax4 = plt.subplots(figsize=(8, 4))

ax4.hist(
    df["Energy Usage (kWh)"],
    bins=15
)

ax4.set_xlabel("Energy Usage (kWh)")
ax4.set_ylabel("Frequency")

st.pyplot(fig4)

# ---------------- DEVICE STATUS ----------------
st.subheader("🟢 Device Status")

status_col1, status_col2, status_col3 = st.columns(3)

status_col1.success("ESP32 Device 1 - Online")
status_col2.success("ESP32 Device 2 - Online")
status_col3.warning("ESP32 Device 3 - High Load")

# ---------------- DATA TABLE ----------------
st.subheader("📋 Real-Time Energy Data")

st.dataframe(
    df.tail(20),
    use_container_width=True
)

# ---------------- AI INSIGHTS ----------------
st.subheader("🤖 AI-Based Insights")

avg_usage = df["Energy Usage (kWh)"].mean()
peak_voltage = df["Voltage (V)"].max()

if avg_usage > 80:
    st.warning(
        "High energy consumption detected. Consider reducing heavy appliance usage during peak hours."
    )
elif avg_usage > 50:
    st.info(
        "Energy consumption is moderate and stable."
    )
else:
    st.success(
        "Energy usage is operating efficiently."
    )

if peak_voltage > 245:
    st.error(
        "Voltage spikes detected. Device protection is recommended."
    )

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown(f"""
### 🚀 Features Included

- Real-time energy monitoring
- IoT device simulation
- Interactive analytics dashboard
- Voltage and current monitoring
- AI-generated energy insights
- Streamlit-based visualization
- Responsive dashboard layout

### ⚙️ Active Configuration

- Selected Device: **{selected_device}**
- Refresh Rate: **{refresh_rate}**

---

Built with ❤️ using Streamlit
""")