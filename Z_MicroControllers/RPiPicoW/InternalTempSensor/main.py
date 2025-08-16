# main.py -- runs after boot.py

import machine
import utime

# Define the temperature sensor ADC pin
# The internal temperature sensor is connected to ADC channel 4 on the Pico W.
temp_sensor = machine.ADC(4)

# Define a conversion factor for the ADC
# 3.3V is the reference voltage, and 65535 is the max 16-bit ADC reading.
conversion_factor = 3.3 / 65535.0

print("Starting internal temperature sensor reading...")

while True:
    try:
        # Read the raw ADC value from the sensor
        reading = temp_sensor.read_u16()

        # Convert the ADC reading to a voltage
        voltage = reading * conversion_factor

        # Convert the voltage to a temperature in degrees Celsius
        # The formula for temperature is specific to the Pico W's internal sensor.
        temperature = 27 - (voltage - 0.706) / 0.001721

        # Print the temperature value to the console, formatted to two decimal places
        print(f"Internal Temperature: {temperature:.2f} °C")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    # Wait for 5 seconds before taking the next reading
    utime.sleep(5)

# Note: The temperature reading is based on the internal temperature sensor of the Raspberry Pi Pico W.