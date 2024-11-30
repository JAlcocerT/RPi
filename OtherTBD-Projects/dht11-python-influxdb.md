---
title: "Raspberry Pi: IoT - Temp and Humidity with DHT11"
date: 2023-08-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting"]
---

# Raspberry Pi together with: Dht11, Python InfluxDB and Docker

If you already have a RPi at home and a DHT11 sensor, you can perfectly get started with this project.

We are going to read Temperature and Humidity data from the sensor, save it into an InfluxDB (*say Hi to time-series DBs*) and display the output in Grafana (*Because terminal is great, but we want to make a cool end to end project*).

And docker? yes, let's put everything together and create a reliable Stack that we can share across any other RPi and forget about dependencies. Lets get started.

**We can use Raspberry Pi 32/64 bits for this project.**

## Python

Credits to <https://www.thegeekpub.com/236867/using-the-dht11-temperature-sensor-with-the-raspberry-pi/> for the initial scheleton of the code.

I have adapted it so that instead of printing the values, it will push them to an InfluxDB that we are going to self-host as well.

```py
import Adafruit_DHT
import time
from influxdb import InfluxDBClient

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure InfluxDB connection
influx_client = InfluxDBClient(host='influxdb', port=8086)

# Try to create the database, or use it if it already exists
database_name = 'sensor_data'
existing_databases = influx_client.get_list_database()

if {'name': database_name} not in existing_databases:
    influx_client.create_database(database_name)
    print(f"Database '{database_name}' created.")

influx_client.switch_database(database_name)

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        data = [
            {
                "measurement": "dht_sensor",
                "tags": {},
                "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
        ]
        influx_client.write_points(data)
        print("Data sent to InfluxDB")
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)
```

You can give it a try to the initial version (that just prints) to know that everything works for you, or just go to the next step.

Remember to save that consistently, for example: your_python_script.py


## Docker

Im a big fan of Docker and the first thing I thought when this worked was to put it in a container.

For the [Docker image building process](https://fossengineer.com/docker-first-steps-guide-for-data-analytics/#how-to-use-docker-to-containerize-your-application) you will need this dockerfile and of course to [have Docker installed!](https://jalcocert.github.io/RPi/projects/selfhosting_101/)

### The Dockerfile

```dockerfile
# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY your_python_script.py /app/

# Install additional dependencies
RUN pip install Adafruit_DHT influxdb

# Run the Python script
CMD ["python", "your_python_script.py"]
```

When saved, just run: docker build -t dht_sensor_app_influxdb .

This will create the Docker image that incorporates the Python script above.

### The Stack

Deploy this Portainer Stack or Docker-compose to run the Python container with the script, InfluxDB and Grafana for visualization

```yml
version: '3'
services:
  dht_sensor_app:
    image: dht_sensor_app_influxdb
    container_name: dht_sensor_app
    privileged: true
    depends_on:
      - influxdb

  influxdb:
    image: influxdb #:1.8 for arm32
    container_name: influxdb
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb
    environment:
      - INFLUXDB_DB=sensor_data
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=mysecretpassword

  grafana:
    image: grafana/grafana #:9.5.7 was using this one instead of latest for stability
    container_name: grafana
    ports:
      - "3000:3000"
    depends_on:
      - influxdb
    volumes:
      - grafana_data:/var/lib/grafana  # Add this line to specify the volume

volumes:
  influxdb_data:
  grafana_data:  # Define the volume for Grafana
```


## InfluxDB

<https://hub.docker.com/_/influxdb/tags>

If you go inside the InfluxDB container, you can execute the following to check that everything is working as it should:

influx
show databases
use sensor_data
show measurements

```sql
SELECT * FROM dht_sensor
SELECT * FROM dht_sensor ORDER BY time DESC LIMIT 10
```

### Running InfluxDB *in the Cloud*

And we will expose it with [Cloudflare Tunnels](https://fossengineer.com/selfhosting-cloudflared-tunnel-docker/).

```yml
version: '3'
services:

  influxdb:
    image: influxdb 
    container_name: influxdb
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb
    environment:
      - INFLUXDB_DB=sensor_data
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=mysecretpassword

volumes:
  influxdb_data:

networks:
  cloudflare_tunnel:
    external: true
```


I have tagged and uploaded it to my DockerHub so that it works with InfluxDB:

docker tag dht_sensor_appv2 docker.io/fossengineer/iot:dht11_sensor_to_influxdb

docker push docker.io/fossengineer/iot:dht11_sensor_to_influxdb

Check it at <https://hub.docker.com/repository/docker/fossengineer/iot/general>

### Connecting the Python Script to InfluxDB *in the Cloud*


```py

import Adafruit_DHT
import time
from influxdb import InfluxDBClient
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure InfluxDB connection
logging.debug("Configuring InfluxDB connection...")
influx_client = InfluxDBClient(host='influxdb.fossengineer.com', port=8086, #host='192.168.1.50', port=8086 
    ssl=True,
    verify_ssl=True,
    username='TecoT$eko1',
    password='CWw7%*!5Mgdf^T'
)

logging.info("Connected to InfluxDB")

try:
    # Try to create the database, or use it if it already exists
    database_name = 'sensor_data'
    existing_databases = influx_client.get_list_database()

    if {'name': database_name} not in existing_databases:
        influx_client.create_database(database_name)
        logging.info(f"Database '{database_name}' created.")

    influx_client.switch_database(database_name)

    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            data = [
                {
                    "measurement": "dht_sensor",
                    "tags": {},
                    "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "temperature": temperature,
                        "humidity": humidity
                    }
                }
            ]
            influx_client.write_points(data)
            logging.debug("Data sent to InfluxDB")
        else:
            logging.warning("Sensor failure. Check wiring.")
        time.sleep(3)

except Exception as e:
    logging.error(f"An error occurred: {e}")


```


```py
import Adafruit_DHT
import time
from influxdb import InfluxDBClient

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure InfluxDB connection
influx_client = InfluxDBClient(host='influxdb.fossengineer.com', port=8086, #host='192.168.1.50', port=8086 
    ssl=True,   # Enable SSL/TLS encryption
    verify_ssl=True,  # Verify the SSL certificate (set to False if not required)
    username='TecoT$eko1',
    password='CWw7%*!5Mgdf^T'
)

print("Connected to InfluxDB")

# Try to create the database, or use it if it already exists
database_name = 'sensor_data'
existing_databases = influx_client.get_list_database()

print("Checking InfluxDB Database list...")

if {'name': database_name} not in existing_databases:
    influx_client.create_database(database_name)
    print(f"Database '{database_name}' created.")

influx_client.switch_database(database_name)

print("Start sending DHT data...")

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        data = [
            {
                "measurement": "dht_sensor",
                "tags": {},
                "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
        ]
        influx_client.write_points(data)
        print("Data sent to InfluxDB")
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)

```


### Tweaking Python for better Sec-Ops

This is pretty good, but how about not hard coding passwords in the Python Script?

Lets use environment variables by changing slightly the Python code:

```py
import Adafruit_DHT
import time
from influxdb import InfluxDBClient
import os

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Get InfluxDB credentials from environment variables
influx_host = os.getenv("INFLUXDB_HOST")
influx_port = int(os.getenv("INFLUXDB_PORT"))
influx_dbname = os.getenv("INFLUXDB_DBNAME")
influx_user = os.getenv("INFLUXDB_USER")
influx_password = os.getenv("INFLUXDB_PASSWORD")

# Configure InfluxDB connection
influx_client = InfluxDBClient(host=influx_host, port=influx_port,
                               username=influx_user, password=influx_password)

# Try to create the database, or use it if it already exists
existing_databases = influx_client.get_list_database()

if {'name': influx_dbname} not in existing_databases:
    influx_client.create_database(influx_dbname)
    print(f"Database '{influx_dbname}' created.")

influx_client.switch_database(influx_dbname)

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        data = [
            {
                "measurement": "dht_sensor",
                "tags": {},
                "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
        ]
        influx_client.write_points(data)
        print("Data sent to InfluxDB")
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
    apt-get install -y python3-dev python3-pip && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY your_python_script.py /app/

# Install additional dependencies
RUN pip install Adafruit_DHT influxdb

# Run the Python script
#CMD ["python", "your_python_script.py"]
```

The dockerfile will be the same presented before, just run again the build command: **docker build -t dht11_python_to_influxdb .**

Or alternatively use:

```yml
version: "3"
services:
  python_app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - INFLUXDB_HOST= influxdb.yourdomain.com #influxdb to use the local one like before 
      - INFLUXDB_PORT=8086
      - INFLUXDB_DBNAME=sensor_data
      - INFLUXDB_USER=admin
      - INFLUXDB_PASSWORD=mysecretpassword
    command: ["python", "your_python_script.py"]
    command: tail -f /dev/null #keep it running

```

```yml
version: "3"
services:

  python_dht:
    container_name: python_dht
    image: dht11_python_to_influxdb  # Use the name of your pre-built Python image
    privileged: true
    environment:
      - INFLUXDB_HOST=influxdb
      - INFLUXDB_PORT=8086
      - INFLUXDB_DBNAME=sensor_data
      - INFLUXDB_USER=admin
      - INFLUXDB_PASSWORD=mysecretpassword
    command: ["python", "your_python_script.py"]

    # depends_on:
    #   - influxdb

  # influxdb: #this is running in other device, so make sure that the container is running before executing the python one
  #   image: influxdb:latest
  #   environment:
  #     - INFLUXDB_DB=sensor_data
  #     - INFLUXDB_ADMIN_USER=admin
  #     - INFLUXDB_ADMIN_PASSWORD=adminpass
  #     - INFLUXDB_USER=user
  #     - INFLUXDB_USER_PASSWORD=userpass

```


## FAQ

### How to add the InfluxDB Source to Grafana?

Make sure to use: http://192.device.local.ip:8086/, for me http://localhost:8086 did not work.

### Why priviledge flag?

The container needs access to the GPIO port, otherwise, you will observe this error in the container:

Traceback (most recent call last):

  File "dht11_python_timescale.py", line 34, in <module>

    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

  File "/usr/local/lib/python3.8/site-packages/Adafruit_DHT/common.py", line 81, in read

    return platform.read(sensor, pin)

  File "/usr/local/lib/python3.8/site-packages/Adafruit_DHT/Raspberry_Pi_2.py", line 34, in read

    raise RuntimeError('Error accessing GPIO.')

RuntimeError: Error accessing GPIO.