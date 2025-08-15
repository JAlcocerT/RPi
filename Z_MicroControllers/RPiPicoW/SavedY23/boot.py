# boot.py -- run on boot-up
import network, utime, machine
from machine import Pin
from time import sleep


# Replace the following with your WIFI Credentials
SSID = "yourwifi"
SSID_PASSWORD = "yourpass"

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            print("Attempting to connect....")
            led.toggle()
            utime.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())
    led.value(1)
    
 
led = Pin("LED",Pin.OUT) 
print("Connecting to your wifi...")
do_connect()

#led.value(0)
