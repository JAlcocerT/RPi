import plotly.graph_objects as go
import json

# Sample log entries
log_entries = [
    '{"values":[0.009,0.0039999997,-0.009],"timestamp":6186415106962397,"accuracy":0}',
    '{"values":[-8.0E-4,-5.9999997E-4,-0.0875],"timestamp":6186415126962397,"accuracy":0}',
    '{"values":[-8.0E-4,-0.0099,-0.0875],"timestamp":6186415146962397,"accuracy":0}',
    '{"values":[-8.0E-4,0.0088,-0.107099995],"timestamp":6186415166962397,"accuracy":0}',
    '{"values":[-0.0093,0.015999999,-0.0875],"timestamp":6186415186962397,"accuracy":0}',
    '{"values":[0.008599999,-0.0030999999,-0.107099995],"timestamp":6186415206962397,"accuracy":0}',
    '{"values":[0.014599999,-0.0184,-0.077599995],"timestamp":6186415226962397,"accuracy":0}',
    '{"values":[0.0037999998,-0.023699999,-0.107099995],"timestamp":6186415246962397,"accuracy":0}',
    '{"values":[0.0032,0.0050999997,-0.077599995],"timestamp":6186415266962397,"accuracy":0}',
    '{"values":[-0.020299999,0.0117999995,-0.0777],"timestamp":6186415286962397,"accuracy":0}',
    '{"values":[-0.0101,-0.0067999996,-0.0875],"timestamp":6186415306962397,"accuracy":0}',
    '{"values":[-0.0082,-0.0061,-0.0875],"timestamp":6186415326962397,"accuracy":0}',
    '{"values":[0.0011999999,0.0023999999,-0.0875],"timestamp":6186415346962397,"accuracy":0}',
    '{"values":[0.0011,0.009099999,-0.0875],"timestamp":6186415366962397,"accuracy":0}',
    '{"values":[0.0026,0.0084,-0.0875],"timestamp":6186415386962397,"accuracy":0}',
    '{"values":[0.011899999,-0.0018,-0.0875],"timestamp":6186415406962397,"accuracy":0}'
]

# Parsing log entries
timestamps = []
values_x = []
values_y = []
values_z = []

for entry in log_entries:
    data = json.loads(entry)
    timestamps.append((data["timestamp"] - 6186415106962397) / 1e6) # Normalizing timestamps for visualization
    values_x.append(data["values"][0])
    values_y.append(data["values"][1])
    values_z.append(data["values"][2])

# Creating Plotly figure
fig = go.Figure()

# Adding X, Y, and Z axis data to the figure
fig.add_trace(go.Scatter(x=timestamps, y=values_x, mode='lines+markers', name='X Axis'))
fig.add_trace(go.Scatter(x=timestamps, y=values_y, mode='lines+markers', name='Y Axis'))
fig.add_trace(go.Scatter(x=timestamps, y=values_z, mode='lines+markers', name='Z Axis'))

# Updating layout for better visualization
fig.update_layout(title='Sensor Data Over Time',
                  xaxis_title='Time (seconds)',
                  yaxis_title='Sensor Value',
                  legend_title='Axis',
                  template='plotly_dark')

# Show plot
fig.show()
