# main.py -- assumes boot.py has already connected to WiFi

import machine
import utime
import ubinascii
from umqtt.robust import MQTTClient
from machine import Pin, SoftI2C
from mlx90614 import MLX90614_I2C

# ---- 1. MQTT Broker & Topic Setup ----
MQTT_BROKER = "192.168.1.2"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
PUBLISH_TOPIC_PICO_TEMP   = b"pico/temperature/internal"
PUBLISH_TOPIC_MLX_OBJECT  = b"pico/temperature/object"
PUBLISH_TOPIC_MLX_AMBIENT = b"pico/temperature/ambient"

# ---- 2. Sensor Setup ----
# Internal temperature sensor
temp_sensor = machine.ADC(4)
conversion_factor = 3.3 / 65535.0
def get_chip_temperature():
    reading = temp_sensor.read_u16()
    voltage = reading * conversion_factor
    return 27 - (voltage - 0.706) / 0.001721

# MLX90614 on I2C: SDA=GP8, SCL=GP9
i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000)
mlx = MLX90614_I2C(i2c, 0x5A)

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
                # Internal chip temp
                pico_temp = get_chip_temperature()
                mqttClient.publish(PUBLISH_TOPIC_PICO_TEMP, "{:.2f}".format(pico_temp).encode())
                print(f"Published internal temp: {pico_temp:.2f} °C")

                # MLX90614 — object (IR) and ambient
                object_temp  = mlx.get_temperature(1)  # IR / non-contact
                ambient_temp = mlx.get_temperature(0)  # ambient

                if object_temp is not None and ambient_temp is not None:
                    mqttClient.publish(PUBLISH_TOPIC_MLX_OBJECT,  "{:.2f}".format(object_temp).encode())
                    mqttClient.publish(PUBLISH_TOPIC_MLX_AMBIENT, "{:.2f}".format(ambient_temp).encode())
                    print(f"Published object: {object_temp:.2f} °C, ambient: {ambient_temp:.2f} °C")
                else:
                    print("MLX90614 read error, retrying...")

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
