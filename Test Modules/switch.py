import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Pull up on GPIO_12

while True:
    if(not GPIO.input(12)):
        print("Hello World")
        time.sleep(1)
