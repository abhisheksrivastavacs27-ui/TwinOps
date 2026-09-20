import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "twinops.db"))

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "twinops/pump01/telemetry")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "2.0"))

# Machine Specification
MACHINE_ID = os.getenv("MACHINE_ID", "PUMP_001")
MACHINE_TYPE = "Industrial Water Pump"

# Threshold Configurations (Centralized)
THRESHOLDS = {
    "temperature": {
        "normal_max": 75.0,
        "warning_max": 85.0,
        "critical_min": 85.0,
        "unit": "°C"
    },
    "vibration": {
        "normal_max": 5.0,
        "warning_max": 7.0,
        "critical_min": 7.0,
        "unit": "mm/s"
    },
    "pressure": {
        "normal_min": 10.0,
        "normal_max": 18.0,
        "warning_min": 8.0,
        "warning_max": 10.0,
        "critical_max": 8.0,
        "unit": "bar"
    }
}

# Simulation Settings File (for dynamic Streamlit UI mode changes)
SIMULATION_MODE_FILE = str(BASE_DIR / "data" / "simulation_mode.json")
