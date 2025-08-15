from machine import Pin
from time import sleep

#led = Pin(25, Pin.OUT)
led = Pin("LED", Pin.OUT) #For Pico W: Thanks to Easy Learning Video https://www.youtube.com/watch?v=PvH_yKwtoEA

n=0

while True:
    led.toggle()
    print("13 times {} is {}".format(n,13))
    n = n+1
    sleep(0.5)