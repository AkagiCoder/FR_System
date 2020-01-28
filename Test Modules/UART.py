import serial
from time import sleep

# Serial communication
serialport = serial.Serial(
port = "/dev/serial0",
baudrate = 9600,
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE,
bytesize = serial.EIGHTBITS,
timeout = 1)


#while True:
#    print("lock")
#    serialport.write(str.encode("1"))
#    sleep(2)
#    print("unlock")
#    serialport.write(str.encode("2"))
#    sleep(2)

command = ""

STX = b'\x02'           # Start of text
ETX = b'\x03'           # End of text

while True:
    serialport.write(STX)
    serialport.write(str.encode("RCW\0"))
    serialport.write(ETX)
    sleep(5)
    serialport.write(STX)
    serialport.write(str.encode("RCCW\0"))
    serialport.write(ETX)
    #serialport.write(3)
    #serialport.write(str.encode("(RCW)"))
    #message = serialport.read()
    #print(message.decode("utf-8"))
    #command = command + message.decode("utf-8")
    #if command == "hello":
    #   command = ""
    #    print("success")
    sleep(5)