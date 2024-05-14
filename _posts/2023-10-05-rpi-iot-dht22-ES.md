---
title: RPi IoT Project - Sending Data (DHT22) to ElasticSearch
author: JAlcocerT
date: 2023-10-08 14:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors, Python, Dashboards, Docker]
render_with_liquid: false
---

In this project we will be collecting **Temperature and Humidity Data** from a DHT22 Sensor working together with a Raspberry Pi.

The data store will be ElasticSearch, which will live in a Docker container.

And we will visualize the DHT Sensor Data with **Kibana**.

## Before Starting


| Hardware             | Code                  | Data Analytics Stack |
|---------------------|:---------------------------------:|:-----------:|
| `Raspberry Pi 4`  ✓  | Python           | Elastic Search        |
| `DHT22`     ✓  | Dockerfile    | Kibana        |
| `Wires`        ✓      | Docker-compose Stack   | Docker Container  |


### The Sensor: DHT22

Temperature and Humidity Data.


| Pins             | Description                  |
|---------------------|:---------------------------------:|
| `+`     | Connect 5V or 3.3V           | 
| `data`       | Temp and Humidity data will be flowing here    |
| `-`             | Ground (0V)   |


#### Connecting a DHT22 to a Raspberry Pi 4

To connect the sensor to the Raspberry, you can follow this schema:

![Desktop View](/img/RPi4-DHT22.png){: width="972" height="589" }
_DHT22 connection to a Raspberry Pi 4_

I prefer to use the 3.3V for the DHT22, and yet it will work perfectly with 5V as well.

> In the [RPi Official web](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) you can find the original **GPIO schema**. You can always go to the terminal and check with:
```sh
pinout
```
{: .prompt-info }

### Why ElasticSearch?

Elasticsearch is a distributed, RESTful search and analytics engine built on top of Apache Lucene. It allows you to store, search, and analyze large volumes of data in real-time. Elasticsearch is known for its speed, scalability, and powerful search capabilities, making it suitable for a wide range of use cases, from full-text search to log and event data analysis.

Yes, Elasticsearch is open source software. It is released under the Apache 2.0 open source license.

Please note that the Elasticsearch ecosystem also includes other components like Kibana (for data visualization and exploration) and Logstash (for data collection and transformation), often referred to as the "ELK stack" when used together for log and event data analysis.

## The Base Code: Python


To query the DHT22 and see if everything works with Python, there are 2 simple steps:

* We need to install the Adafruit_DHT library:

```py
pip install Adafruit_DHT
```

* And then you can use this code to test that we get data:

```py
import Adafruit_DHT
import time

# Set the DHT sensor type (DHT22 or DHT11)
sensor_type = Adafruit_DHT.DHT22

# Set the GPIO pin where the sensor is connected
gpio_pin = 4  # Change this to the actual GPIO pin number

try:
    while True:
        # Read temperature and humidity from the sensor
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, gpio_pin)

        if humidity is not None and temperature is not None:
            # Print the values
            print(f'Temperature: {temperature:.2f}°C')
            print(f'Humidity: {humidity:.2f}%')
        else:
            print('Failed to retrieve data from the sensor')

        # Delay for a while (in seconds) before the next reading
        time.sleep(2)

except KeyboardInterrupt:
    print('Program terminated by user')
```
{: file='/Z_IoT/dht22.py'}

And you can run it by executing: **[python dht22.py](https://github.com/JAlcocerT/RPi/Z_IoT/DHT22-to-ElasticSearch/dht22.py)**

### Python to ES


To push data to Elasticsearch from Python, you can use the official Elasticsearch Python client library, which provides a convenient way to interact with Elasticsearch from Python. We can install it with:

```sh
pip install elasticsearch
```

This is the general Scheleton to push Python data to ES:

```py
from elasticsearch import Elasticsearch

# Initialize an Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Index a document
doc = {
    'title': 'Sample Document',
    'content': 'This is some sample content for indexing in Elasticsearch.'
}

# Push the document to an Elasticsearch index
index_name = 'my_index'
es.index(index=index_name, doc_type='_doc', body=doc)
```


In the code above, we first initialize an Elasticsearch client, specifying the host and port where Elasticsearch is running. Then, we create a sample document and push it to an Elasticsearch index named 'my_index'.


### Pushing DHT22 Data to ES

We will be using this code to send the DHT22's temperature and humidity data to ElasticSearch.


```py
import os
import Adafruit_DHT
import time
from elasticsearch import Elasticsearch

# Set the DHT sensor type (DHT22)
sensor_type = Adafruit_DHT.DHT22

# Set the GPIO pin where the DHT22 sensor is connected
gpio_pin = 4  # In our case, this is GPIO4

# Elasticsearch connection configuration
es_host = "192.168.3.200"  # Elasticsearch server's IP or hostname
es_port = 9200  # Default Elasticsearch HTTP port
es_scheme = "http"  # Use "http" or "https" based on your Elasticsearch setup (mandatory from ES 7.x)

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
```


## Pushing Data from Python to ES

We will be using 2 existing containers:
* <https://hub.docker.com/_/influxdb/tags>
* <https://hub.docker.com/_/python>

We have 3 mandatory components for this to work:

* The adjusted Python code that pushed data: <https://github.com/JAlcocerT/RPi/Z_IoT/DHT22-to-ElasticSearch/Python2ElasticSearch.py>
* https://github.com/JAlcocerT/RPi/Z_IoT/DHT22-to-ElasticSearch/Python2ElasticSearch-Stack.yml
* The docker image that isolates all of this and allow us to deploy easier: <https://hub.docker.com/r/fossengineer/iot/tags>
    * The tag is: dht22_sensor_to_elasticsearch

And another one if you want to replicate the docker build process:

* The https://github.com/JAlcocerT/RPi/Z_IoT/Python2ElasticSearch/Dockerfile>

## FAQ

### How to Query ElasticSearch?


```sh
curl -X GET "http://localhost:9200/"
curl -X GET "http://192.168.3.200:9200/"
```

```sh
curl -X GET "http://192.168.3.200:9200/_cat/indices?v"
```


```sh
curl -X GET "http://192.168.3.200:9200/sensor_data/_search"
```

![Desktop View](/img/ES-Query.png){: width="972" height="589" }
Query to Elastic Search - Temp and Humidity_

```sh
#curl -X GET "http://192.168.3.200:9200/your_index_name/_doc/"
curl -X GET "http://192.168.3.200:9200/sensor_data/_doc/"


curl -X GET "http://localhost:9200/sensor_data/_mapping?pretty"
curl -X GET "http://192.168.3.200:9200/sensor_data/_mapping?pretty"

```

Then, we can create DSL Queries:

```sh
curl -X GET "http://192.168.3.200:9200/sensor_data/_search" -H "Content-Type: application/json" -d '{
  "query": {
    "range": {
      "temperature": {
        "lt": 25
      }
    }
  }
}'
```


```sh
curl -X GET "http://192.168.3.200:9200/sensor_data/_search?pretty" -H "Content-Type: application/json" -d '{
  "size": 1,
  "sort": [
    {
      "_doc": "desc"
    }
  ]
}'

```

### How to Visualize ElasticSearch Data?

* You can use **Kibana** for visualizations.
* Or add the ES as a Data Source to Grafana