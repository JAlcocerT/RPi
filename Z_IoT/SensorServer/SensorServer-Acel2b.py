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
    time_data = []  # To store elapsed time for each data point
    initial_velocity = 0
    last_local_timestamp = None
    total_distance = 0
    start_time = datetime.now().timestamp()  # Capture start time for elapsed time calculation

    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            local_timestamp = datetime.now().timestamp()
            elapsed_time = local_timestamp - start_time  # Calculate elapsed time since start

            acceleration = data['values'][2] + 0.115 + 0.0129#ADDING AVG

            if last_local_timestamp is not None:
                delta_t = local_timestamp - last_local_timestamp
                velocity = initial_velocity + acceleration * delta_t
                distance = initial_velocity * delta_t + 0.5 * acceleration * delta_t**2
                total_distance += distance
            else:
                velocity = initial_velocity
                distance = 0

            acceleration_data.append(acceleration)
            velocity_data.append(velocity)
            distance_data.append(total_distance)
            time_data.append(elapsed_time)  # Add elapsed time to time_data list

            initial_velocity = velocity
            last_local_timestamp = local_timestamp

    finally:
        # Calculate and print averages
        print_averages(acceleration_data, velocity_data, distance_data)
        # Plot the data with correct time scaling
        plot_data(time_data, acceleration_data, velocity_data, distance_data)

def print_averages(acceleration_data, velocity_data, distance_data):
    avg_acceleration = np.mean(acceleration_data) if acceleration_data else 0
    avg_velocity = np.mean(velocity_data) if velocity_data else 0
    avg_distance = np.mean(distance_data) if distance_data else 0
    print(f"Average Acceleration: {avg_acceleration:.4f} m/s^2")
    print(f"Average Velocity: {avg_velocity:.4f} m/s")
    print(f"Average Distance: {avg_distance:.4f} m")

def plot_data(time_data, acceleration_data, velocity_data, distance_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_data, y=acceleration_data, mode='lines+markers', name='Acceleration (m/s^2)'))
    fig.add_trace(go.Scatter(x=time_data, y=velocity_data, mode='lines+markers', name='Velocity (m/s)'))
    fig.add_trace(go.Scatter(x=time_data, y=distance_data, mode='lines+markers', name='Distance (m)'))
    fig.update_layout(
        title='Sensor Data over Time',
        xaxis_title='Time (seconds)',
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
    await receive_sensor_data(uri, timeout=5)  # Adjust the timeout as needed

asyncio.run(main())
