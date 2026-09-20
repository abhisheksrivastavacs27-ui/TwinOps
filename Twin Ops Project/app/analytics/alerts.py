from typing import Dict, Any, List
from app.config import THRESHOLDS, MACHINE_ID


def evaluate_telemetry_alerts(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluates telemetry values against centralized threshold rules and returns generated alerts."""
    alerts = []
    machine_id = data.get("machine_id", MACHINE_ID)
    timestamp = data.get("timestamp")
    temp = data.get("temperature", 0.0)
    vib = data.get("vibration", 0.0)
    press = data.get("pressure", 0.0)

    # Temperature checks
    t_cfg = THRESHOLDS["temperature"]
    if temp > t_cfg["critical_min"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "CRITICAL",
            "parameter": "Temperature",
            "message": f"Critical high temperature detected ({temp:.1f}°C > {t_cfg['critical_min']}°C)",
            "value": temp,
            "status": "ACTIVE"
        })
    elif temp > t_cfg["normal_max"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "WARNING",
            "parameter": "Temperature",
            "message": f"High temperature warning ({temp:.1f}°C)",
            "value": temp,
            "status": "ACTIVE"
        })

    # Vibration checks
    v_cfg = THRESHOLDS["vibration"]
    if vib > v_cfg["critical_min"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "CRITICAL",
            "parameter": "Vibration",
            "message": f"Severe vibration anomaly detected ({vib:.2f} mm/s > {v_cfg['critical_min']} mm/s)",
            "value": vib,
            "status": "ACTIVE"
        })
    elif vib > v_cfg["normal_max"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "WARNING",
            "parameter": "Vibration",
            "message": f"Elevated vibration warning ({vib:.2f} mm/s)",
            "value": vib,
            "status": "ACTIVE"
        })

    # Pressure checks
    p_cfg = THRESHOLDS["pressure"]
    if press < p_cfg["critical_max"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "CRITICAL",
            "parameter": "Pressure",
            "message": f"Critical low pressure detected ({press:.1f} bar < {p_cfg['critical_max']} bar)",
            "value": press,
            "status": "ACTIVE"
        })
    elif press < p_cfg["normal_min"]:
        alerts.append({
            "machine_id": machine_id,
            "timestamp": timestamp,
            "severity": "WARNING",
            "parameter": "Pressure",
            "message": f"Sub-optimal pressure warning ({press:.1f} bar)",
            "value": press,
            "status": "ACTIVE"
        })

    return alerts
