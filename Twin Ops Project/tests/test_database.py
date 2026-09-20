import os
import pytest
import sqlite3
from app.database import (
    init_db,
    save_sensor_data,
    save_alert,
    update_machine_status,
    get_recent_sensor_data,
    get_recent_alerts,
    get_machine_status
)


@pytest.fixture
def test_db(tmp_path):
    db_file = str(tmp_path / "test_twinops.db")
    init_db(db_file)
    return db_file


def test_init_db(test_db):
    assert os.path.exists(test_db)
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "sensor_data" in tables
    assert "alerts" in tables
    assert "machine_status" in tables


def test_save_and_retrieve_sensor_data(test_db):
    sample = {
        "machine_id": "PUMP_TEST",
        "timestamp": "2026-09-19T20:00:00",
        "temperature": 65.5,
        "vibration": 3.2,
        "pressure": 14.1
    }
    row_id = save_sensor_data(sample, db_path=test_db)
    assert row_id > 0

    df = get_recent_sensor_data(limit=10, db_path=test_db)
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]["temperature"] == 65.5


def test_save_and_retrieve_alert(test_db):
    alert = {
        "machine_id": "PUMP_TEST",
        "timestamp": "2026-09-19T20:01:00",
        "severity": "CRITICAL",
        "parameter": "Vibration",
        "message": "High vibration",
        "value": 8.5
    }
    alert_id = save_alert(alert, db_path=test_db)
    assert alert_id > 0

    alerts = get_recent_alerts(limit=10, db_path=test_db)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "CRITICAL"


def test_update_machine_status(test_db):
    update_machine_status("PUMP_TEST", "WARNING", 72.5, "2026-09-19T20:02:00", db_path=test_db)
    st = get_machine_status("PUMP_TEST", db_path=test_db)
    assert st is not None
    assert st["status"] == "WARNING"
    assert st["health_score"] == 72.5
