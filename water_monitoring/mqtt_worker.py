"""Optional MQTT-to-SQLite worker. Run only with a broker and paho-mqtt installed."""
import json
import os
from pydantic import ValidationError
from .schemas import WaterTelemetry
from .storage import WaterStore


def main():
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise SystemExit("Install requirements.txt to use MQTT worker") from exc
    host = os.getenv("WATER_MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("WATER_MQTT_PORT", "1883"))
    topic = os.getenv("WATER_MQTT_TOPIC", "waterplant/+/telemetry")
    store = WaterStore(os.getenv("WATER_DB_PATH", "./data/water_plant.db"))

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(topic, qos=1)
            print(f"Subscribed to {topic}")
        else:
            print(f"MQTT connection failed: {reason_code}")

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            reading = WaterTelemetry.model_validate(payload)
            store.insert(reading.model_dump())
            print(f"Stored telemetry from {reading.plant_id}")
        except (ValueError, UnicodeDecodeError, ValidationError) as exc:
            print(f"Rejected invalid telemetry: {exc}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
