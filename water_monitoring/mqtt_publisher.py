"""Optional MQTT publisher. Requires paho-mqtt and a reachable broker."""
import json
import os
import time
from .simulator import generate_reading


def main():
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise SystemExit("Install requirements.txt to use MQTT publishing") from exc
    host = os.getenv("WATER_MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("WATER_MQTT_PORT", "1883"))
    topic = os.getenv("WATER_MQTT_TOPIC", "waterplant/demo/telemetry")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(host, port, 60)
    client.loop_start()
    try:
        for i in range(100):
            reading = generate_reading(i)
            reading["timestamp"] = reading["timestamp"].isoformat()
            client.publish(topic, json.dumps(reading), qos=1)
            print(f"published {i + 1}/100 to {topic}")
            time.sleep(2)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
