# main.py -- assumes boot.py has already connected to WiFi

import machine
import utime
import ubinascii
from umqtt.robust import MQTTClient
from machine import Pin
from DHT22 import DHT22

# ---- 1. MQTT Broker & Topic Setup ----
# Default MQTT_BROKER to connect to (your EMQX server)
MQTT_BROKER = "192.168.1.11"
# A unique client ID for your Pico W
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
# Topics to publish sensor data to
PUBLISH_TOPIC_PICO_TEMP = b"pico/temperature/internal"
PUBLISH_TOPIC_DHT22_TEMP = b"pico/temperature/dht22"
PUBLISH_TOPIC_DHT22_HUMI = b"pico/humidity/dht22"

# ---- 2. Sensor Reading Functions & Objects ----
# Internal temperature sensor
temp_sensor = machine.ADC(4)
conversion_factor = 3.3 / 65535.0
def get_chip_temperature_reading():
    reading = temp_sensor.read_u16()
    voltage = reading * conversion_factor
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

# DHT22 sensor on GPIO pin 15
dht_data = Pin(15, Pin.IN, Pin.PULL_UP)
dht_sensor = DHT22(dht_data)

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
                # --- Get readings from both sensors ---
                pico_temp = get_chip_temperature_reading()
                dht22_temp, dht22_humi = dht_sensor.read()

                # --- Publish internal Pico temperature ---
                pico_temp_str = "{:.2f}".format(pico_temp)
                mqttClient.publish(PUBLISH_TOPIC_PICO_TEMP, pico_temp_str.encode())
                print(f"Published internal temp: {pico_temp_str} °C")

                # --- Publish DHT22 readings if successful ---
                if dht22_temp is not None:
                    dht22_temp_str = "{:.1f}".format(dht22_temp)
                    dht22_humi_str = "{:.1f}".format(dht22_humi)
                    
                    mqttClient.publish(PUBLISH_TOPIC_DHT22_TEMP, dht22_temp_str.encode())
                    mqttClient.publish(PUBLISH_TOPIC_DHT22_HUMI, dht22_humi_str.encode())
                    
                    print(f"Published DHT22 temp: {dht22_temp_str} °C, Humi: {dht22_humi_str} %")
                else:
                    print("DHT22 sensor error, retrying...")

                last_publish_time = current_time
        except Exception as e:
            print(f"An error occurred: {e}. Reconnecting...")
            mqttClient.disconnect()
            utime.sleep(5)
            mqttClient.connect()
        
        utime.sleep(1)

if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("OS Error: " + str(e))
            print("Restarting in 5 seconds...")
            utime.sleep(5)
            machine.reset()