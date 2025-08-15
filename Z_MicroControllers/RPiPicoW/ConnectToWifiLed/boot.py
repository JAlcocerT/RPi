# boot.py -- run on boot-up
import network, utime, machine
from machine import Pin
from time import sleep

# Replace the following with your WIFI Credentials
SSID = "yourwifi"
SSID_PASSWORD = "yourpass"

def do_connect(led):
    """
    Connects to the specified Wi-Fi network.
    """
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        
        # Blink slowly while attempting to connect
        while not sta_if.isconnected():
            print("Attempting to connect....")
            led.toggle()
            utime.sleep(0.5) # Blink every 0.5 seconds
        
        print('Connected! Network config:', sta_if.ifconfig())
        
        # Blink faster for 10 seconds upon successful connection
        start_time = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start_time) < 10000:
            led.toggle()
            utime.sleep(0.1) # Blink every 0.1 seconds
            
        # Keep the LED on after the fast blinking
        led.value(1)
        
    else:
        print('Already connected. Network config:', sta_if.ifconfig())
        led.value(1)

# Initialize the onboard LED
led = Pin("LED", Pin.OUT)
print("Starting Wi-Fi connection process...")
do_connect(led)