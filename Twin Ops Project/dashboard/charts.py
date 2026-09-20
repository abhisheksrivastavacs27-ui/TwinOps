import streamlit as st
import pandas as pd
from app.config import THRESHOLDS


def render_telemetry_charts(df: pd.DataFrame):
    """Renders time-series charts for Temperature, Vibration, Pressure, and Health Score."""
    if df.empty:
        st.warning("Insufficient telemetry data to display historical trend charts.")
        return

    st.subheader("📈 Real-Time Telemetry Trends")

    tab1, tab2, tab3 = st.tabs(["🌡️ Temperature", "📳 Vibration", "🎯 Pressure"])

    with tab1:
        st.caption("Temperature (°C) over Time (Normal < 75°C, Warning 75-85°C, Critical > 85°C)")
        chart_data = df.set_index("timestamp")[["temperature"]]
        st.line_chart(chart_data, color="#38bdf8")

    with tab2:
        st.caption("Vibration (mm/s) over Time (Normal < 5.0, Warning 5-7, Critical > 7.0)")
        chart_data = df.set_index("timestamp")[["vibration"]]
        st.line_chart(chart_data, color="#eab308")

    with tab3:
        st.caption("Pressure (bar) over Time (Nominal Range: 10.0 - 18.0 bar)")
        chart_data = df.set_index("timestamp")[["pressure"]]
        st.line_chart(chart_data, color="#22c55e")
