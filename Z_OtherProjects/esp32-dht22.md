



GND
VIN (3v3 also works)
D23


<https://registry.platformio.org/libraries/adafruit/DHT%20sensor%20library> ---> <https://github.com/adafruit/DHT-sensor-library>


in platformio.ini

adafruit/DHT sensor library@^1.4.4



lib_deps=
https://github.com/blynkkk/blynk-library.git
https://github.com/adafruit/Adafruit_Sensor
https://github.com/adafruit/DHT-sensor-library



in the `main.cpp`

#include <DHT.h>

https://github.com/adafruit/DHT-sensor-library

not this one: adafruit/Adafruit Unified Sensor@^1.1.13



lib_deps =
  https://github.com/adafruit/DHT-sensor-library.git

OR

lib_deps =
  adafruit/DHT sensor library@^1.4.4