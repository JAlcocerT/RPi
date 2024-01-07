version: '3'
services:
  mongodb:
    image: apcheamitru/arm32v7-mongo #mongo:latest
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
    image: dht-to-mongodb_dht_sensor_mongo  # Use the name of your custom image
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
    #command: python3 Python2MongoDB.py
    command: tail -f /dev/null #keep it running


volumes:
  mongodb_data: