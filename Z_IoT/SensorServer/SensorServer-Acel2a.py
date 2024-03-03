
# ##python3 SensorServer-Acel2a.py

#TO BE ADJUSTED THE TIMESTAMP, AS IT IS NOT 500S


import asyncio
import websockets
import json
from datetime import datetime
import numpy as np  # For calculating averages
import plotly.graph_objects as go

async def websocket_handler(websocket):
    acceleration_data = []
    velocity_data = []
    distance_data = []
    initial_velocity = 0
    last_local_timestamp = None
    total_distance = 0

    try:
        while True:  # This loop will run until an exception (like a timeout) occurs
            message = await websocket.recv()
            data = json.loads(message)

            local_timestamp = datetime.now().timestamp()

            acceleration = data['values'][2]

            if last_local_timestamp is not None:
                delta_t = local_timestamp - last_local_timestamp
                velocity = initial_velocity + acceleration * delta_t
                distance = initial_velocity * delta_t + 0.5 * acceleration * delta_t**2
                total_distance += distance
            else:
                velocity = initial_velocity
                distance = 0

            acceleration_data.append(acceleration+0.1277) #adding the avg to get it closer to 0
            velocity_data.append(velocity)
            distance_data.append(total_distance)

            initial_velocity = velocity
            last_local_timestamp = local_timestamp

    finally:
        # Calculate and print averages
        print_averages(acceleration_data, velocity_data, distance_data)
        # Plot the data
        plot_data(acceleration_data, velocity_data, distance_data)

def print_averages(acceleration_data, velocity_data, distance_data):
    avg_acceleration = np.mean(acceleration_data) if acceleration_data else 0
    avg_velocity = np.mean(velocity_data) if velocity_data else 0
    avg_distance = np.mean(distance_data) if distance_data else 0
    print(f"Average Acceleration: {avg_acceleration:.4f} m/s^2")
    print(f"Average Velocity: {avg_velocity:.4f} m/s")
    print(f"Average Distance: {avg_distance:.4f} m")

def plot_data(acceleration_data, velocity_data, distance_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=acceleration_data, mode='lines+markers', name='Acceleration (m/s^2)'))
    fig.add_trace(go.Scatter(y=velocity_data, mode='lines+markers', name='Velocity (m/s)'))
    fig.add_trace(go.Scatter(y=distance_data, mode='lines+markers', name='Distance (m)'))
    fig.update_layout(
        title='Sensor Data over Time',
        xaxis_title='Time (s)',
        yaxis_title='Values',
        legend_title="Data Type"
    )
    fig.write_html("sensor_data_plot.html")

async def receive_sensor_data(uri, timeout=5):
    async with websockets.connect(uri) as websocket:
        try:
            await asyncio.wait_for(websocket_handler(websocket), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    await receive_sensor_data(uri, timeout=10)  # Adjust the timeout as needed

asyncio.run(main())



################3


# import asyncio
# import websockets
# import json
# import plotly.graph_objects as go
# from datetime import datetime


# async def receive_sensor_data(uri, timeout=5):
#     async with websockets.connect(uri) as websocket:
#         try:
#             await asyncio.wait_for(websocket_handler(websocket), timeout)
#         except asyncio.TimeoutError:
#             print("Timeout reached, stopping data reception.")

# import asyncio
# import websockets
# import json
# import plotly.graph_objects as go
# from datetime import datetime

# import asyncio
# import websockets
# import json
# import plotly.graph_objects as go
# from datetime import datetime
# import numpy as np  # For calculating averages

# async def websocket_handler(websocket):
#     acceleration_data = []
#     velocity_data = []
#     distance_data = []
#     initial_velocity = 0
#     last_local_timestamp = None
#     total_distance = 0

#     try:
#         while True:  # Assuming this is a condition for demonstration
#             message = await websocket.recv()
#             data = json.loads(message)

#             local_timestamp = datetime.now().timestamp()

#             acceleration = data['values'][2]

#             if last_local_timestamp is not None:
#                 delta_t = local_timestamp - last_local_timestamp
#                 velocity = initial_velocity + acceleration * delta_t
#                 distance = initial_velocity * delta_t + 0.5 * acceleration * delta_t**2
#                 total_distance += distance
#             else:
#                 velocity = initial_velocity
#                 distance = 0

#             acceleration_data.append(acceleration)
#             velocity_data.append(velocity)
#             distance_data.append(total_distance)

#             initial_velocity = velocity
#             last_local_timestamp = local_timestamp

#     except Exception as e:
#         print(f"Stopped data collection due to: {str(e)}")
#         # Calculate and print averages
#         print_averages(acceleration_data, velocity_data, distance_data)
#         # Continue with plotting
#         plot_data(acceleration_data, velocity_data, distance_data)

# def print_averages(acceleration_data, velocity_data, distance_data):
#     avg_acceleration = np.mean(acceleration_data) if acceleration_data else 0
#     avg_velocity = np.mean(velocity_data) if velocity_data else 0
#     avg_distance = np.mean(distance_data) if distance_data else 0
#     print(f"Average Acceleration: {avg_acceleration} m/s^2")
#     print(f"Average Velocity: {avg_velocity} m/s")
#     print(f"Average Distance: {avg_distance} m")

# # Assuming the rest of your code remains the same and you have defined the main and other necessary functions.



# # Assuming the rest of your code remains the same and you have defined the main and other necessary functions.

# async def main():
#     #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
#     uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
#     await receive_sensor_data(uri, timeout=5)

# asyncio.run(main())
