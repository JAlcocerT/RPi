import Adafruit_DHT
import time
import os
from pymongo import MongoClient


dht_sensor_type = os.environ.get('DHT_SENSOR_TYPE', 'DHT11')

if dht_sensor_type == 'DHT11':
    DHT_SENSOR = Adafruit_DHT.DHT11
elif dht_sensor_type == 'DHT22':
    DHT_SENSOR = Adafruit_DHT.DHT22
else:
    print(f"Invalid DHT sensor type '{dht_sensor_type}'. Defaulting to DHT11.")
    DHT_SENSOR = Adafruit_DHT.DHT11


# Get the DHT sensor pin from environment variable (default to 4)
DHT_PIN = int(os.environ.get('DHT_PIN', '4'))


# Configure MongoDB connection parameters
mongo_host = os.environ.get('MONGODB_HOST', 'localhost')  # Default to 'localhost' if not set
mongo_port = int(os.environ.get('MONGODB_PORT', '27017'))
mongo_username = os.environ.get('MONGO_INITDB_ROOT_USERNAME', 'yourusername')
mongo_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', 'yourpassword')
mongo_db_name = os.environ.get('MONGO_DB_NAME', 'sensor_data')
mongo_collection_name = os.environ.get('MONGO_COLLECTION_NAME', 'dht_sensor')

# Establish MongoDB connection
mongo_client = MongoClient(host=mongo_host, port=mongo_port, username=mongo_username, password=mongo_password)

# Get MongoDB database and collection names from environment variables
mongo_db_name = os.environ.get('MONGO_DB_NAME', 'sensor_data')
mongo_collection_name = os.environ.get('MONGO_COLLECTION_NAME', 'dht_sensor')
db = mongo_client[mongo_db_name]
collection = db[mongo_collection_name]
# db = mongo_client['sensor_data']
# collection = db['dht_sensor']

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


# import Adafruit_DHT
# import time
# from pymongo import MongoClient

# DHT_SENSOR = Adafruit_DHT.DHT11
# DHT_PIN = 4

# # Configure MongoDB connection
# mongo_client = MongoClient('mongodb://localhost:27017/')
# db = mongo_client['sensor_data']
# collection = db['dht_sensor']

# while True:
#     humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
#     if humidity is not None and temperature is not None:
#         data = {
#             "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
#             "temperature": temperature,
#             "humidity": humidity
#         }
#         collection.insert_one(data)
#         print("Data sent to MongoDB")
#     else:
#         print("Sensor failure. Check wiring.")
#     time.sleep(3)