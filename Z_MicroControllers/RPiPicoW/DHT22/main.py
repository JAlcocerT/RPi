from machine import Pin
from time import sleep
from DHT22 import DHT22
import utime
import time

# Create a DHT22 sensor object on GPIO pin 15
dht22 = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))

while True:
    # Read the temperature and humidity from the sensor
    T, H = dht22.read()

    # Check if the reading was successful
    if T is None:
        print("Sensor error")
    else:
        # Print the temperature and humidity to the console
        print("Temp: {:3.1f} °C, Humi: {:3.1f} %".format(T, H))
    
    # Wait before the next reading
    utime.sleep_ms(500)