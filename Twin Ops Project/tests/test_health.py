import pytest
from app.analytics.health import calculate_health_score


def test_health_score_normal():
    data = {"temperature": 60.0, "vibration": 3.0, "pressure": 14.0}
    res = calculate_health_score(data)
    assert res["health_score"] == 100.0
    assert res["status"] == "NORMAL"


def test_health_score_warning():
    data = {"temperature": 80.0, "vibration": 6.0, "pressure": 9.0}
    res = calculate_health_score(data)
    assert 60.0 <= res["health_score"] < 80.0
    assert res["status"] == "WARNING"


def test_health_score_critical():
    data = {"temperature": 92.0, "vibration": 9.0, "pressure": 5.0}
    res = calculate_health_score(data)
    assert res["health_score"] < 60.0
    assert res["status"] == "CRITICAL"
