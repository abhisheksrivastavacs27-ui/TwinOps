import numpy as np
from typing import Dict, Any, List, Optional
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.config import THRESHOLDS


class AnomalyDetector:
    """Experimental Demonstration Anomaly Detector using Isolation Forest and Statistical Z-Scores."""

    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.is_fitted = False
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
            self._fit_default_baseline()

    def _fit_default_baseline(self):
        """Fits model on nominal synthetic baseline operational data."""
        if not SKLEARN_AVAILABLE or self.model is None:
            return
        np.random.seed(42)
        # Generate 200 normal readings
        normal_temp = np.random.uniform(50.0, 72.0, 200)
        normal_vib = np.random.uniform(1.5, 4.5, 200)
        normal_press = np.random.uniform(11.0, 17.0, 200)
        X = np.column_stack([normal_temp, normal_vib, normal_press])
        self.model.fit(X)
        self.is_fitted = True

    def detect_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detects whether a telemetry reading is an anomaly."""
        temp = float(data.get("temperature", 60.0))
        vib = float(data.get("vibration", 3.0))
        press = float(data.get("pressure", 14.0))

        if SKLEARN_AVAILABLE and self.is_fitted and self.model is not None:
            features = np.array([[temp, vib, press]])
            prediction = self.model.predict(features)[0]  # 1: Normal, -1: Anomaly
            decision_score = self.model.decision_function(features)[0]

            # Convert decision_score to 0..1 scale (lower decision_score = higher anomaly likelihood)
            anomaly_score = float(np.clip(0.5 - decision_score, 0.0, 1.0))
            is_anomaly = bool(prediction == -1)
            method = "Isolation Forest (ML)"
        else:
            # Fallback Z-score thresholding
            temp_z = abs(temp - 60.0) / 10.0
            vib_z = abs(vib - 3.0) / 1.5
            press_z = abs(press - 14.0) / 3.0
            max_z = max(temp_z, vib_z, press_z)
            anomaly_score = float(min(1.0, max_z / 3.0))
            is_anomaly = anomaly_score > 0.6
            method = "Z-Score Statistical"

        status_str = "ANOMALY" if is_anomaly else "NORMAL"

        return {
            "is_anomaly": is_anomaly,
            "status": status_str,
            "anomaly_score": round(anomaly_score, 3),
            "method": method,
            "label": "Experimental Demonstration Anomaly Detection"
        }


# Singleton instance
detector = AnomalyDetector()


def detect_anomaly(data: Dict[str, Any]) -> Dict[str, Any]:
    return detector.detect_anomaly(data)
