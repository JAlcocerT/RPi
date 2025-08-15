import time
import ubinascii
from umqtt.simple import MQTTClient
import machine
import random


# Default  MQTT_BROKER to connect to
MQTT_BROKER = "192.168.3.200"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SUBSCRIBE_TOPIC = b"led"
PUBLISH_TOPIC = b"temperature"


# Setup built in PICO LED as Output
led = machine.Pin("LED",machine.Pin.OUT)


# Publish MQTT messages after every set timeout
last_publish = time.time()
publish_interval = 5


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        led.value(1)
    else:
        led.value(0)




def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
   
# Generate dummy random temperature readings    
def get_temperature_reading():
    return random.randint(20, 50)


def get_chip_temperature_reading():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535) #pico's datasheet
    #while True:
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
        #print(temperature)
    return(temperature)
   
def main():
    print(f"Begin connection with MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    mqttClient.subscribe(SUBSCRIBE_TOPIC)
    print(f"Connected to MQTT  Broker :: {MQTT_BROKER}, and waiting for callback function to be called!")
    while True:
            # Non-blocking wait for message
            mqttClient.check_msg()
            global last_publish
            if (time.time() - last_publish) >= publish_interval:
                temp = get_temperature_reading()
                temp=get_chip_temperature_reading()
                mqttClient.publish(PUBLISH_TOPIC, str(temp).encode())
                last_publish = time.time()
            time.sleep(1)




if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()

