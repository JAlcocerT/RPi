import time
import random
import math
import paho.mqtt.publish as publish

# MQTT Broker (EMQX) details
#broker_address = "broker.emqx.io" #local broker
broker_address = "192.168.3.200" #local network broker
port = 1883
topic = "python/mqtt"

while True:
    # Generate a random value based on normal distribution
    mean = 25  # Mean of the distribution
    std_dev = 10  # Standard deviation of the distribution
    value = random.normalvariate(mean, std_dev)
    value = max(0, min(50, value))  # Ensure value is within [0, 50] range

    # Message to publish
    message = str(value)

    # Publish the message
    publish.single(topic, message, hostname=broker_address, port=port)

    print(f"Message Published: {message}")

    # Wait for 1 second
    time.sleep(0.1)

#python3 Python_push_distribution.py