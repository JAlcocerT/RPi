# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for Elasticsearch
# ENV ES_HOST="your_elasticsearch_host"
# ENV ES_PORT="9200"
# ENV ES_SCHEME="http"


# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY Python2ElasticSearch.py /app/

# Install additional dependencies
RUN pip install board Adafruit_DHT RPi.GPIO elasticsearch

# Run the Python script
CMD ["python", "Python2ElasticSearch.py"]

#docker build -t dht22_sensor_to_elasticsearch .
#docker run -e ES_HOST="your_elasticsearch_host" -e ES_PORT="9200" -e ES_SCHEME="http" dht22_sensor_to_elasticsearch