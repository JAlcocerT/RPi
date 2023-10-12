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