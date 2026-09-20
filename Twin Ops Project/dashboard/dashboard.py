import os
import sys
import time
import streamlit as st
import pandas as pd

# Add workspace root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import DATABASE_PATH, MACHINE_ID
from app.database import (
    init_db,
    get_recent_sensor_data,
    get_recent_alerts,
    get_machine_status
)
from app.analytics.health import calculate_health_score
from app.analytics.anomaly_detection import detect_anomaly
try:
    from components import (
        render_header,
        render_metric_cards,
        render_digital_twin_schematic,
        render_simulation_controls,
        render_alerts_panel,
        render_predictive_maintenance_panel
    )
    from charts import render_telemetry_charts
except (ImportError, ModuleNotFoundError):
    from dashboard.components import (
        render_header,
        render_metric_cards,
        render_digital_twin_schematic,
        render_simulation_controls,
        render_alerts_panel,
        render_predictive_maintenance_panel
    )
    from dashboard.charts import render_telemetry_charts

# Page Configuration
st.set_page_config(
    page_title="Twin Ops — Industrial Digital Twin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS for Dark Industrial Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
    }
    .stSidebar {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    # Ensure DB tables exist
    init_db()

    # Sidebar Navigation & Simulation Controls
    st.sidebar.image("https://img.icons8.com/color/96/water-pump.png", width=64)
    st.sidebar.title("TWIN OPS")
    st.sidebar.markdown("**Industrial Digital Twin Platform**")
    st.sidebar.divider()

    navigation = st.sidebar.radio(
        "Navigation",
        ["📊 Live Overview", "🧩 Digital Twin View", "🚨 Alert Log", "📈 Analytics", "🔮 Predictive Maintenance"],
        index=0
    )

    st.sidebar.divider()
    render_simulation_controls()

    # Refresh Rate Control
    st.sidebar.divider()
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh Dashboard", value=True)
    refresh_rate = st.sidebar.slider("Refresh Interval (s)", 1, 10, 2)

    # Data Ingestion Query
    df = get_recent_sensor_data(limit=100)
    alerts = get_recent_alerts(limit=20)
    status_db = get_machine_status(MACHINE_ID)

    if df.empty:
        status_info = {
            "last_seen": "No Data Yet (Start Subscriber)",
            "status": "OFFLINE",
            "health_score": 100.0,
            "mqtt_status": "WAITING FOR TELEMETRY"
        }
        latest_reading = {
            "machine_id": MACHINE_ID,
            "timestamp": "N/A",
            "temperature": 0.0,
            "vibration": 0.0,
            "pressure": 0.0
        }
        health_info = {"health_score": 100.0, "status": "UNKNOWN", "factors": {}}
        anomaly_info = {"is_anomaly": False, "anomaly_score": 0.0, "method": "N/A"}
    else:
        latest_row = df.iloc[-1].to_dict()
        latest_reading = {
            "machine_id": str(latest_row.get("machine_id", MACHINE_ID)),
            "timestamp": str(latest_row.get("timestamp", "N/A")),
            "temperature": float(latest_row.get("temperature", 0.0)),
            "vibration": float(latest_row.get("vibration", 0.0)),
            "pressure": float(latest_row.get("pressure", 0.0))
        }

        health_info = calculate_health_score(latest_reading)
        anomaly_info = detect_anomaly(latest_reading)

        status_info = {
            "last_seen": latest_reading["timestamp"],
            "status": health_info["status"],
            "health_score": health_info["health_score"],
            "mqtt_status": "CONNECTED"
        }

    # Render Persistent Industrial Header
    render_header(status_info)

    # Route Selected View
    if navigation == "📊 Live Overview":
        if df.empty:
            st.warning("⚠️ No sensor telemetry currently available in SQLite database (`data/twinops.db`). Please launch `app.mqtt.publisher` and `app.mqtt.subscriber`.")
        else:
            render_metric_cards(latest_reading, health_info)
            st.divider()
            col1, col2 = st.columns([1.2, 1])
            with col1:
                render_telemetry_charts(df)
            with col2:
                render_alerts_panel(alerts[:5])

    elif navigation == "🧩 Digital Twin View":
        if df.empty:
            st.warning("Please start telemetry ingestion to view dynamic digital twin node states.")
        else:
            render_metric_cards(latest_reading, health_info)
            st.divider()
            render_digital_twin_schematic(latest_reading, health_info)

    elif navigation == "🚨 Alert Log":
        render_alerts_panel(alerts)

    elif navigation == "📈 Analytics":
        st.subheader("📊 Aggregate Telemetry Analytics")
        if df.empty:
            st.info("No historical readings available for statistics.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Temperature", f"{df['temperature'].mean():.1f} °C", f"Max: {df['temperature'].max():.1f}°C")
            col2.metric("Avg Vibration", f"{df['vibration'].mean():.2f} mm/s", f"Max: {df['vibration'].max():.2f} mm/s")
            col3.metric("Avg Pressure", f"{df['pressure'].mean():.1f} bar", f"Min: {df['pressure'].min():.1f} bar")
            st.divider()
            render_telemetry_charts(df)

    elif navigation == "🔮 Predictive Maintenance":
        if df.empty:
            st.info("Start subscriber to enable predictive health analytics.")
        else:
            render_predictive_maintenance_panel(latest_reading, health_info, anomaly_info, df)

    # Auto Refresh Loop
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()


if __name__ == "__main__":
    main()
