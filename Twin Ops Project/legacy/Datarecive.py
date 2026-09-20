import paho.mqtt.client as mqtt

broker = "broker.hivemq.com"
topic = "twinops/pump01/telemetry"


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe(topic)


def on_message(client, userdata, msg):
    print("Data Received:", msg.payload.decode())


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883)

client.loop_forever()