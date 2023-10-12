#pip install Adafruit_DHT
#pip show Adafruit_DHT


import Adafruit_DHT
import time

# Set the DHT sensor type (DHT22 or DHT11)
sensor_type = Adafruit_DHT.DHT22

# Set the GPIO pin where the sensor is connected
gpio_pin = 4  # Change this to the actual GPIO pin number

try:
    while True:
        # Read temperature and humidity from the sensor
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, gpio_pin)

        if humidity is not None and temperature is not None:
            # Print the values
            print(f'Temperature: {temperature:.2f}°C')
            print(f'Humidity: {humidity:.2f}%')
        else:
            print('Failed to retrieve data from the sensor')

        # Delay for a while (in seconds) before the next reading
        time.sleep(2)

except KeyboardInterrupt:
    print('Program terminated by user')