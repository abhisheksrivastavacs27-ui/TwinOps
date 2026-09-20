import pytest
from app.analytics.alerts import evaluate_telemetry_alerts


def test_evaluate_telemetry_alerts_normal():
    data = {
        "machine_id": "PUMP_001",
        "timestamp": "2026-09-19T20:00:00",
        "temperature": 60.0,
        "vibration": 3.0,
        "pressure": 14.0
    }
    alerts = evaluate_telemetry_alerts(data)
    assert len(alerts) == 0


def test_evaluate_telemetry_alerts_critical():
    data = {
        "machine_id": "PUMP_001",
        "timestamp": "2026-09-19T20:00:00",
        "temperature": 90.0,
        "vibration": 8.5,
        "pressure": 6.5
    }
    alerts = evaluate_telemetry_alerts(data)
    assert len(alerts) == 3
    severities = [a["severity"] for a in alerts]
    assert severities.count("CRITICAL") == 3
