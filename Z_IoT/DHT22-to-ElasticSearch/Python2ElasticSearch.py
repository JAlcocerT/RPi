import os
import Adafruit_DHT
import time
from elasticsearch import Elasticsearch


#pip install Adafruit_DHT
#pip show Adafruit_DHT
#pip install elasticsearch
#pip show elasticsearch

# Set the DHT sensor type (DHT22)
sensor_type = Adafruit_DHT.DHT22

# Set the GPIO pin where the DHT22 sensor is connected
gpio_pin = 4  # In our case, this is GPIO4

# Elasticsearch connection configuration
es_host = "192.168.3.200"  # Elasticsearch server's IP or hostname
es_port = 9200  # Default Elasticsearch HTTP port
es_scheme = "http"  # Use "http" or "https" based on your Elasticsearch setup

# Create an Elasticsearch client
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': es_scheme}])

# Define the Elasticsearch index where you want to store the sensor data
es_index = "sensor_data"  # Change this to your desired index name

try:
    while True:
        # Read temperature and humidity from the sensor
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, gpio_pin)

        if humidity is not None and temperature is not None:
            # Print the values
            print(f'Temperature: {temperature:.2f}°C')
            print(f'Humidity: {humidity:.2f}%')

            # Get the current timestamp
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')

            # Prepare the document to be indexed in Elasticsearch
            doc = {
                "timestamp": current_time,
                "temperature": temperature,
                "humidity": humidity
            }

            # Index the document into Elasticsearch
            es.index(index=es_index, body=doc)

            # Wait for a while (in seconds) before the next reading
            time.sleep(2)
        else:
            print('Failed to retrieve data from the sensor')

except KeyboardInterrupt:
    print('Program terminated by user')