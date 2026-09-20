import json
import time
import sys
import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, PUBLISH_INTERVAL
from app.simulator.sensor_simulator import PumpSimulator
from app.utils.logging_config import setup_logging

logger = setup_logging("mqtt_publisher")


def run_publisher(
    broker: str = MQTT_BROKER,
    port: int = MQTT_PORT,
    topic: str = MQTT_TOPIC,
    interval: float = PUBLISH_INTERVAL,
    mode: str = "NORMAL"
):
    """Runs the MQTT publisher loop continuously."""
    simulator = PumpSimulator(mode=mode)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="twinops_pump01_publisher"
    )

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info("Connected successfully to MQTT Broker: %s:%d", broker, port)
        else:
            logger.error("Failed to connect to MQTT broker, reason_code: %s", reason_code)

    def on_disconnect(client, userdata, flags, reason_code, properties=None):
        logger.warning("Disconnected from MQTT broker (reason_code: %s). Retrying connection...", reason_code)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    logger.info("Connecting to MQTT Broker at %s:%d...", broker, port)
    try:
        client.connect(broker, port, keepalive=60)
        client.loop_start()
    except Exception as e:
        logger.error("Could not connect to MQTT broker: %s", e)
        sys.exit(1)

    logger.info("Starting telemetry transmission on topic: %s (Interval: %.1fs)...", topic, interval)

    try:
        while True:
            sensor_data = simulator.generate_sensor_data()
            payload = json.dumps(sensor_data)

            res = client.publish(topic, payload, qos=0)
            if res.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Published: %s", payload)
            else:
                logger.error("Failed to publish message (rc: %d)", res.rc)

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Publisher stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Publisher client disconnected cleanly.")


if __name__ == "__main__":
    run_publisher()
