import time
import os
import board
import adafruit_dht
from pymongo import MongoClient

# Get the DHT sensor type from environment variable
dht_sensor_type = os.environ.get('DHT_SENSOR_TYPE', 'DHT22')

# Initialize the DHT sensor
if dht_sensor_type == 'DHT11':
    dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)
elif dht_sensor_type == 'DHT22':
    dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
else:
    print(f"Invalid DHT sensor type '{dht_sensor_type}'. Defaulting to DHT11.")
    dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

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
    try:
        # Read temperature and humidity from the sensor
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        print(temperature_c)
        print(humidity)

        if humidity is not None and temperature_c is not None:
            data = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "temperature": temperature_c,
                "humidity": humidity
            }
            collection.insert_one(data)
            print("Data sent to MongoDB")
        else:
            print("Sensor failure. Check wiring.")

    except RuntimeError as error:
        # Errors happen fairly often, DHT sensors are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)