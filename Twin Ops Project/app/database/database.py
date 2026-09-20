import os
import sqlite3
from typing import Dict, Any, List, Optional
import pandas as pd
from app.config import DATABASE_PATH, MACHINE_ID
from app.utils.logging_config import setup_logging

logger = setup_logging("database")


def get_connection(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    """Returns a connection to the SQLite database, ensuring directory exists."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_PATH):
    """Creates database tables and indexes if they do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Table 1: Telemetry Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            vibration REAL NOT NULL,
            pressure REAL NOT NULL
        )
    """)

    # Table 2: System Alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            parameter TEXT NOT NULL,
            message TEXT NOT NULL,
            value REAL NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    """)

    # Table 3: Machine Health Status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS machine_status (
            machine_id TEXT PRIMARY KEY,
            last_seen TEXT NOT NULL,
            status TEXT NOT NULL,
            health_score REAL NOT NULL
        )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_data_ts ON sensor_data (timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts (timestamp DESC)")

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully at: %s", db_path)


def save_sensor_data(data: Dict[str, Any], db_path: str = DATABASE_PATH) -> int:
    """Saves a telemetry reading into sensor_data table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_data (machine_id, timestamp, temperature, vibration, pressure)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["machine_id"],
        data["timestamp"],
        float(data["temperature"]),
        float(data["vibration"]),
        float(data["pressure"])
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_alert(alert: Dict[str, Any], db_path: str = DATABASE_PATH) -> int:
    """Saves an alert into alerts table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (machine_id, timestamp, severity, parameter, message, value, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        alert["machine_id"],
        alert["timestamp"],
        alert["severity"],
        alert["parameter"],
        alert["message"],
        float(alert["value"]),
        alert.get("status", "ACTIVE")
    ))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def update_machine_status(machine_id: str, status: str, health_score: float, last_seen: str, db_path: str = DATABASE_PATH):
    """Updates or inserts current status of a machine."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO machine_status (machine_id, last_seen, status, health_score)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(machine_id) DO UPDATE SET
            last_seen = excluded.last_seen,
            status = excluded.status,
            health_score = excluded.health_score
    """, (machine_id, last_seen, status, float(health_score)))
    conn.commit()
    conn.close()


def get_recent_sensor_data(limit: int = 100, db_path: str = DATABASE_PATH) -> pd.DataFrame:
    """Fetches recent sensor readings as a pandas DataFrame."""
    conn = get_connection(db_path)
    query = """
        SELECT machine_id, timestamp, temperature, vibration, pressure
        FROM sensor_data
        ORDER BY id DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    return df


def get_recent_alerts(limit: int = 20, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """Fetches recent alerts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, machine_id, timestamp, severity, parameter, message, value, status
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_machine_status(machine_id: str = MACHINE_ID, db_path: str = DATABASE_PATH) -> Optional[Dict[str, Any]]:
    """Fetches current machine status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT machine_id, last_seen, status, health_score
        FROM machine_status
        WHERE machine_id = ?
    """, (machine_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
