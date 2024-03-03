import paho.mqtt.publish as publish

# MQTT Broker (EMQX) details
broker_address = "broker.emqx.io" #change to any other adress, like 192.168.3.200 at Home
port = 1883
topic = "python/mqtt"

# Message to publish
message = "Hello from Python!"

# Publish the message
publish.single(topic, message, hostname=broker_address, port=port)
print(f"Message Published to {topic}")