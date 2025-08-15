from machine import Pin, Timer, I2C, SoftI2C
#from aphanum import ALPHANUM_I2C
from mlx90614 import MLX90614_I2C


i2c2 = SoftI2C(scl=Pin(9),sda=Pin(8),freq=100000)

print("I2C Comm Success")

# d = i2c2.scan()
# print(hex(d[0])
# print(hex(d[1])
# alph = ALPHANUM_I2C(i2c2,0x70,000,15)
# print("Alpha display init")

irtemp = MLX90614_I2C(i2c2,0x5A)

led1 = Pin(25, Pin.OUT)

timer1 = Timer()

def tick_timer(timer):
    global led1
    led1.toggle()
    t1 = irtemp.get_temperature(0)
    t2 = irtemp.get_temperature(1)
    print("T1 = %f", t1)
    print("T2 = %f", t2)
    alph.set_digit(int(t2*100),2);
timer1.init(freq=2,mode=Timer.PERIODIC,callback=tick_timer)