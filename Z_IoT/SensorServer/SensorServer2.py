import asyncio
import websockets
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json


import asyncio
import websockets
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

# Lists to store separate sensor values
x_data = []
y_data = []
z_data = []

async def receive_sensor_data():
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")  # Continue printing the message
            
            # Parse the message as JSON and extract values
            sensor_data = json.loads(message)
            values = sensor_data["values"]
            
            # Append data to respective lists
            x_data.append(values[0])
            y_data.append(values[1])
            z_data.append(values[2])
            
            # Limiting to the latest 50 data points for each list
            if len(x_data) > 50: x_data.pop(0)
            if len(y_data) > 50: y_data.pop(0)
            if len(z_data) > 50: z_data.pop(0)

def update_plot(frame):
    plt.cla()  # Clear the current axes
    # Plot each sensor value list
    plt.plot(x_data, label='X Data')
    plt.plot(y_data, label='Y Data')
    plt.plot(z_data, label='Z Data')
    plt.legend(loc='upper left')
    plt.xlabel('Sample Number')
    plt.ylabel('Sensor Value')
    plt.title('Real-time Sensor Data Visualization')

# Set up plot to call update_plot() function periodically
fig = plt.figure()
ani = FuncAnimation(fig, update_plot, interval=1000)

# Use asyncio to run the WebSocket client
asyncio.run(receive_sensor_data())


# Global list to store the data points
# data_points = []

# async def receive_sensor_data():
#     #uri = "ws://[ip]:[port]/sensor/connect?type=[sensor_type]"
#     uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
#     async with websockets.connect(uri) as websocket:
#         while True:
#             message = await websocket.recv()
#             print(f"Received message: {message}")  # Add this line to print the message
#             # Assuming the message is a single numerical value; adjust parsing as necessary
#             data_points.append(float(message))
#             if len(data_points) > 50:  # Limiting to the latest 50 data points
#                 data_points.pop(0)

# def update_plot(frame):
#     plt.cla()  # Clear the current axes
#     plt.plot(data_points, label='Sensor Data')
#     plt.legend(loc='upper left')
#     plt.xlabel('Sample Number')
#     plt.ylabel('Sensor Value')
#     plt.title('Real-time Sensor Data Visualization')

# # Set up plot to call update_plot() function periodically
# fig = plt.figure()
# ani = FuncAnimation(fig, update_plot, interval=1000)

# # Run the WebSocket client in a separate thread
# loop = asyncio.get_event_loop()
# task = loop.create_task(receive_sensor_data())

# # Display the plot
# plt.show()

# # Stop the asyncio loop when the plot is closed
# loop.run_until_complete(task)
