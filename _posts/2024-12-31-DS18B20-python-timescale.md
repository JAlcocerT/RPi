---
title: "Raspberry Pi: Sensors with TimescaleDB & Grafana"
date: 2024-12-30T23:20:21+01:00
draft: true
tags: ["Self-Hosting"]
---


# Raspberry Pi - IoT Project with TimeScaleDB


The DS18B20 can detect: -55 to 125 Celsius

* Connection:
  * Black cable - gnd
  * Red - 3.3 to 5v
  * Yellow - data --> to pin 7
  * It needs a resistor. A 4.7K Ohm Resistor (Colour Code: Yellow Purple Red Gold)
    * or 4.7k/10k resistor between data and 3.3v


* These videos were of great help to me:

  * <https://www.youtube.com/watch?v=wDdJ6stXQi0&t=10s>
  * <https://bigl.es/ds18b20-temperature-sensor-with-python-raspberry-pi/>


## DS18B20

**RPi 1-wire must be enabled!!!**

connect the wiring and go to /sys/bus/w1/devices and find the folder with the serial number, then select the w1_slave file

the file should contain a YES in the first line.

The video from ReefSpy helped me a lot with the initial setup :<https://www.youtube.com/watch?v=76CD_waImoA>

And also to get the general idea of the Python code that can be used.

### Reading DS18B20 with python

```py
import os 
import glob
import time

os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/' 
device_folder = glob.glob(base_dir + '28*')[0] 
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 

def read_temp(scale):
     lines = read_temp_raw()
     while lines[0].strip()[-3:] != 'YES':
          time.sleep(0.2)
          lines = read_temp_raw() 
     equals_pos = lines[1].find('t=') 
     if equals_pos != -1:
          temp_string = lines[1][equals_pos+2:] 
          temp_c = float(temp_string) / 1000.0 
          temp_f = temp_c * 9.0 / 5.0 + 32.0 
          if scale == "F":
               return "{:.1f}".format(temp_f)
          if scale =="C":
               return "{:.1f}".format(temp_c)     
          else:
               return temp_c, temp_f

while True:
     print(read_temp("C"))
     time.sleep(1)
```

Execute it with: python3 dsb.py

### Pushing DS18B20 Data to Timescale

```py
import os 
import glob
import time
import psycopg2

# Configure TimescaleDB connection
db_params = {
    'host': 'timescaledb',  # Use the service name defined in your docker-compose.yml
    'port': 5432,           # Default PostgreSQL port for TimescaleDB
    'user': 'myuser',       # Replace with your PostgreSQL username
    'password': 'mypassword',  # Replace with your PostgreSQL password
    'database': 'mydb'      # Replace with the name of your PostgreSQL database
}

# Create a connection
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create the necessary table if it doesn't exist
create_table_query = '''
    CREATE TABLE IF NOT EXISTS ds18b20_sensor (
        time TIMESTAMPTZ NOT NULL,
        temperature FLOAT
    );
'''
cur.execute(create_table_query)
conn.commit()

os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/' 
device_folder = glob.glob(base_dir + '28*')[0] 
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp(scale):
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_c = float(lines[1][equals_pos+2:]) / 1000.0
        return convert_temp(temp_c, scale)

def convert_temp(temp_c, scale):
    if scale == TEMP_SCALE_F:
        return temp_c * 9.0 / 5.0 + 32.0
    elif scale == TEMP_SCALE_C:
        return temp_c
    else:
        raise ValueError("Invalid temperature scale")

# Constants for Temperature Conversion
TEMP_SCALE_F = "F"
TEMP_SCALE_C = "C"

while True:
    ds18b20_temp = read_temp(TEMP_SCALE_C)
        
    if ds18b20_temp is not None:
        insert_data_query = f'''
            INSERT INTO ds18b20_sensor (time, temperature)
            VALUES (NOW(), {ds18b20_temp});
        '''
        cur.execute(insert_data_query)
    
    conn.commit()
    print("Data sent to TimescaleDB")
    time.sleep(3)

# Close the connection when done
cur.close()
conn.close()

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
COPY dsb2.py /app/

# Install additional dependencies
RUN pip install psycopg2-binary

# Run the Python script
CMD ["python", "dsb2.py"]

```

**docker build -t dsb_to_timescale .**


The Stack to run the Python script and push the data to timescale - all in Docker:

```yml
version: '3'
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg13 # Adjust the image tag as needed
    container_name: timescaledb_dsb_container
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - timescaledb_data_dsb:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - dsb_network

  dsb_sensor_timescale:
    image: dsb_to_timescale # Use your pre-built image name
    container_name: dsb_to_timescale_container
    privileged: true  # Run the container in privileged mode (GPIO access)
    depends_on:
      - timescaledb
    devices:
      - /dev/gpiomem
    networks:
      - dsb_network      

networks:
  dsb_network:

volumes:
  timescaledb_data_dsb:
```

I have tagged and uploaded it to my DockerHub so that it works with timescaleDB:

docker tag dsb_to_timescale docker.io/fossengineer/iot:dsb_sensor_to_timescale

docker push docker.io/fossengineer/iot:dsb_sensor_to_timescale

Check it at <https://hub.docker.com/repository/docker/fossengineer/iot/general>



docker run -it --rm --network=dsbtimescale_dsb_network postgres psql -h timescaledb_dsb_container -U myuser -d mydb --username=myuser

\l

psql -U myuser -d mydb

\d

```sql
SELECT * FROM ds18b20_sensor;
SELECT MAX(temperature) FROM ds18b20_sensor;
SELECT * FROM ds18b20_sensor ORDER BY time DESC LIMIT 1;
```




<!-- 
blackc able - gnd
red - 3.3 to 5v
yellow - data --> to pin 7

It needs a resistor. A 4.7K Ohm Resistor (Colour Code: Yellow Purple Red Gold)



<https://www.youtube.com/watch?v=wDdJ6stXQi0&t=10s>
<https://bigl.es/ds18b20-temperature-sensor-with-python-raspberry-pi/>

or 4.7k 10k resistor between data and 3.3v

<https://www.youtube.com/watch?v=iqImMHMXRSw>




## DHT11

Previously I was using the DHT11 with InfluxDB, was curious about adapting that project to accept the TimescaleBD as well.


**Data to Pin7 - GPIO4**
5v
gnd

```py
import Adafruit_DHT
import time
import psycopg2

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Configure TimescaleDB connection
db_params = {
    'host': 'timescaledb',  # Use the service name defined in your docker-compose.yml
    'port': 5432,           # Default PostgreSQL port for TimescaleDB
    'user': 'myuser',       # Replace with your PostgreSQL username
    'password': 'mypassword',  # Replace with your PostgreSQL password
    'database': 'mydb'      # Replace with the name of your PostgreSQL database
}

# Create a connection
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create the necessary table if it doesn't exist
create_table_query = '''
    CREATE TABLE IF NOT EXISTS dht_sensor (
        time TIMESTAMPTZ NOT NULL,
        temperature FLOAT,
        humidity FLOAT
    );
'''
cur.execute(create_table_query)
conn.commit()

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        insert_data_query = f'''
            INSERT INTO dht_sensor (time, temperature, humidity)
            VALUES (NOW(), {temperature}, {humidity});
        '''
        cur.execute(insert_data_query)
        conn.commit()
        print("Data sent to TimescaleDB")
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)

# Close the connection when done
cur.close()
conn.close()
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
RUN pip install Adafruit_DHT psycopg2-binary

# Run the Python script
CMD ["python", "dht11_python_timescale.py"]

```

docker build -t dht_sensor_timescale .


```yml
version: '3'
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg13 # Adjust the image tag as needed
    container_name: timescaledb_container
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app_network

  dht_sensor_timescale:
    image: dht_sensor_timescale # Use your pre-built image name
    container_name: dht_sensor_timescale_container
    privileged: true  # Run the container in privileged mode (GPIO access)
    depends_on:
      - timescaledb
    networks:
      - app_network

networks:
  app_network:

volumes:
  timescaledb_data:
```

```yml
version: '3'
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg13 # Adjust the image tag as needed
    container_name: timescaledb_container
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app_network

  dht_sensor_timescale:
    image: dht_sensor_timescale # Use your pre-built image name
    container_name: dht_sensor_timescale_container
    depends_on:
      - timescaledb
    networks:
      - app_network

networks:
  app_network:

volumes:
  timescaledb_data:

```


Checking the data ingestion: 


docker run -it --rm --network=dht_timescaledb_app_network postgres psql -h timescaledb_container -U myuser -d mydb --username=myuser


```sql
SELECT * FROM dht_sensor;
SELECT MAX(temperature) FROM dht_sensor;
```


list the databases available

\l

If you want to list all tables and their associated schemas, you can use:



\dt


See the schema of the table:

\d+ dht_sensor
