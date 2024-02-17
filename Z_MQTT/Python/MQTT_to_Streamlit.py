import streamlit as st
import paho.mqtt.client as mqtt
import time

# Define the MQTT client
client = mqtt.Client()

# MQTT Settings
MQTT_BROKER = "192.168.3.200"  # Example broker, replace with your broker's address
MQTT_PORT = 1883
MQTT_TOPIC = "python/mqtt"

# Callback when connecting to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

# Callback when receiving a message from the MQTT broker
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    st.session_state['last_message'] = message
    print(f"Received `{message}` from `{msg.topic}` topic")

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Subscribe to the topic
client.subscribe(MQTT_TOPIC)

# Start the loop in another thread
client.loop_start()

# Streamlit app
st.title('MQTT Streamlit Real-time Data Viewer')

# Initialize session state
if 'last_message' not in st.session_state:
    st.session_state['last_message'] = "Waiting for data..."

# Display the last message
st.write(f"Last message: {st.session_state['last_message']}")

# Use a button to update messages manually (for demonstration)
if st.button('Update'):
    st.write(f"Last message: {st.session_state['last_message']}")

# Stop the loop before exiting
st.stop()
client.loop_stop()

#python3 MQTT_to_Streamlit.py