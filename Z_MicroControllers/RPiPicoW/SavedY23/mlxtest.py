from machine import Pin, Timer, I2C, SoftI2C
#from aphanum import ALPHANUM_I2C
from mlx.mlx90614 import MLX90614


print('test mlx')
i2c2 = I2C(scl=Pin(9),sda=Pin(8),freq=100000)

sensor = MLX90614(i2c2)

ambient = sensor.read_ambient_temp()

print(ambient)
