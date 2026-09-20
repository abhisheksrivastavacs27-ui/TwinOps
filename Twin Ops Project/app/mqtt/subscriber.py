import json
import sys
import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from app.database import init_db, save_sensor_data, save_alert, update_machine_status
from app.analytics.alerts import evaluate_telemetry_alerts
from app.analytics.health import calculate_health_score
from app.utils.logging_config import setup_logging

logger = setup_logging("mqtt_subscriber")


def process_telemetry_message(payload_str: str):
    """Parses, validates, persists telemetry and updates health and alert statuses."""
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON payload: %s. Raw message: %s", e, payload_str)
        return

    # Validate required fields
    required_fields = ["machine_id", "timestamp", "temperature", "vibration", "pressure"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        logger.warning("Received telemetry missing required fields: %s. Payload: %s", missing, data)
        return

    # 1. Persist Telemetry to Database
    try:
        row_id = save_sensor_data(data)
        logger.info("Saved telemetry record #%d for %s", row_id, data["machine_id"])
    except Exception as e:
        logger.error("Failed to save sensor data to SQLite: %s", e)
        return

    # 2. Evaluate Rule-Based Alerts & Store
    try:
        alerts = evaluate_telemetry_alerts(data)
        for alert in alerts:
            alert_id = save_alert(alert)
            logger.warning("ALERT GENERATED [#%d] [%s] %s: %s (Value: %s)",
                           alert_id, alert["severity"], alert["parameter"], alert["message"], alert["value"])
    except Exception as e:
        logger.error("Error during alert evaluation: %s", e)

    # 3. Calculate Health Score & Update Machine Status
    try:
        health_info = calculate_health_score(data)
        update_machine_status(
            machine_id=data["machine_id"],
            status=health_info["status"],
            health_score=health_info["health_score"],
            last_seen=data["timestamp"]
        )
        logger.info("Updated Status for %s -> Health: %.1f/100 (%s)",
                    data["machine_id"], health_info["health_score"], health_info["status"])
    except Exception as e:
        logger.error("Error updating machine health status: %s", e)


def run_subscriber(broker: str = MQTT_BROKER, port: int = MQTT_PORT, topic: str = MQTT_TOPIC):
    """Runs the MQTT subscriber client continuously."""
    # Ensure database tables exist
    init_db()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="twinops_pump01_subscriber"
    )

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info("Connected to MQTT Broker. Subscribing to: %s", topic)
            client.subscribe(topic, qos=0)
        else:
            logger.error("Failed to connect to MQTT broker, reason_code: %s", reason_code)

    def on_message(client, userdata, msg):
        payload_str = msg.payload.decode("utf-8", errors="ignore")
        logger.debug("Received payload on %s: %s", msg.topic, payload_str)
        process_telemetry_message(payload_str)

    def on_disconnect(client, userdata, flags, reason_code, properties=None):
        logger.warning("Subscriber disconnected from MQTT broker (reason_code: %s).", reason_code)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    logger.info("Connecting subscriber to MQTT Broker at %s:%d...", broker, port)
    try:
        client.connect(broker, port, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Subscriber stopped by user.")
    except Exception as e:
        logger.error("Subscriber fatal error: %s", e)
    finally:
        client.disconnect()
        logger.info("Subscriber client disconnected cleanly.")


if __name__ == "__main__":
    run_subscriber()
