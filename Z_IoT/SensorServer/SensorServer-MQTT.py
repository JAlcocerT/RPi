#python3 SensorServer2MQTT.py

import asyncio
import websockets
import json
import paho.mqtt.publish as publish

async def receive_sensor_data(uri, mqtt_topic, timeout=5):
    async with websockets.connect(uri) as websocket:
        try:
            await asyncio.wait_for(websocket_handler(websocket, mqtt_topic), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

async def websocket_handler(websocket, mqtt_topic):
    while True:
        message = await websocket.recv()
        print(f"Received message: {message}")
        data = json.loads(message)
        # Extract the third value from the 'values' field
        third_value = data['values'][2]
        print(f"Third value: {third_value}")
        # Publish the third value to MQTT
        publish.single(mqtt_topic, payload=str(third_value), hostname="192.168.3.200")
        print(f"Published third value to MQTT topic '{mqtt_topic}': {third_value}")
        # Log the message
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{message}\n")

async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    mqtt_topic = "sensor/third_value"  # MQTT topic to publish the third value
    await receive_sensor_data(uri, mqtt_topic, timeout=5)

asyncio.run(main())