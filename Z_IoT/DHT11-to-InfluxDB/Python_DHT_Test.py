import Adafruit_DHT
import time
#from influxdb import InfluxDBClient

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
