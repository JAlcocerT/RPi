##python3 SensorServer-Acel2.py


import asyncio
import websockets
import json
import plotly.graph_objects as go
from datetime import datetime


async def receive_sensor_data(uri, timeout=5):
    async with websockets.connect(uri) as websocket:
        try:
            await asyncio.wait_for(websocket_handler(websocket), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

import asyncio
import websockets
import json
import plotly.graph_objects as go
from datetime import datetime

async def websocket_handler(websocket):
    acceleration_data = []
    velocity_data = []
    distance_data = []
    initial_velocity = 0  # Starting with an initial velocity of 0 m/s
    last_local_timestamp = None  # To store the local timestamp of the previous reading
    total_distance = 0  # Initialize total distance traveled

    while True:
        message = await websocket.recv()
        data = json.loads(message)

        # Use local timestamp
        local_timestamp = datetime.now().timestamp()  # Get current local timestamp in seconds

        acceleration = data['values'][2]  # Assuming Z-axis acceleration in m/s^2

        if last_local_timestamp is not None:
            # Calculate time interval in seconds
            delta_t = local_timestamp - last_local_timestamp
            # Calculate velocity in m/s using the time interval
            velocity = initial_velocity + acceleration * delta_t
            # Calculate distance traveled during delta_t assuming constant velocity over the interval
            distance = initial_velocity * delta_t + 0.5 * acceleration * delta_t**2
            total_distance += distance
        else:
            velocity = initial_velocity
            distance = 0  # No movement for the first data point

        # Store data for plotting
        acceleration_data.append(acceleration)
        velocity_data.append(velocity)
        distance_data.append(total_distance)

        # Update for next iteration
        initial_velocity = velocity  # Update initial velocity
        last_local_timestamp = local_timestamp  # Update the local timestamp

        # Plotting function call (assuming it's called less frequently in practice)
        plot_data(acceleration_data, velocity_data, distance_data)

def plot_data(acceleration_data, velocity_data, distance_data):
    fig = go.Figure()
    # Adding acceleration data to the plot
    fig.add_trace(go.Scatter(y=acceleration_data, mode='lines+markers', name='Acceleration (m/s^2)'))
    # Adding velocity data to the plot
    fig.add_trace(go.Scatter(y=velocity_data, mode='lines+markers', name='Velocity (m/s)'))
    # Adding distance data to the plot
    fig.add_trace(go.Scatter(y=distance_data, mode='lines+markers', name='Distance (m)'))
    fig.update_layout(
        title='Sensor Data over Time',
        xaxis_title='Time (s)',
        yaxis_title='Values',
        legend_title="Data Type"
    )
    fig.write_html("sensor_data_plot.html")

def print_averages(acceleration_data, velocity_data, distance_data):
    avg_acceleration = np.mean(acceleration_data) if acceleration_data else 0
    avg_velocity = np.mean(velocity_data) if velocity_data else 0
    avg_distance = np.mean(distance_data) if distance_data else 0
    print(f"Average Acceleration: {avg_acceleration} m/s^2")
    print(f"Average Velocity: {avg_velocity} m/s")
    print(f"Average Distance: {avg_distance} m")

# Assuming the rest of your code remains the same and you have defined the main and other necessary functions.

async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    await receive_sensor_data(uri, timeout=5)

asyncio.run(main())
