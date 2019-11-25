import RPi.GPIO as GPIO         # GPIO for keypad
import random                   # Key generator
import time                     # Delay
from datetime import date       # Date and time

# SYSTEM_RUNNING is the status flag of the program
# True:  Program continuously runs
# False: Program ends
SYSTEM_RUNNING = True

# Global Variables
lockStatus = "LOCKED"
lock = False
activeKeys = 0

#----------------
# Layer #1
#----------------

# Display main menu options
def mainMenu():
    global SYSTE_RUNNING
    global lockStatus
    global activeKeys

    while SYSTEM_RUNNING:
        # Main menu with a list of commands
        print("\033[2J\033[H")
        print("Facial Recognition System Menu\n")
        print("STATUS")
        print("Door: ", lockStatus)
        print("Active Keys: ", activeKeys, "\n")
        print("Select an option:")
        print("\t1. Keys")
        print("\t2. Settings")
        print("\t3. Door Lock")
        print("\n\tEnter 'exit' to terminate the program")
        command = input(">> ")
        mainCommands(command)
    print("Main menu thread terminated")
    return

# Reads command from main menu
def mainCommands(command):
    global SYSTEM_RUNNING
    
    if(command == "1"):
        keyList()
    elif(command == "2"):
        settings()
    elif(command == "3"):
        doorLock()
    elif(command == "exit"):
        SYSTEM_RUNNING = False
        print ("SYSTEM SHUTTING DOWN...\n")
    else:
        input("Invalid option! Press any key to continue")
    return

def keyPad():
    global SYSTEM_RUNNING
    
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
    
    # Delay required to let enough time for the voltage
    # to drop for each output column.
    delay = 0.001

    while SYSTEM_RUNNING:
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
    
    # Clean up GPIO
    GPIO.cleanup()
    print("Keypad thread terminated")
    return

#----------------
# LAYER #2
#----------------

# Performs key generation and view information about keys
def keyList():
    global activeKeys
    while True:
        KF = open("keyList.dat", "a+")
        print("\033[2J\033[H")
        print("Keys\n")
        print("1. Generate a key")
        print("2. Show active keys")
        print("3. History of keys used")
        print("4. Remove a key")
        print("5. Back to the main menu")
        command = input("\n>> ")
        if(command == "1"):
            # Generate a 5-digit key
            key = random.randrange(10000,99999, 1) % 100000
            print("Key Generated: ", key)
            today = date.today()
            print("Date Generated: ", today)
            KF.write(str(key)+"\n")
            activeKeys = activeKeys + 1
            input("Press any enter to continue")
        elif(command == "2"):
            KF.seek(0, 0)
            keys = KF.read()
            print(keys)
            input("Press any enter to continue")
        elif(command == "3"):
            print("File")
        elif(command == "4"):
            KF.seek(0, 0)
            keys = KF.read()
            print(keys)
            removeKey = input("Which key to remove: ")
            KF.seek(int(removeKey), 0)
            KF.truncate()
        elif(command == "5"):
            break
        else:
            print("Invalid option!")
            time.sleep(2)
        KF.close()
    #x = random.randrange(10000,99999, 3) % 100000
    #print(x)
    return

def settings():
    print("\033[2J\033[H")
    print("settings function")
    input("Press any key to continue")
    return

def doorLock():
    global lock
    global lockStatus
    if(lock == True):
        lock = False
        lockStatus = "UNLOCKED"
        print("Unlocking Door")
    else:
        lock = True
        lockStatus = "LOCKED"
        print("Locking Door")
    time.sleep(2)
    return

