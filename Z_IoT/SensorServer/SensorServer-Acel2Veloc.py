#python3 SensorServer-Acel2Veloc.py



import asyncio
import websockets
import json
import plotly.graph_objects as go

async def receive_sensor_data(uri, timeout=5):
    async with websockets.connect(uri) as websocket:
        try:
            await asyncio.wait_for(websocket_handler(websocket), timeout)
        except asyncio.TimeoutError:
            print("Timeout reached, stopping data reception.")

async def websocket_handler(websocket):
    acceleration_data = []
    velocity_data = []
    initial_velocity = 0  # Initial velocity
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        acceleration = data['values'][2]  # Assuming the third value is acceleration in m/s^2
        acceleration_data.append(acceleration)
        # Calculate velocity in m/s
        velocity = initial_velocity + acceleration
        velocity_data.append(velocity)
        initial_velocity = velocity  # Update initial velocity for next iteration
        # Plot acceleration and velocity
        plot_data(acceleration_data, velocity_data)

def plot_data(acceleration_data, velocity_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=acceleration_data, mode='lines', name='Acceleration', yaxis='y1'))
    fig.add_trace(go.Scatter(y=velocity_data, mode='lines', name='Velocity', yaxis='y2'))
    fig.update_layout(
        title='Acceleration and Velocity vs Time',
        xaxis_title='Time',
        yaxis_title='Acceleration (m/s^2)',  # Units for acceleration
        yaxis2=dict(title='Velocity (m/s)', overlaying='y', side='right')  # Secondary Y-axis for velocity
    )
    fig.write_html("acceleration_velocity_plot.html")

async def main():
    #uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.gravity"
    uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
    await receive_sensor_data(uri, timeout=5)

asyncio.run(main())


# import asyncio
# import websockets
# import json
# import plotly.graph_objects as go

# async def receive_sensor_data(uri, timeout=5):
#     async with websockets.connect(uri) as websocket:
#         try:
#             await asyncio.wait_for(websocket_handler(websocket), timeout)
#         except asyncio.TimeoutError:
#             print("Timeout reached, stopping data reception.")

# async def websocket_handler(websocket):
#     acceleration_data = []
#     velocity_data = []
#     initial_velocity = 0  # Initial velocity
#     while True:
#         message = await websocket.recv()
#         data = json.loads(message)
#         acceleration = data['values'][2]  # Assuming the third value is acceleration
#         acceleration_data.append(acceleration)
#         # Calculate velocity
#         velocity = initial_velocity + acceleration
#         velocity_data.append(velocity)
#         initial_velocity = velocity  # Update initial velocity for next iteration
#         # Plot acceleration and velocity
#         plot_data(acceleration_data, velocity_data)

# def plot_data(acceleration_data, velocity_data):
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(y=acceleration_data, mode='lines', name='Acceleration'))
#     fig.add_trace(go.Scatter(y=velocity_data, mode='lines', name='Velocity'))
#     fig.update_layout(title='Acceleration and Velocity vs Time', xaxis_title='Time', yaxis_title='Value')
#     fig.write_html("acceleration_velocity_plot.html")

# async def main():
#     uri = "ws://192.168.3.201:8080/sensor/connect?type=android.sensor.linear_acceleration"
#     await receive_sensor_data(uri, timeout=5)

# asyncio.run(main())
