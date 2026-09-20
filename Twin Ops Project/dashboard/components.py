import json
import os
import streamlit as st
from typing import Dict, Any, List
import pandas as pd
from app.config import SIMULATION_MODE_FILE, MACHINE_ID, MACHINE_TYPE, THRESHOLDS


def render_header(status_info: Dict[str, Any]):
    """Renders the top industrial control header bar."""
    st.markdown("""
        <style>
        .twinops-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            border: 1px solid #334155;
            color: #f8fafc;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .header-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #38bdf8;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header-subtitle {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 4px;
        }
        .pill {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 8px;
        }
        .pill-green { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
        .pill-blue { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #0284c7; }
        .pill-yellow { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }
        .pill-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        </style>
    """, unsafe_allow_html=True)

    last_ts = status_info.get("last_seen", "N/A")
    mqtt_status = status_info.get("mqtt_status", "CONNECTED")

    st.markdown(f"""
        <div class="twinops-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div class="header-title">⚙️ TWIN OPS</div>
                    <div class="header-subtitle">Industrial Digital Twin & Predictive Maintenance Platform — {MACHINE_ID} ({MACHINE_TYPE})</div>
                </div>
                <div style="margin-top: 8px;">
                    <span class="pill pill-green">● SYSTEM ONLINE</span>
                    <span class="pill pill-blue">📡 MQTT: {mqtt_status}</span>
                    <span class="pill pill-blue">💾 DB: CONNECTED</span>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">
                ⏱️ Last Telemetry Update: <strong>{last_ts}</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_metric_cards(latest: Dict[str, Any], health_info: Dict[str, Any]):
    """Renders primary KPI metric cards for temperature, vibration, pressure, and health score."""
    temp = latest.get("temperature", 0.0)
    vib = latest.get("vibration", 0.0)
    press = latest.get("pressure", 0.0)
    score = health_info.get("health_score", 100.0)
    status = health_info.get("status", "NORMAL")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🌡️ Temperature",
            value=f"{temp:.1f} °C",
            delta="Normal (<75°C)" if temp <= 75 else f"+{temp-75:.1f}°C High",
            delta_color="normal" if temp <= 75 else "inverse"
        )

    with col2:
        st.metric(
            label="📳 Vibration",
            value=f"{vib:.2f} mm/s",
            delta="Normal (<5.0)" if vib <= 5.0 else f"+{vib-5.0:.2f} High",
            delta_color="normal" if vib <= 5.0 else "inverse"
        )

    with col3:
        st.metric(
            label="🎯 Pressure",
            value=f"{press:.1f} bar",
            delta="Nominal (10-18)" if 10 <= press <= 18 else f"{press:.1f} Low",
            delta_color="normal" if 10 <= press <= 18 else "inverse"
        )

    with col4:
        if status == "NORMAL":
            badge_icon = "🟢"
        elif status == "WARNING":
            badge_icon = "🟡"
        else:
            badge_icon = "🔴"

        st.metric(
            label=f"{badge_icon} Health Score",
            value=f"{score:.0f} / 100",
            delta=f"Status: {status}",
            delta_color="normal" if status == "NORMAL" else "inverse"
        )


def render_digital_twin_schematic(latest: Dict[str, Any], health_info: Dict[str, Any]):
    """Renders a stylized SVG industrial pump schematic with dynamic live color nodes."""
    temp = latest.get("temperature", 60.0)
    vib = latest.get("vibration", 3.0)
    press = latest.get("pressure", 14.0)

    # Node Colors
    temp_color = "#22c55e" if temp <= 75 else ("#eab308" if temp <= 85 else "#ef4444")
    vib_color = "#22c55e" if vib <= 5.0 else ("#eab308" if vib <= 7.0 else "#ef4444")
    press_color = "#22c55e" if 10 <= press <= 18 else ("#eab308" if 8 <= press < 10 else "#ef4444")

    svg_code = f"""
    <div style="background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center;">
        <h4 style="color: #94a3b8; margin-bottom: 15px;">PUMP_001 — VIRTUAL DIGITAL TWIN SCHEMATIC</h4>
        <svg width="100%" height="280" viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="motorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#334155" />
                    <stop offset="100%" stop-color="#1e293b" />
                </linearGradient>
                <linearGradient id="pumpGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0284c7" />
                    <stop offset="100%" stop-color="#0369a1" />
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>

            <!-- Base Plate -->
            <rect x="50" y="190" width="600" height="20" rx="4" fill="#475569" />
            <rect x="70" y="210" width="560" height="8" rx="2" fill="#334155" />

            <!-- Electric Motor Housing -->
            <rect x="80" y="70" width="180" height="120" rx="8" fill="url(#motorGrad)" stroke="#64748b" stroke-width="2" />
            <text x="170" y="125" fill="#f8fafc" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">ELECTRIC MOTOR</text>
            <text x="170" y="145" fill="#94a3b8" font-family="sans-serif" font-size="11" text-anchor="middle">3-Phase Induction</text>

            <!-- Cooling Fins -->
            <line x1="100" y1="70" x2="100" y2="190" stroke="#475569" stroke-width="3" />
            <line x1="120" y1="70" x2="120" y2="190" stroke="#475569" stroke-width="3" />
            <line x1="140" y1="70" x2="140" y2="190" stroke="#475569" stroke-width="3" />

            <!-- Shaft & Coupling Guard -->
            <rect x="260" y="115" width="80" height="30" fill="#64748b" rx="3" />
            <line x1="260" y1="130" x2="340" y2="130" stroke="#cbd5e1" stroke-width="6" />

            <!-- Centrifugal Pump Volute Casing -->
            <circle cx="430" cy="130" r="60" fill="url(#pumpGrad)" stroke="#38bdf8" stroke-width="2" />
            <circle cx="430" cy="130" r="25" fill="#0f172a" stroke="#0284c7" stroke-width="2" />
            <text x="430" y="134" fill="#38bdf8" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">IMPELLER</text>

            <!-- Discharge Pipe (Top) -->
            <rect x="415" y="20" width="30" height="50" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />
            <rect x="405" y="15" width="50" height="10" fill="#38bdf8" rx="2" />

            <!-- Suction Pipe (Right) -->
            <rect x="490" y="115" width="80" height="30" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />
            <rect x="565" y="105" width="10" height="50" fill="#38bdf8" rx="2" />

            <!-- SENSOR NODES & OVERLAYS -->

            <!-- 1. Temperature Sensor Node (Bearing) -->
            <circle cx="230" cy="80" r="14" fill="{temp_color}" filter="url(#glow)" />
            <text x="230" y="84" fill="#0f172a" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">T</text>
            <line x1="230" y1="66" x2="230" y2="40" stroke="{temp_color}" stroke-width="2" stroke-dasharray="2,2" />
            <rect x="160" y="15" width="140" height="25" rx="4" fill="#1e293b" stroke="{temp_color}" stroke-width="1.5" />
            <text x="230" y="31" fill="#f8fafc" font-family="sans-serif" font-size="11" text-anchor="middle">Temp: {temp:.1f}°C</text>

            <!-- 2. Vibration Sensor Node (Shaft Coupling) -->
            <circle cx="300" cy="165" r="14" fill="{vib_color}" filter="url(#glow)" />
            <text x="300" y="169" fill="#0f172a" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">V</text>
            <line x1="300" y1="179" x2="300" y2="200" stroke="{vib_color}" stroke-width="2" stroke-dasharray="2,2" />
            <rect x="230" y="200" width="140" height="25" rx="4" fill="#1e293b" stroke="{vib_color}" stroke-width="1.5" />
            <text x="300" y="216" fill="#f8fafc" font-family="sans-serif" font-size="11" text-anchor="middle">Vib: {vib:.2f} mm/s</text>

            <!-- 3. Pressure Sensor Node (Discharge Pipe) -->
            <circle cx="430" cy="45" r="14" fill="{press_color}" filter="url(#glow)" />
            <text x="430" y="49" fill="#0f172a" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">P</text>
            <line x1="444" y1="45" x2="520" y2="45" stroke="{press_color}" stroke-width="2" stroke-dasharray="2,2" />
            <rect x="520" y="32" width="140" height="25" rx="4" fill="#1e293b" stroke="{press_color}" stroke-width="1.5" />
            <text x="590" y="48" fill="#f8fafc" font-family="sans-serif" font-size="11" text-anchor="middle">Press: {press:.1f} bar</text>

        </svg>
    </div>
    """
    st.markdown(svg_code, unsafe_allow_html=True)


def render_simulation_controls():
    """Renders interactive simulation control panel in the sidebar."""
    st.sidebar.markdown("### 🎛️ SIMULATION CONTROL")
    st.sidebar.markdown("""
        <div style="background: rgba(234, 179, 8, 0.1); padding: 8px 12px; border-radius: 6px; border: 1px solid #eab308; font-size: 0.78rem; color: #facc15; margin-bottom: 12px;">
            ⚠️ <strong>SIMULATION MODE</strong><br/>Not connected to live hardware. Use controls below to trigger physical anomalies for testing.
        </div>
    """, unsafe_allow_html=True)

    # Read current mode from file if exists
    current_mode = "NORMAL"
    if os.path.exists(SIMULATION_MODE_FILE):
        try:
            with open(SIMULATION_MODE_FILE, "r") as f:
                data = json.load(f)
                current_mode = data.get("mode", "NORMAL")
        except Exception:
            pass

    selected_mode = st.sidebar.radio(
        "Operating Mode:",
        options=["NORMAL", "WARNING", "FAILURE", "RANDOM"],
        index=["NORMAL", "WARNING", "FAILURE", "RANDOM"].index(current_mode) if current_mode in ["NORMAL", "WARNING", "FAILURE", "RANDOM"] else 0,
        help="NORMAL: Safe operational parameters. WARNING: Elevated temp/vibration. FAILURE: Critical fault threshold reached."
    )

    interval = st.sidebar.slider(
        "Publishing Interval (s):",
        min_value=1.0,
        max_value=10.0,
        value=2.0,
        step=0.5
    )

    if st.sidebar.button("Apply Mode Change", type="primary", use_container_width=True):
        os.makedirs(os.path.dirname(SIMULATION_MODE_FILE), exist_ok=True)
        with open(SIMULATION_MODE_FILE, "w") as f:
            json.dump({"mode": selected_mode, "interval": interval}, f)
        st.sidebar.success(f"Mode updated to {selected_mode}!")


def render_alerts_panel(alerts: List[Dict[str, Any]]):
    """Renders list of recent system alerts."""
    st.subheader("🚨 System Alert Log")
    if not alerts:
        st.info("No active alerts logged. Machine operating within nominal parameters.")
        return

    for alert in alerts:
        sev = alert.get("severity", "INFO")
        if sev == "CRITICAL":
            border_color = "#ef4444"
            icon = "🔴"
            bg_color = "rgba(239, 68, 68, 0.1)"
        elif sev == "WARNING":
            border_color = "#eab308"
            icon = "🟡"
            bg_color = "rgba(234, 179, 8, 0.1)"
        else:
            border_color = "#38bdf8"
            icon = "🔵"
            bg_color = "rgba(56, 189, 248, 0.1)"

        st.markdown(f"""
            <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #f8fafc; font-size: 0.95rem;">{icon} [{sev}] {alert.get('parameter')} — {alert.get('message')}</strong>
                    <span style="font-size: 0.8rem; color: #94a3b8;">{alert.get('timestamp')}</span>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Value recorded: <code>{alert.get('value')}</code> | Machine: <code>{alert.get('machine_id')}</code>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_predictive_maintenance_panel(latest: Dict[str, Any], health_info: Dict[str, Any], anomaly_info: Dict[str, Any], df: pd.DataFrame):
    """Renders predictive maintenance diagnostic analysis and recommendations."""
    st.subheader("🔮 Predictive Maintenance & Health Diagnostics")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Risk Indicators & Anomalies")
        is_anom = anomaly_info.get("is_anomaly", False)
        anom_score = anomaly_info.get("anomaly_score", 0.0)

        if is_anom:
            st.error(f"⚠️ ANOMALY DETECTED (Score: {anom_score:.2f}) — Method: {anomaly_info.get('method')}")
        else:
            st.success(f"✓ Operational Pattern Normal (Anomaly Score: {anom_score:.2f})")

        factors = health_info.get("factors", {})
        st.markdown("**Contributing Risk Penalties:**")
        for param, info in factors.items():
            pen = info.get("penalty", 0.0)
            status_txt = info.get("status", "Normal")
            if pen > 0:
                st.write(f"• **{param.capitalize()}**: {status_txt} (-{pen} pts)")
            else:
                st.write(f"• **{param.capitalize()}**: Nominal (0 pts penalty)")

    with col2:
        st.markdown("#### Maintenance Recommendation")
        score = health_info.get("health_score", 100.0)

        if score < 60:
            rec = "🔴 **CRITICAL MAINTENANCE RECOMMENDED**: High risk of impending mechanical component failure. Schedule immediate shutdown and inspect pump bearings, shaft alignment, and discharge valves."
        elif score < 80:
            rec = "🟡 **PROACTIVE INSPECTION ADVISED**: Elevated stress metrics observed. Recommend scheduling routine maintenance check on lubrication and vibration isolation mounts."
        else:
            rec = "🟢 **HEALTHY OPERATION**: Pump operating normally. Continue standard monitoring schedule."

        st.info(rec)
        st.caption("🔒 *Note: Recommendations are prototype algorithmic demonstrations based on rule bounds.*")
