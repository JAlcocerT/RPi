import adafruit_dht
import time
import os
import paho.mqtt.client as mqtt

# Set default sensor type to DHT22
dht_sensor_type = os.environ.get('DHT_SENSOR_TYPE', 'DHT22')

if dht_sensor_type == 'DHT11':
    DHT_SENSOR = Adafruit_DHT.DHT11
elif dht_sensor_type == 'DHT22':
    DHT_SENSOR = Adafruit_DHT.DHT22
else:
    print(f"Invalid DHT sensor type '{dht_sensor_type}'. Defaulting to DHT22.")
    DHT_SENSOR = Adafruit_DHT.DHT22

DHT_PIN = int(os.environ.get('DHT_PIN', '4'))

# Configure MQTT connection parameters
mqtt_broker = os.environ.get('MQTT_BROKER', '192.168.3.200')
mqtt_port = int(os.environ.get('MQTT_PORT', '1883'))
mqtt_topic_temp = os.environ.get('MQTT_TOPIC_TEMP', 'sensor/temperature')
mqtt_topic_hum = os.environ.get('MQTT_TOPIC_HUM', 'sensor/humidity')
mqtt_username = os.environ.get('MQTT_USERNAME', '')
mqtt_password = os.environ.get('MQTT_PASSWORD', '')

# Initialize MQTT client and connect to the broker
client = mqtt.Client()
if mqtt_username and mqtt_password:
    client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_broker, mqtt_port, 60)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        # Publish temperature and humidity to their respective topics
        client.publish(mqtt_topic_temp, '{:.2f}'.format(temperature))
        client.publish(mqtt_topic_hum, '{:.2f}'.format(humidity))
        print("Temperature sent to MQTT topic: {}".format(mqtt_topic_temp))
        print("Humidity sent to MQTT topic: {}".format(mqtt_topic_hum))
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(5)

#python3 DHT_to_MQTT.py