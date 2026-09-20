"""Backward compatibility wrapper for app.database.database."""
from app.database.database import (
    init_db as create_database,
    save_sensor_data,
    get_connection,
    init_db,
    save_alert,
    update_machine_status,
    get_recent_sensor_data,
    get_recent_alerts,
    get_machine_status
)

if __name__ == "__main__":
    create_database()
    print("Database created successfully!")