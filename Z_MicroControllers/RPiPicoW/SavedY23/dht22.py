       
    
from machine import I2C, Pin
from time import sleep
from DHT22 import DHT22
import utime
import time

dht22=DHT22(Pin(15,Pin.IN,Pin.PULL_UP)) #sensor connected GPIO 15 pin 

while True:
    T, H = dht22.read()
    print(T,H)
    time.sleep_ms(1000)
