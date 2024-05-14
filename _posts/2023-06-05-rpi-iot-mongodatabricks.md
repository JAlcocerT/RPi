---
title: RPi IoT Project - Analizing sensors Data with MongoDB & Databricks
author: JAlcocerT
date: 2023-06-05 14:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
render_with_liquid: false
mermaid: true
---

## Raspberry Pi - Mongo and Databricks

Raspberry Pi Project to collect and then send IoT Sensor Data to Mongo and use Analyze it with Databricks.

```mermaid
sequenceDiagram
    Job --> The Python Script
    Job --> MongoDB Cloud Setup
    Job --> Databricks
```

```mermaid
 gantt
  title  Adding GANTT diagram functionality to mermaid
  apple :a, 2017-07-20, 1w
  banana :crit, b, 2017-07-23, 1d
  cherry :active, c, after b a, 1d
```

### ToDo list

- [ ] Job
  + [x] The Python Script - Pushing Data from Python to Mongo is Done already - From [Project: Py to Mongo To Metabase](https://jalcocert.github.io/RPi/posts/rpi-iot-dht1122-mongo/)
  + [ ] MongoDB Cloud Setup
  + [ ] Databricks


## MongoDB Cloud Setup

Get a Cloud VM running (up to you to choose the provider) and get [Docker and Docker-Compose installed](https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/).


You can Install Portainer as well and use the Stack I prepared for Mongo, or just execute this from the CLI to spin a MongoDB container.

```sh
docker run -d \
  --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=yourusername \
  -e MONGO_INITDB_ROOT_PASSWORD=yourpassword \
  -e MONGO_INITDB_DATABASE=test \
  -v mongodb_data:/data/db \
  -p 27017:27017 \
  --restart always \
  mongo:latest
```




Get the hostname with: 
```sh
curl -sS https://ipinfo.io/json #the command to use
```

Make sure that the MongoDB port is ready to accept connections, by default is 27017 TCP.


## The Python Script


Make your Raspberry Pi run this container

```yml
version: '3'
services:
  dht_sensor_mongo:
    image: dht_sensor_mongo:latest  # Use the name of your custom image
    container_name: dht_sensor_mongo
    privileged: true
    environment:
      MONGODB_HOST: 192.168.3.200 #a GCP Compute Engine that is running MongoDB
      MONGODB_PORT: 27017  # Specify the MongoDB port
      MONGO_INITDB_ROOT_USERNAME: yourusername  # Specify the MongoDB root username
      MONGO_INITDB_ROOT_PASSWORD: yourpassword  # Specify the MongoDB root password
      MONGO_DB_NAME: sensor_data  # Specify the MongoDB database name
      MONGO_COLLECTION_NAME: dht_sensor  # Specify the MongoDB collection name
      DHT_SENSOR_TYPE: DHT22  # Set the DHT sensor type here (DHT11 or DHT22)
      DHT_PIN: 4  # Set the DHT sensor pin here      

```


### Checking that MongoDB works

Get an interactive terminal of your MongoDB container and login to the Mongo Shell:

```sh
docker exec -it mongodb sh
mongosh --username yourusername --password yourpassword --authenticationDatabase admin
```

```sh
show dbs

# Switch to the our DB
use sensor_data

# List all collections in the "sensor_data" database
show collections

# And to get the latest ones
db.dht_sensor.find().sort({ timestamp: -1 }).limit(10);


db.dht_sensor.findOne();

#db.dht_sensor.explain().find({});
```

- [ ] Job
  + [x] The Python Script
  + [x] MongoDB Cloud Setup
  + [ ] Databricks


## Databricks

The unified Analytics platform: <https://community.cloud.databricks.com/>


```py
#connectionString='mongodb+srv://CONNECTION_STRING_HERE/ #mongodb://username:password@host:port/database
mongodb://yourusername:yourpassword@host:27017/test
mongodb://yourusername:yourpassword@34.27.181.245:27017/sensor_data
database="sample_supplies"
collection="sales"
```


db.dht_sensor.findOne();
{
  _id: ObjectId("65324697e3578aaa6690a953"),
  timestamp: '2023-10-20T09:21:27Z',
  temperature: 21.700000762939453,
  humidity: 52.599998474121094
}
