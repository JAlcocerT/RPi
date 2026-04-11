"""
MQTT subscriber that writes Pico W sensor readings to TimescaleDB.
Run this in the background before starting the FastAPI web app.
"""

import time
import psycopg2
import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.1.2"
MQTT_PORT   = 1883
MQTT_TOPIC  = "pico/#"

DB_HOST = "192.168.1.2"
DB_PORT = 5432
DB_NAME = "sensors"
DB_USER = "pico"
DB_PASS = "pico"


def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    conn.autocommit = True
    return conn


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"MQTT connection failed, rc={rc}")


def on_message(client, userdata, msg):
    try:
        value = float(msg.payload.decode())
        with userdata["conn"].cursor() as cur:
            cur.execute(
                "INSERT INTO readings (topic, value) VALUES (%s, %s)",
                (msg.topic, value)
            )
        print(f"{msg.topic}: {value}")
    except Exception as e:
        print(f"Error inserting reading: {e}")
        # Reconnect DB on failure
        try:
            userdata["conn"] = connect_db()
        except Exception as db_err:
            print(f"DB reconnect failed: {db_err}")


def main():
    conn = connect_db()
    print("Connected to TimescaleDB")

    client = mqtt.Client(userdata={"conn": conn})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Fatal error: {e} — restarting in 5s")
            time.sleep(5)
