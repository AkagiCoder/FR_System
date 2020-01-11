import RPi.GPIO as GPIO         # GPIO for keypad
import random                   # Key generator
import time                     # Delay
import serial                   # UART
from datetime import datetime   # Date and time
from picamera import PiCamera   # Raspberry Pi Camera
# SYSTEM_RUNNING is the status flag of the program
# True:  Program continuously runs
# False: Program ends
SYSTEM_RUNNING = True

#----------------
# User defined objects
#----------------

#class key:
#    def __init__(self, num, code, dateCreate, timeCreate):
#        self.num = num                     # Key's number indicating the position of the list
#        self.code = code                   # Key's code
#        self.dateCreate = dateCreate       # Date when the key was generated
#        self.timeCreate = timeCreate       # Time when the key was generated
        
#----------------
# Global Variables
#----------------

lockStatus = "LOCKED"
lock = False
activeKeys = 0
keypadInput = ""

# Delay required to let enough time for the voltage
# to drop for each output column.
keyDelay = 0.001

#----------------
# Initialization of RPi's hardware
#----------------

# Serial communication
serialport = serial.Serial(
port = "/dev/serial0",
baudrate = 9600,
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE,
bytesize = serial.EIGHTBITS,
timeout = 1)

# GPIOs
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
        print("List of Active Key(s)")
        print("No.\tKey\tDate\t\tTime")
        KF = open("keyList.dat", "r")
        keys = KF.read()
        print(keys)
        print("Select an option:")
        print("\t1. Generate key")
        print("\t2. Key usage history")
        print("\t3. Remove a key")
        print("\t4. Lock/unlock door")
        print("\t5. DELETE ALL ACTIVE KEYS")
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
        keyHist()
    elif(command == "3"):
        keyRemove()
    elif(command == "4"):
        lockCont()
    elif(command == "5"):
        deleteAllKeys()
    elif(command == "6"):
        refresh()
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
    global lock
    global lockStatus
    global activeKeys

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
            print("Keypad Inputs: ", keypadInput)
            KF = open("keyList.dat", "r")
            keyList = KF.readlines()
            validCode = False
            for i in range(0, activeKeys):
                keyInfo = keyList[i].split()
                if keyInfo[1] == keypadInput:
                    #lock = False
                    #lockStatus = "Unlocked"
                    validCode = True
                    KH = open("keyHistory.dat", "a")
                    today = datetime.now()
                    KH.write(keypadInput + "\t" + today.strftime("%d/%m/%y\t%I:%M %p") + "\n")
                    KH.close()
                    lockCont()
            if validCode:
                print("Valid key code")
            else:
                print("Invalid key code")
            KF.close()
            keypadInput = ""  # Reset buffer
            print("Wait for 5 seconds to input again")
            time.sleep(5)     # Add 5 second delay to prevent spamming
            print("Keypad is ready")
    
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

def refresh():
    return

# Generate a 5-digit key
def keyGen():
    global activeKeys
    if activeKeys < 10:
        print("\033[2J\033[H")
        print("Generating key...")
        KF = open("keyList.dat", "a")
        key = ""
        # Key is generated in this loop
        for i in range(0, 5):
            key += str(random.randrange(0, 9, 1))
        print("Key Generated: ", key)
        # Stamp the generated date and time
        today = datetime.now()
        print("Date Generated: ", today, "\n")
        KF.write(str(activeKeys + 1) + ".\t" +
             key + "\t" +
             today.strftime("%m/%d/%y\t%I:%M %p") + "\n")
        activeKeys = activeKeys + 1
        KF.close()
        input("Press ENTER to continue")
    # Key limit reached
    else:
        print("Maximum limit of keys reached!")
        time.sleep(2)
    return

# Shows the history of key usage
def keyHist():


    KH = open("keyHistory.dat", "r")
    while(True):
        print("\033[2J\033[H")
        print("Key Usage History\n")
        print("Key\tDate\t\tTime")
        usage = KH.read()
        print(usage)
        command = input("Enter 'clear' to clear history\nor 'back' to return to the main menu\n>> ")
        if command == "clear":
            KHTemp = open("keyHistory.dat", "w")
            KHTemp.close()
            print("Key history has been cleared!")
            time.sleep(2)
        elif command == "back":
            KH.close()
            return
        else:
            print("Invalid option")
            time.sleep(2)
            #print("\033[2J\033[H")
            #print("Key Usage History\n")
            #print("Key\tDate\t\tTime")
            #print(usage)

# Select and remove an active key
def keyRemove():
    global activeKeys
    
    # Exit this option if the list is empty
    if activeKeys < 1:
        print("Key list is empty!")
        time.sleep(2)
        return
    
    # Display the active keys
    print("\033[2J\033[H")
    print("List of Active Key(s)")
    print("No.\tKey\tDate\t\tTime")
    KF = open("keyList.dat", "r")
    keys = KF.read()
    KF.seek(0, 0)
    keyList = KF.readlines()
    print(keys)
    
    keyNum = int(input("Which key is to be removed[No.]: "))
    if keyNum > activeKeys or keyNum < 1:
        print("Invalid [No.]!")
        time.sleep(2)
        return
    KF.close()
    
    KF = open("keyList.dat", "w")
    count = 0
    for i in range(0, activeKeys):
        keyInfo = keyList[i].split();
        if (str(keyNum)+".") != keyInfo[0]:
            count += 1
            KF.write(str(count) + ".\t" +
                     keyInfo[1] + "\t" +
                     keyInfo[2] + "\t" +
                     keyInfo[3] + " " + keyInfo[4] + "\n")
    activeKeys -= 1
    KF.close()
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
        
def deleteAllKeys():
    global activeKeys
    KF = open("keyList.dat", "w")
    KF.close()
    activeKeys = 0
    