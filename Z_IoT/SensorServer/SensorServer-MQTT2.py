#python3 SensorServer-MQTT2.py

import asyncio
import websockets
import json
import paho.mqtt.publish as publish

async def receive_sensor_data(uri, mqtt_topics, timeout=5):
    async with websockets.connect(uri) as websocket:
        try:
            await asyncio.wait_for(websocket_handler(websocket, mqtt_topics), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

async def websocket_handler(websocket, mqtt_topics):
    while True:
        message = await websocket.recv()
        print(f"Received message: {message}")
        data = json.loads(message)
        # Extract the three values from the 'values' field
        values = data['values']
        print(f"Received values: {values}")
        # Publish each value to its respective MQTT topic
        for i, value in enumerate(values):
            mqtt_topic = mqtt_topics[i]
            publish.single(mqtt_topic, payload=str(value), hostname="192.168.3.200")
            print(f"Published value to MQTT topic '{mqtt_topic}': {value}")
        # Log the message
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{message}\n")

async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration" #without G
    mqtt_topics = ["sensor/value1", "sensor/value2", "sensor/value3"]  # MQTT topics for each value
    await receive_sensor_data(uri, mqtt_topics, timeout=10)

asyncio.run(main())