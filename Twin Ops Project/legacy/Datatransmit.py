import json
import random
import time

import paho.mqtt.client as mqtt

broker = "broker.hivemq.com"
topic = "twinops/pump01/telemetry"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, 1883)
sensor_data = {
    "temperature": random.uniform(40, 90),
    "vibration": random.uniform(1, 10)
}
message = json.dumps(sensor_data)
client.publish(topic, message)
print("Data Sent:", message)
time.sleep(2)