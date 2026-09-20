import sqlite3
import os
import sys

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import DATABASE_PATH


def main():
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at path: {DATABASE_PATH}")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n==================================================")
    print("           TWIN OPS DATABASE INSPECTOR           ")
    print("==================================================\n")

    # Sensor Data Count
    cursor.execute("SELECT COUNT(*) as cnt FROM sensor_data")
    count = cursor.fetchone()["cnt"]
    print(f"📊 Total Telemetry Records: {count}")

    # Latest Telemetry
    cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print("\n--- Latest Telemetry Readings (Top 5) ---")
    if not rows:
        print("  (No telemetry records yet)")
    for r in rows:
        print(f"  [{r['timestamp']}] Temp: {r['temperature']}°C | Vib: {r['vibration']} mm/s | Press: {r['pressure']} bar")

    # Machine Status
    cursor.execute("SELECT * FROM machine_status")
    status_rows = cursor.fetchall()
    print("\n--- Machine Status ---")
    if not status_rows:
        print("  (No machine status updated yet)")
    for s in status_rows:
        print(f"  ID: {s['machine_id']} | Status: {s['status']} | Health Score: {s['health_score']}/100 | Last Seen: {s['last_seen']}")

    # Recent Alerts
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 5")
    alert_rows = cursor.fetchall()
    print("\n--- Recent Alerts (Top 5) ---")
    if not alert_rows:
        print("  (No alerts logged)")
    for a in alert_rows:
        print(f"  [{a['timestamp']}] [{a['severity']}] {a['parameter']}: {a['message']} (Val: {a['value']})")

    print("\n==================================================\n")
    conn.close()


if __name__ == "__main__":
    main()
