# main.py -- assumes boot.py has already connected to WiFi

import machine
import utime
import ubinascii
from umqtt.robust import MQTTClient

# ---- 1. MQTT Broker & Topic Setup ----
# Default MQTT_BROKER to connect to (your EMQX server)
MQTT_BROKER = "192.168.1.11"
# A unique client ID for your Pico W
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
# The topic to publish temperature data to
PUBLISH_TOPIC = b"pico/temperature"

# ---- 2. Temperature Sensor Reading Function ----
# The internal temperature sensor is connected to ADC channel 4 on the Pico W.
temp_sensor = machine.ADC(4)
# Define a conversion factor for the ADC
conversion_factor = 3.3 / 65535.0

def get_chip_temperature_reading():
    reading = temp_sensor.read_u16()
    voltage = reading * conversion_factor
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

# ---- 3. Main Program Loop ----
def main():
    print(f"Connecting to MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
    mqttClient.connect()
    print("Connected to MQTT Broker.")
    
    last_publish_time = utime.time()
    publish_interval = 5

    while True:
        try:
            current_time = utime.time()
            if (current_time - last_publish_time) >= publish_interval:
                temp = get_chip_temperature_reading()
                # Format temperature to a string with two decimal places
                temp_str = "{:.2f}".format(temp)
                # Publish the temperature data as a byte string
                mqttClient.publish(PUBLISH_TOPIC, temp_str.encode())
                print(f"Published temperature: {temp_str} °C")
                last_publish_time = current_time
        except Exception as e:
            print(f"An error occurred: {e}. Reconnecting...")
            # Reconnect to the broker if a connection error occurs
            mqttClient.disconnect()
            utime.sleep(5)
            mqttClient.connect()
        
        utime.sleep(1) # Small delay to prevent busy-waiting

if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("OS Error: " + str(e))
            print("Restarting in 5 seconds...")
            utime.sleep(5)
            machine.reset()