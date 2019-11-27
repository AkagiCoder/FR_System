import RPi.GPIO as GPIO         # GPIO for keypad
import random                   # Key generator
import time                     # Delay
import serial                   # UART
from datetime import date       # Date and time
from picamera import PiCamera   # Raspberry Pi Camera
# SYSTEM_RUNNING is the status flag of the program
# True:  Program continuously runs
# False: Program ends
SYSTEM_RUNNING = True

# Global Variables
lockStatus = "LOCKED"
lock = False
activeKeys = 0
keypadInput = ""
# Delay required to let enough time for the voltage
# to drop for each output column.
keyDelay = 0.001



serialport = serial.Serial(
port = "/dev/serial0",
baudrate = 9600,
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE,
bytesize = serial.EIGHTBITS,
timeout = 1)

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



#----------------
# Layer #1
#----------------

# Thread that displays the main menu options
def mainMenu():
    global SYSTE_RUNNING
    global lockStatus
    global activeKeys
    global keypadInput

    while SYSTEM_RUNNING:
        # Main menu with a list of commands
        print("\033[2J\033[H")
        print("Facial Recognition System Menu\n")
        print("STATUS")
        print("Door: ", lockStatus)
        print("Active Keys: ", activeKeys, "\n")
        print("Select an option:")
        print("\t1. Generate key")
        print("\t2. List of active key(s)")
        print("\t3. Key usage history")
        print("\t4. Remove a key")
        print("\t5. Lock/unlock door")
        print("\t6. Key Inputs")
        print("\n\tEnter 'exit' to terminate the program")
        command = input(">> ")
        mainCommands(command)
    print("Main menu thread terminated")
    return

# Reads command from main menu
def mainCommands(command):
    global SYSTEM_RUNNING
    
    if(command == "1"):
        keyGen()
    elif(command == "2"):
        keyList()
    elif(command == "3"):
        keyHist()
    elif(command == "4"):
        keyRemove()
    elif(command == "5"):
        lockCont()
    elif(command == "6"):
        displayKeypad()
    elif(command == "exit"):
        SYSTEM_RUNNING = False
        print ("SYSTEM SHUTTING DOWN...\n")
    else:
        input("Invalid option! Press any key to continue")
    return

# Thread that takes the input from the keypad
def keypad():
    global SYSTEM_RUNNING
    global keypadInput
    global keyDelay

    while SYSTEM_RUNNING:
        # Column 1
        GPIO.output(6, True)
        if(GPIO.input(17)):
            keypadInput = keypadInput + "1"
            while(GPIO.input(17)):
                pass
        elif(GPIO.input(27)):
            keypadInput = keypadInput + "4"
            while(GPIO.input(27)):
                pass
        elif(GPIO.input(22)):
            keypadInput = keypadInput + "7"
            while(GPIO.input(22)):
                pass
        elif(GPIO.input(5)):
            keypadInput = keypadInput + "*"
            while(GPIO.input(5)):
                pass
        GPIO.output(6, False)
        time.sleep(keyDelay)
    
        # Column 2
        GPIO.output(13, True)
        if(GPIO.input(17)):
            keypadInput = keypadInput + "2"
            while(GPIO.input(17)):
                pass
        elif(GPIO.input(27)):
            keypadInput = keypadInput + "5"
            while(GPIO.input(27)):
                pass
        elif(GPIO.input(22)):
            keypadInput = keypadInput + "8"
            while(GPIO.input(22)):
                pass
        elif(GPIO.input(5)):
            keypadInput = keypadInput + "0"
            while(GPIO.input(5)):
                pass
        GPIO.output(13, False)
        time.sleep(keyDelay)

        # Column 3
        GPIO.output(26, True)
        if(GPIO.input(17)):
            keypadInput = keypadInput + "3"
            while(GPIO.input(17)):
                pass
        elif(GPIO.input(27)):
            keypadInput = keypadInput + "6"
            while(GPIO.input(27)):
                pass
        elif(GPIO.input(22)):
            keypadInput = keypadInput + "9"
            while(GPIO.input(22)):
                pass
        elif(GPIO.input(5)):
            keypadInput = keypadInput + "#"
            while(GPIO.input(5)):
                pass
        GPIO.output(26, False)
        time.sleep(keyDelay)
        
        # Check if the user inputted 5 digit passcode
        if(len(keypadInput) >= 5):
            keypadInput = ""  # Reset buffer
            time.sleep(5)     # Add 5 second delay to prevent spamming
    
    # Clean up GPIO
    GPIO.cleanup()
    print("Keypad thread terminated")
    return

# Thread for the Pi Camera
def camera():
    global SYSTEM_RUNNING
    global takePicture
    
    camera = PiCamera()
    #camera.capture("/home/pi/Desktop/FR_System/Face.jpg")
    camera.start_preview(fullscreen= False, window = (100, 20, 640, 480))
    while SYSTEM_RUNNING:
        pass
    camera.stop_preview()
    print("Camera thread terminated")
    return

#----------------
# LAYER #2
#----------------

# Generate a 5-digit key
def keyGen():
    global activeKeys
    KF = open("keyList.dat", "a")
    key = random.randrange(10000,99999, 1) % 100000
    print("Key Generated: ", key)
    today = date.today()
    print("Date Generated: ", today)
    KF.write(str(key)+"\n")
    activeKeys = activeKeys + 1
    input("Press ENTER to continue")
    KF.close()
    return

# Prints active keys
def keyList():
    global activeKeys
    KF = open("keyList.dat", "r")
    keys = KF.read()
    print(keys)
    input("Press ENTER to continue")
    KF.close()
    return

# Shows the history of key usage
def keyHist():
    print("History of Keys")
    time.sleep(1)
    return

# Select and remove an active key
def keyRemove():
    print("Remove key")
    time.sleep(1)
    return

def lockCont():
    global lock
    global lockStatus
    global serialport

    if lock:
        serialport.write(str.encode("2"))
        lock = False
        lockStatus = "UNLOCKED"
    else:
        serialport.write(str.encode("1"))
        lock = True
        lockStatus = "LOCKED"
        
def displayKeypad():
    global keypadInput
    count = 0
    
    while count < 5:
        print("Current Inputs: ", keypadInput)
        time.sleep(1)
        count += 1