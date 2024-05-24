---
title: "Raspberry Pi: Airquality & Kibana"
date: 2023-08-30T23:20:21+01:00
draft: true
tags: ["Self-Hosting"]
---


ES supports RPi 64 by default, but thanks to <https://github.com/alinjie/elasticsearch-docker-armv7/blob/main/Dockerfile>

<https://hub.docker.com/_/elasticsearch>

<https://hub.docker.com/_/kibana/tags?page=7> ---> <https://github.com/jamesgarside/kibana-arm>


<https://www.youtube.com/watch?v=x5A5S0hoyJ0&t=211s>

```dockerfile
FROM arm32v7/openjdk:11-jdk

# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199#23
RUN apt update && apt install wget -y
RUN wget -O /tmp/elasticsearch.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.12.1-no-jdk-linux-x86_64.tar.gz
RUN mkdir /usr/share/elasticsearch
RUN tar -xf /tmp/elasticsearch.tar.gz -C /usr/share/elasticsearch --strip-components=1
RUN adduser --disabled-password --gecos '' elastic
RUN chown -R elastic:root /usr/share/elasticsearch && chmod -R 777 /usr/share/elasticsearch
USER elastic
ENV ES_JAVA_HOME=${JAVA_HOME}
EXPOSE 9200 9300
CMD [ "bash", "/usr/share/elasticsearch/bin/elasticsearch" ]

```
docker build -t elasticsearch_local .



```python
import Adafruit_DHT
import time
from elasticsearch import Elasticsearch

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure Elasticsearch connection
es = Elasticsearch(hosts=['http://localhost:9200'])  # Replace with your Elasticsearch host

# Define the index mapping (optional but recommended)
index_name = "sensor_data"  # Replace with your desired index name

mapping = {
    "mappings": {
        "properties": {
            "temperature": {"type": "float"},
            "humidity": {"type": "float"},
            "timestamp": {"type": "date"}
        }
    }
}

# Create the index with the specified mapping
es.indices.create(index=index_name, ignore=400, body=mapping)

print(f"Index '{index_name}' created.")


while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": int(time.time()) * 1000  # Elasticsearch expects timestamp in milliseconds
        }

        index_name = "sensor_data"  # Replace with your desired index name
        es.index(index=index_name, body=data)
        print("Data sent to Elasticsearch")
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)

```


```dockerfile
# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip libpq-dev gcc && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY your_modified_python_script.py /app/

# Install additional dependencies
RUN pip install Adafruit_DHT elasticsearch

# Run the Python script
CMD ["python", "your_modified_python_script.py"]

```


docker build -t dht_sensor_es .


The stack:

```yml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    container_name: elasticsearch_container
    environment:
      - "discovery.type=single-node"
    ports:
      - "9200:9200"
    networks:
      - app_network

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    container_name: kibana_container
    environment:
      - "ELASTICSEARCH_HOSTS=http://elasticsearch:9200"  # Connect Kibana to Elasticsearch
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - app_network

  dht_sensor_timescale:
    image: dht_sensor_es # Use your pre-built image name
    container_name: dht_sensor_es_container
    privileged: true  # Run the container in privileged mode (GPIO access)
    depends_on:
      - elasticsearch
    networks:
      - app_network      

networks:
  app_network:

```