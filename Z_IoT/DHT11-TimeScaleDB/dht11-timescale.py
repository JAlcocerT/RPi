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