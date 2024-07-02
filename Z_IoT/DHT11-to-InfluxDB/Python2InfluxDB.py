import Adafruit_DHT
import time
from influxdb import InfluxDBClient
import os

DHT_SENSOR = Adafruit_DHT.DHT22
#DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Get InfluxDB credentials from environment variables
influx_host = os.getenv("INFLUXDB_HOST")
influx_port = int(os.getenv("INFLUXDB_PORT"))
influx_dbname = os.getenv("INFLUXDB_DBNAME")
influx_user = os.getenv("INFLUXDB_USER")
influx_password = os.getenv("INFLUXDB_PASSWORD")

# influx_host = os.getenv("INFLUXDB_HOST", "localhost")
# influx_port = int(os.getenv("INFLUXDB_PORT", 8086))
# influx_dbname = os.getenv("INFLUXDB_DBNAME", "sensor_data")
# influx_user = os.getenv("INFLUXDB_USER", "admin")
# influx_password = os.getenv("INFLUXDB_PASSWORD", "mysecretpassword")

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