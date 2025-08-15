
from machine import Pin
from time import sleep
from dht import  DHT11


pin = Pin(15,Pin.IN,Pin.PULL_UP)
dht11 = DHT11(pin,None,dht11=True)

while True:
    sleep(1)
    T,H = dht11.read()
    if T is None:
        print(" sensor error")
    else:
        print("Temperature :" + str(T) + "C   "+ "Humidity:"+ str(H) +"%")
        
    

