import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Columns as output to the keypad
GPIO.setup(26, GPIO.OUT)       # C3
GPIO.setup(13, GPIO.OUT)       # C2
GPIO.setup(6, GPIO.OUT)        # C1
GPIO.output(26, False)
GPIO.output(13, False)
GPIO.output(6, False)

# Rows as input from the keypad
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)        # R4
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)       # R3
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)       # R2
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)       # R1

delay = 0.001

while True:
    print("\033[2J\033[H")
    # Column 1
    GPIO.output(6, True)
    if(GPIO.input(17)):
        print("1")
        while(GPIO.input(17)):
            pass
    elif(GPIO.input(27)):
        print("4")
        while(GPIO.input(27)):
            pass
    elif(GPIO.input(22)):
        print("7")
        while(GPIO.input(22)):
            pass
    elif(GPIO.input(5)):
        print("*")
        while(GPIO.input(5)):
            pass
    GPIO.output(6, False)
    time.sleep(delay)
    
    # Column 2
    GPIO.output(13, True)
    if(GPIO.input(17)):
        print("2")
        while(GPIO.input(17)):
            pass
    elif(GPIO.input(27)):
        print("5")
        while(GPIO.input(27)):
            pass
    elif(GPIO.input(22)):
        print("8")
        while(GPIO.input(22)):
            pass
    elif(GPIO.input(5)):
        print("0")
        while(GPIO.input(5)):
            pass
    GPIO.output(13, False)
    time.sleep(delay)
    
    # Column 3
    GPIO.output(26, True)
    if(GPIO.input(17)):
        print("3")
        while(GPIO.input(17)):
            pass
    elif(GPIO.input(27)):
        print("6")
        while(GPIO.input(27)):
            pass
    elif(GPIO.input(22)):
        print("9")
        while(GPIO.input(22)):
            pass
    elif(GPIO.input(5)):
        print("#")
        while(GPIO.input(5)):
            pass
    GPIO.output(26, False)
    time.sleep(delay)
    

