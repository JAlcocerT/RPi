##python3 SensorServer-Acel2Veloc3.py


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

async def websocket_handler(websocket):
    acceleration_data = []
    velocity_data = []
    initial_velocity = 0  # Starting with an initial velocity of 0 m/s
    last_local_timestamp = None  # To store the local timestamp of the previous reading

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
        else:
            # For the first reading, we can't calculate delta_t or change in velocity
            velocity = initial_velocity

        # Store acceleration and velocity for plotting
        acceleration_data.append(acceleration)
        velocity_data.append(velocity)

        # Update for next iteration
        initial_velocity = velocity  # Update initial velocity
        last_local_timestamp = local_timestamp  # Update the local timestamp

        # Plotting function call (assuming it's called less frequently in practice)
        plot_data(acceleration_data, velocity_data)


def plot_data(acceleration_data, velocity_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=acceleration_data, mode='lines', name='Acceleration', yaxis='y1'))
    fig.add_trace(go.Scatter(y=velocity_data, mode='lines', name='Velocity', yaxis='y2'))
    fig.update_layout(
        title='Acceleration and Velocity vs Time',
        xaxis_title='Time',
        yaxis_title='Acceleration (m/s^2)',
        yaxis2=dict(title='Velocity (m/s)', overlaying='y', side='right')
    )
    fig.write_html("acceleration_velocity_plot.html")



async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    await receive_sensor_data(uri, timeout=5)

asyncio.run(main())
