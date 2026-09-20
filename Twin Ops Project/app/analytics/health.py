from typing import Dict, Any
from app.config import THRESHOLDS


def calculate_health_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates a transparent demonstration health score (0-100) for PUMP_001.

    Clearly labeled as 'Prototype Pump Health Score'.
    """
    temp = data.get("temperature", 60.0)
    vib = data.get("vibration", 3.0)
    press = data.get("pressure", 14.0)

    score = 100.0
    factors = {}

    # Temperature Penalty (Up to 40 pts)
    if temp <= THRESHOLDS["temperature"]["normal_max"]:
        temp_status = "Normal"
        temp_penalty = 0.0
    elif temp <= THRESHOLDS["temperature"]["warning_max"]:
        temp_status = "Elevated"
        # Linear penalty between 75°C (0 pts) and 85°C (20 pts)
        temp_penalty = 20.0 * ((temp - 75.0) / 10.0)
    else:
        temp_status = "Critical"
        # Penalty between 85°C (20 pts) and 100°C (40 pts)
        temp_penalty = 20.0 + min(20.0, 20.0 * ((temp - 85.0) / 15.0))
    factors["temperature"] = {"status": temp_status, "penalty": round(temp_penalty, 1)}

    # Vibration Penalty (Up to 40 pts)
    if vib <= THRESHOLDS["vibration"]["normal_max"]:
        vib_status = "Normal"
        vib_penalty = 0.0
    elif vib <= THRESHOLDS["vibration"]["warning_max"]:
        vib_status = "Elevated"
        vib_penalty = 20.0 * ((vib - 5.0) / 2.0)
    else:
        vib_status = "Critical"
        vib_penalty = 20.0 + min(20.0, 20.0 * ((vib - 7.0) / 3.0))
    factors["vibration"] = {"status": vib_status, "penalty": round(vib_penalty, 1)}

    # Pressure Penalty (Up to 20 pts)
    if THRESHOLDS["pressure"]["normal_min"] <= press <= THRESHOLDS["pressure"]["normal_max"]:
        press_status = "Normal"
        press_penalty = 0.0
    elif THRESHOLDS["pressure"]["warning_min"] <= press < THRESHOLDS["pressure"]["normal_min"]:
        press_status = "Low Warning"
        press_penalty = 10.0 * ((10.0 - press) / 2.0)
    else:
        press_status = "Critical Low"
        press_penalty = 10.0 + min(10.0, 10.0 * ((8.0 - press) / 4.0))
    factors["pressure"] = {"status": press_status, "penalty": round(press_penalty, 1)}

    # Calculate final health score
    total_penalty = temp_penalty + vib_penalty + press_penalty
    final_score = max(0.0, min(100.0, score - total_penalty))
    final_score = round(final_score, 1)

    # Status Determination
    if final_score >= 80.0:
        overall_status = "NORMAL"
    elif final_score >= 60.0:
        overall_status = "WARNING"
    else:
        overall_status = "CRITICAL"

    return {
        "health_score": final_score,
        "status": overall_status,
        "factors": factors,
        "label": "Prototype Demonstration Health Score"
    }
