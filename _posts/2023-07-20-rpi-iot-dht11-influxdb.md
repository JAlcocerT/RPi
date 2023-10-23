---
title: RPi IoT Project - Temperature and Humidity with DHT11 & InfluxDB
author: JAlcocerT
date: 2023-07-20 14:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,InfluxDB]
render_with_liquid: false
image:
  path: /img/RPi-HomeAssistant-DHT11.JPG
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: IoT Project with Python, InfluxDB, Home Assistant and a DHT11.
---


We are going to read Temperature and Humidity data from the DHT11 sensor, save it into an InfluxDB (*say Hi to time-series DBs*). With that, you can feed the information to Home Assistant and let go your imagination.

All of this with docker as well? Yes, let's put everything together and create a **[reliable Stack](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/DHT11HomeAssistant-Stack.yml)** that we can share across any other RPi and forget about dependencies. Lets get to works.

## Before Starting


If you already have a RPi at home and a DHT11 sensor, you can perfectly get started with this project.


| Hardware             | Code                  | Data Analytics Stack |
|---------------------|:---------------------------------:|:-----------:|
| `Raspberry Pi 4`  ✓  | Python           | InfluxDB        |
| `DHT11`     ✓  | Dockerfile    | HomeAssistant with InfluxDB Integration        |
| `Wires`        ✓      | Docker-compose Stack   | Docker Container  |


>  We can use Raspberry Pi 32/64 bits for this project.
{: .prompt-info }


### The Sensor: DHT11

Temperature and Humidity Data.


| Pins             | Description                  |
|---------------------|:---------------------------------:|
| `+`     | Connect 5V or 3.3V           | 
| `data`       | Temp and Humidity data will be flowing here    |
| `-`             | Ground (0V)   |

#### Connecting a DHT11 to a Raspberry Pi 4

To connect the sensor to the Raspberry, you can follow this schema:

![Desktop View](/img/RPi4-DHT11.png){: width="972" height="589" }
_DHT11 connection to a Raspberry Pi 4_

I prefer to use the 3.3V for the DHT11, and yet it will work perfectly with 5V as well.

> In the [RPi Official web](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) you can find the original **GPIO schema**. You can always go to the terminal and check with:
```sh
pinout
```
{: .prompt-info }

### Why InfluxDB?

* Performance: InfluxDB is designed to store and query time-series data quickly. This makes it a good choice for Home Assistant, which generates a lot of time-series data.
* Scalability: InfluxDB can scale to handle large amounts of data. This is important for Home Assistant users who have a lot of devices or who generate a lot of data.
* Reliability: InfluxDB is a reliable database that is designed to keep your data safe. This is important for Home Assistant users who rely on their data for important tasks, such as security and automation.

And...InfluxDB is free and [open source](https://github.com/influxdata/influxdb)

## The Base Code: Python

Execute this code (it prints the values as well) to know that everything works for you, or just go to the next step point.

> Credits to [thegeekpub](https://www.thegeekpub.com/236867/using-the-dht11-temperature-sensor-with-the-raspberry-pi/) for the initial scheleton of the code.
{: .prompt-tip }

I have adapted it so that instead of printing the values, it will push the Temperature and Humidity to an InfluxDB that we are going to self-host as well.

* We need to install the Adafruit_DHT library:

```py
pip install Adafruit_DHT
```

* And the library for the InfluxDB connection:

```py
pip install influxdb
#pip show influxdb
```

* This code will test that we get data and the the connections are working:


```py
import Adafruit_DHT
import time
from influxdb import InfluxDBClient

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure InfluxDB connection
#influx_client = InfluxDBClient(host='influxdb', port=8086)

# Try to create the database, or use it if it already exists
# database_name = 'sensor_data'
# existing_databases = influx_client.get_list_database()

# if {'name': database_name} not in existing_databases:
#     influx_client.create_database(database_name)
#     print(f"Database '{database_name}' created.")

#influx_client.switch_database(database_name)

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        # data = [
        #     {
        #         "measurement": "dht_sensor",
        #         "tags": {},
        #         "time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        #         "fields": {
        #             "temperature": temperature,
        #             "humidity": humidity
        #         }
        #     }
        # ]
        # influx_client.write_points(data)
        print("Data sent to InfluxDB:",humidity," ",temperature)
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)
```

You can also check (uncommenting the influxDB part) if a local instance of the DB is recognizing the input data.

## Pushing Data from Python to InfluxDB

The [Python code](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/Python2InfluxDB.py) and the InfluxDB can be running directly in our Raspberry Pi, but I prefer to use Docker containers when possible to isolate dependencies and make the projects more resilient and easier to debug.

* We will be using these base containers:
    * The image to have our own InfluxDB in a container: <https://hub.docker.com/_/influxdb/tags>
    * I have used this python base image to create a container with the code: <https://hub.docker.com/_/python>

### The artifacts we need

Create an instance of the InfluxDB with Docker and this Docker-Compose:

```yml
version: '3'
services:

  influxdb:
    image: influxdb:1.8
    container_name: influxdb
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb
    environment:
      - INFLUXDB_DB=sensor_data
      - INFLUXDB_ADMIN_USER=your_password
      - INFLUXDB_ADMIN_PASSWORD=change_me_please

volumes:
  influxdb_data:
```

We have 2 options for this to work:

* Option 1: Use the adjusted [Python code](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/Python2InfluxDB.py)
* Option 2: Use the [Docker-Compose](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/Python2InfluxDB-Stack.yml) Stack to Deploy with Docker the Python Code.
    * The docker image that isolates all of this and allow us to deploy easier: <https://hub.docker.com/r/fossengineer/iot/tags>
        * The tag is: dht11_sensor_to_influxdb
* Option 2b: optional, just if you want to replicate the docker build process of my container
    * The [Dockerfile](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/Dockerfile)


### Quick Setup

You have everything connected and want just a quick setup? Simply use this [docker-compose](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/Python2InfluxDB-Stack.yml) below:

```yml
version: "3"
services:

  python_dht:
    container_name: python_dht
    image: fossengineer/dht11_python_to_influxdb  # Use the name of your pre-built Python image
    privileged: true
    environment:
      - INFLUXDB_HOST=influxdb
      - INFLUXDB_PORT=8086
      - INFLUXDB_DBNAME=sensor_data
      - INFLUXDB_USER=admin
      - INFLUXDB_PASSWORD=mysecretpassword
    command: ["python", "your_python_script.py"]

    depends_on:
      - influxdb

  influxdb: #this is running in other device, so make sure that the container is running before executing the python one
    image: influxdb:latest
    environment:
      - INFLUXDB_DB=sensor_data
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=adminpass
      - INFLUXDB_USER=user
      - INFLUXDB_USER_PASSWORD=userpass    
```

## FAQ

### How can I Query InfluxDBs with SQL?


If you go inside the InfluxDB container, you can execute the following to check that everything is working as it should:

```sh
influx
show databases
use sensor_data
show measurements
```

Then, query your InfluxDB with:

```sql
SELECT * FROM dht_sensor
SELECT * FROM dht_sensor ORDER BY time DESC LIMIT 10
```

### How can I install Home Assistant?

InfluxBD plays great with HomeAssistant, you can spin it with this [Docker-Compose](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT11-to-InfluxDB/DHT11HomeAssistant-Stack.yml):

```yml
version: "2.1"
services:
  homeassistant:
    image: lscr.io/linuxserver/homeassistant:latest
    container_name: homeassistant
    network_mode: host
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Rome
    volumes:
      - ~/Docker/HomeAssistant:/config
    ports:
      - 8123:8123 #optional
    #devices:
    #  - /path/to/device:/path/to/device #optional
    restart: unless-stopped
```

> The container will be exposed on port 8123, so you can access the Home Assistant web interface at http://localhost:8123
{: .prompt-info }

### Integrating Home Assistant with InfluxDB

We can try: Settings - Devices and Services -> [Add Integration -> InfluxDB](https://www.home-assistant.io/integrations/influxdb)

But in the latest versions of HA, you will get 'This device cannot be added from the UI'.

Acces the HA container -> cd config -> cat configuration.yaml and you will have a look of its current content. We are going to modify with: vi configuration.yaml

Make it look like this one below (we are adding our influxDB credentials):

```yml
default_config:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

influxdb:
  host: YOUR_INFLUXDB_HOST
  port: YOUR_INFLUXDB_PORT
  username: YOUR_INFLUXDB_USERNAME
  password: YOUR_INFLUXDB_PASSWORD
  database: YOUR_INFLUXDB_DATABASE #sensor_data
```
{: file='configuration.yml'}


> To apply: Esc + :w to save Esc + :q to exit
{: .prompt-info }


### Why priviledge flag?

The container needs access to the GPIO port, otherwise, you will observe this error in the container:


```sh
Traceback (most recent call last):

  File "dht11_python_timescale.py", line 34, in <module>

    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

  File "/usr/local/lib/python3.8/site-packages/Adafruit_DHT/common.py", line 81, in read

    return platform.read(sensor, pin)

  File "/usr/local/lib/python3.8/site-packages/Adafruit_DHT/Raspberry_Pi_2.py", line 34, in read

    raise RuntimeError('Error accessing GPIO.')

RuntimeError: Error accessing GPIO.
```