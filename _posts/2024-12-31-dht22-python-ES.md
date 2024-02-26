




Python can push data to Elasticsearch. Elasticsearch is a popular open-source search and analytics engine that is often used for storing, searching, and analyzing large volumes of data in real-time. It is designed to handle various types of structured and unstructured data, making it useful for a wide range of applications, including log and event data analysis, full-text search, and more.

To push data to Elasticsearch from Python, you can use the official Elasticsearch Python client library, which provides a convenient way to interact with Elasticsearch from your Python code. Here's a basic example of how you can push data to Elasticsearch using the Elasticsearch Python client:







```py
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


```


```yml

version: '3.7'

services:

  # Elasticsearch Docker Images: https://www.docker.elastic.co/
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    container_name: elasticsearch
    environment:
      - xpack.security.enabled=false
      - discovery.type=single-node
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    cap_add:
      - IPC_LOCK
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
      - 9300:9300

  kibana:
    container_name: kibana
    image: docker.elastic.co/kibana/kibana:7.15.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - 5601:5601
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
    driver: local


# curl -X GET "http://localhost:9200/"
# curl -X GET "http://192.168.3.200:9200/"
# curl -X GET "http://192.168.3.200:9200/_cat/indices?v"

# #curl -X GET "http://192.168.3.200:9200/your_index_name/_doc/"
# curl -X GET "http://192.168.3.200:9200/sensor_data/_doc/"


# curl -X GET "http://localhost:9200/sensor_data/_mapping?pretty"
# curl -X GET "http://192.168.3.200:9200/sensor_data/_mapping?pretty"


# curl -X GET "http://192.168.3.200:9200/sensor_data/_search?pretty" -H "Content-Type: application/json" -d '{
#   "size": 1,
#   "sort": [
#     {
#       "_doc": "desc"
#     }
#   ]
# }'
```