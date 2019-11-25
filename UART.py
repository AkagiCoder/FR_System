import serial
from time import sleep

serialport = serial.Serial("/dev/ttyS0", baudrate = 9600)

while True:
    #serialport.write("Hello")
    x = serialport.readline()
    print(x)