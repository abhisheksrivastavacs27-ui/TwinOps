import pytest
from app.analytics.anomaly_detection import detect_anomaly, AnomalyDetector


def test_anomaly_detector_normal():
    detector = AnomalyDetector()
    data = {"temperature": 60.0, "vibration": 3.0, "pressure": 14.0}
    res = detector.detect_anomaly(data)
    assert "is_anomaly" in res
    assert "anomaly_score" in res
    assert isinstance(res["anomaly_score"], float)


def test_anomaly_detector_extreme_outlier():
    detector = AnomalyDetector()
    data = {"temperature": 115.0, "vibration": 15.0, "pressure": 2.0}
    res = detector.detect_anomaly(data)
    assert res["is_anomaly"] is True
    assert res["status"] == "ANOMALY"
