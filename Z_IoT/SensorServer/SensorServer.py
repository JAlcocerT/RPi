#python3 SensorServer.py

import asyncio
import websockets

import asyncio
import websockets

# Adjusted function to not require modifications for data_points handling
async def receive_sensor_data(uri, timeout=5):  # Timeout parameter added
    async with websockets.connect(uri) as websocket:
        try:
            # Run for only a specified timeout duration
            await asyncio.wait_for(websocket_handler(websocket), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

async def websocket_handler(websocket):
    while True:
        message = await websocket.recv()
        print(f"Received message: {message}")
        # Log the message
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"{message}\n")

async def main():
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration" #without G
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.accelerometer"
    await receive_sensor_data(uri, timeout=5)  # Call with a 5-second timeout

# Replace asyncio.run with an appropriate loop for older Python versions
asyncio.run(main())



# async def receive_sensor_data():
#     #uri = "ws://[ip]:[port]/sensor/connect?type=[sensor_type]"
#     #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
#     uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
#     async with websockets.connect(uri) as websocket:
#         while True:
#             message = await websocket.recv()
#             print(f"Received message: {message}")

# # Replace asyncio.run with an appropriate loop for older Python versions
# asyncio.run(receive_sensor_data())


#pip install asyncio

#https://f-droid.org/en/packages/github.umer0586.sensorserver/