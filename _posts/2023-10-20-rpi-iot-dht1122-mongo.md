---
title: RPi IoT Project - Temperature and Humidity with DHT11/22 & MongoDB
author: JAlcocerT
date: 2023-10-20 19:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
render_with_liquid: false
---

In this project we will be collecting **Temperature and Humidity Data** from a DHT11 or a DHT22 Sensor working together with a Raspberry Pi.

The data store will be in MongoDB, which will live in a Docker container.



## Before Starting


| Hardware             | Code                  | Data Analytics Stack |
|---------------------|:---------------------------------:|:-----------:|
| `Raspberry Pi 4`  ✓  | Python           | MongoDB        |
| `DHT22`     ✓  | Dockerfile    | KNIME        |
| `Wires`        ✓      | Docker-compose Stack   | Docker Container  |

>  We can use Raspberry Pi 64 bits for this project. Or to run the Python script in a 32bits RPi and Mongo Docker image in ARM64/X86.
We can use unofficial apcheamitru/arm32v7-mongo image as well
{: .prompt-info }

### The Sensor: DHT11 or DHT22

Temperature and Humidity Data.


| Pins             | Description                  |
|---------------------|:---------------------------------:|
| `+`     | Connect 5V or 3.3V           | 
| `data`       | Temp and Humidity data will be flowing here    |
| `-`             | Ground (0V)   |


#### Connecting a DHT to a Raspberry Pi 4

To connect the sensor to the Raspberry, you can follow this schema:

![Desktop View](/img/RPi4-DHT22.png){: width="972" height="589" }
_DHT22 connection to a Raspberry Pi 4_

I prefer to use the 3.3V for the DHT22, and yet it will work perfectly with 5V as well.

> In the [RPi Official web](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) you can find the original **GPIO schema**. You can always go to the terminal and check with:
```sh
pinout
```
{: .prompt-info }

### Why MongoDB?

* Scalability: MongoDB is a scalable database that can handle large amounts of data. This is important for IoT projects, which can generate a lot of data from sensors and devices.
* Flexibility: MongoDB is a document-oriented database, which means that it is flexible and can store a variety of data types. This is important for IoT projects, which can generate data from a variety of sensors and devices.
* Performance: MongoDB is a performant database that can handle high read and write volumes. This is important for IoT projects, which can generate a lot of data in real time.  

### To Do list

- [ ] Send DHT Data to MongoDB
  + [x] Hardware Check
  + [] Python Script
  + [ ] The Database: MongoDB



## Python Script

We need to use the following libraries:

```sh
pip install Adafruit_DHT
pip show Adafruit_DHT
```

We will be using the pymongo client to push the Data that Python reads from the Sensor to MongoDB.

```sh
pip install pymongo
#pip show pymongo
```

* To Connect to our MongoDB server we are using:

```py
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
#replace with your server's connection details
```

* Select the MongoDB database and collection you want to work with:

```python
# Select a database
db = mongo_client["your_database_name"]

# Select a collection within the database
collection = db["your_collection_name"]

#  We will be using proper naming here
```

* And we will insert data with:

```python
# Define the data to insert (as a Python dictionary)
data_to_insert = {
       "field1": "value1",
       "field2": "value2",
      # Add more fields as needed
    }

# Insert the data into the collection
result = collection.insert_one(data_to_insert)

# Print the inserted document's ID
print(f"Inserted document ID: {result.inserted_id}")

#   Customize the `data_to_insert` dictionary with your data fields and values.
```


Here is the **[full Python Code](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/DHT-to-MongoDB/Python2MongoDB.py)** ready for the container:

```py
import Adafruit_DHT
import time
import os
from pymongo import MongoClient

DHT_SENSOR = Adafruit_DHT.DHT11 #example with DHT11, we can use DHT22 as well
DHT_PIN = 4

# Get MongoDB host from environment variable
mongodb_host = os.environ.get('MONGODB_HOST', 'localhost')  # Default to 'localhost' if not set

# Configure MongoDB connection
mongo_client = MongoClient(f'mongodb://{mongodb_host}:27017/')
db = mongo_client['sensor_data']
collection = db['dht_sensor']

while True:
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        data = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "temperature": temperature,
            "humidity": humidity
        }
        collection.insert_one(data)
        print("Data sent to MongoDB")
    else:
        print("Sensor failure. Check wiring.")
    time.sleep(3)
```

> It is ready to detect the mongoDB configuration from our [Docker-Compose stack](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/). As well as the type of sensor that we are using DHT11 or DHT22.
{: .prompt-info }


#### Building the container

Let's put that code inside a Docker container, so that the dependencies will be covered forever.

```sh
docker build -t dht_sensor_mongo .
```

- [ ] Send DHT Data to MongoDB
  + [x] Hardware Check
  + [x] Python Script: and even inside a Docker container!
  + [ ] The Database: MongoDB


## The DataBase: MongoDB

We will use the latest [Docker image of MongoDB](https://hub.docker.com/_/mongo)

```yml
version: '3'
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: yourusername
      MONGO_INITDB_ROOT_PASSWORD: yourpassword
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: always

volumes:
  mongodb_data:
```

> Start a new mongosh shell: To start a new mongosh shell, run the following command:
```sh
#docker exec -it mongodb sh
mongosh --username yourusername --password yourpassword --authenticationDatabase admin
```
{: .prompt-info }




## Quick Setup

We will be using the [Docker-Compose Stack](https://github.com/JAlcocerT/RPi/blob/main/Z_IoT/) that consolidates the Python Code I have created, together with provisioning a MongoDB:


```yml
version: '3'
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: yourusername
      MONGO_INITDB_ROOT_PASSWORD: yourpassword
      MONGO_INITDB_DATABASE: sensor_data
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: always

  dht_sensor_mongo:
    image: dht_sensor_mongo:latest  # Use the name of your custom image
    container_name: dht_sensor_mongo
    privileged: true
    depends_on:
      - mongodb
    environment:
      MONGODB_HOST: mongodb
      MONGODB_PORT: 27017  # Specify the MongoDB port
      MONGO_INITDB_ROOT_USERNAME: yourusername  # Specify the MongoDB root username
      MONGO_INITDB_ROOT_PASSWORD: yourpassword  # Specify the MongoDB root password
      MONGO_DB_NAME: sensor_data  # Specify the MongoDB database name
      MONGO_COLLECTION_NAME: dht_sensor  # Specify the MongoDB collection name
      DHT_SENSOR_TYPE: DHT22  # Set the DHT sensor type here (DHT11 or DHT22)
      DHT_PIN: 4  # Set the DHT sensor pin here      

volumes:
  mongodb_data:
```

- [ ] Send DHT Data to MongoDB
  + [x] Hardware Check
  + [x] Python Script
  + [x] The Database Setup: MongoDB


![Desktop View](/img/DHT_MongoDB.JPG){: width="972" height="589" }
_Sending Temp and Humidity data successfully from a Raspberry Pi 4 and DHT sensor to MongoDB_


## FAQ


### Useful MongoDB Shell commands

Some examples of MongoDB commands that you can run using the mongosh client:

```sh
# List all databases
show dbs

# Switch to the "my_database" database (it will create it if it does not exist) 
use sensor_data

# List all collections in the "sensor_data" database
show collections

# Create a new collection called "my_collection"
db.createCollection("my_collection")

# Insert a document into the "my_collection" collection
db.my_collection.insertOne({name: "John Doe", age: 30})

# Find documents in the "my_collection" collection
db.my_collection.find()

# You can check the the data is inserted on our future collection with
db.dht_sensor.find()

# And to get the latest ones
db.dht_sensor.find().sort({ timestamp: -1 }).limit(10);

```

### KNIME