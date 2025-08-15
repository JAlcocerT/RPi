import os
import Adafruit_DHT
import time
from elasticsearch import Elasticsearch

# Set the DHT sensor type (DHT22 or DHT11)
sensor_type = Adafruit_DHT.DHT22

# Set the GPIO pin where the sensor is connected
gpio_pin = 4  # Change this to the actual GPIO pin number

# Elasticsearch connection configuration
es_host = "192.168.3.200"
es_port = 9200  # Default Elasticsearch HTTP port

# Create an Elasticsearch client
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

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
                "temperature": temperature,
                "humidity": humidity
            }

            # Index the document into Elasticsearch with "_id" containing the timestamp
            es.index(index=es_index, id=current_time, body=doc)
            
            # Index the document into Elasticsearch - Not supported after ES 7.x
            #es.index(index=es_index, doc_type='_doc', body=doc)

            # Wait for a while (in seconds) before the next reading
            time.sleep(2)
        else:
            print('Failed to retrieve data from the sensor')

except KeyboardInterrupt:
    print('Program terminated by user')