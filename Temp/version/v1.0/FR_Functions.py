import RPi.GPIO as GPIO         # GPIO for keypad
import random                   # Key generator
import time                     # Delay
import serial                   # UART
import cv2                      # Camera, haar classifier, cropping
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime   # Date and time
from datetime import timedelta  # Perform arithmetic on dates/times
from threading import Lock
from DeepFace.commons import functions, distance as dst
from DeepFace.basemodels import OpenFace, Facenet
from tensorflow.keras.preprocessing import image


# SYSTEM_RUNNING is the status flag of the program
# True:  Program continuously runs
# False: Program ends
SYSTEM_RUNNING = True

#----------------
# Global Variables
#----------------
lockStatus = "LOCKED"
lock = True
activeKeys = 0        # Total number of active keys (Max = 10)
keypadInput = ""      # Variable to store the inputs from keypad
keyFile_Lock = Lock() # Mutex for accessing the key file
UART_Lock = Lock()    # Mutex for accessing the UART

# Delay required to give enough time for the voltage
# to drop for each output column.
keyDelay = 0.001

#----------------
# FCheck and Camera Variables
#----------------
faceFlag = False            # Flag to print the person's name when verified
faces = []                  # Face data
frame = None                # Frame data from camera
personName = "Bryan"       # Valid person
personImg = "Bryan.png"    # Person to check in the database
distance_metric = "cosine"  # Distance type
distSensitivity = 0.2       # Adjust the distance sensitivity

# OpenFace
#print("Using OpenFace model backend", distance_metric,"distance.")
#model_name = "OpenFace"
#model = OpenFace.loadModel()
#input_shape = (96, 96)

# Facenet
print("Using Facenet model backend", distance_metric,"distance.")
model_name = "Facenet"
model = Facenet.loadModel()
input_shape = (160, 160)

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

# Serial communication commands
# Message format:
# STX + Command + ETX
STX = b'\x02'           # Start of text
ETX = b'\x03'           # End of text
CW = "RCW"              # Rotate motor clockwise
CCW = "RCCW"            # Rotate motor counter-clockwise
ACCX = "ACCEL_X"        # Acceleration on X-axis
ACCY = "ACCEL_Y"        # Acceleration on Y-axis
ACCZ = "ACCEL_Z"        # Acceleration on Z-axis

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
        print("No.\tKey\tCreation Date & Time\tExpiration Date & Time")
        KF = open("keyList.dat", "r")
        keys = KF.read()
        print(keys)
        print("Select an option:")
        print("\t1. Generate key")
        print("\t2. Key usage history")
        print("\t3. Remove a key")
        print("\t4. Lock/unlock door")
        print("\t5. DELETE ALL ACTIVE KEYS")
        print("\t6. ATmega Settings")
        print("\n\tEnter 'exit' to terminate the program")
        command = input(">> ")
        mainCommands(command)
    print("Main menu thread has terminated")
    return

# Reads command from main menu
def mainCommands(command):
    global SYSTEM_RUNNING
    
    if(command == "1"):
        keyGen()
    elif(command == "2"):
        keyHist()
    elif(command == "3"):
        selectKeyRemoval()
    elif(command == "4"):
        lockCont()
    elif(command == "5"):
        deleteAllKeys()
    elif(command == "6"):
        ATmegaSettings()
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
            keyFile_Lock.acquire()
            KF = open("keyList.dat", "r")
            keyList = KF.readlines()
            validCode = False
            for i in range(0, activeKeys):
                keyInfo = keyList[i].split()
                if keyInfo[1] == keypadInput:
                    lock = False
                    lockStatus = "Unlocked"
                    validCode = True
                    KH = open("keyHistory.dat", "a")
                    today = datetime.now()
                    KH.write(keypadInput + "\t" + today.strftime("%d/%m/%y\t%I:%M %p") + "\n")
                    KH.close()
            if validCode:
                print("Valid key code")
            else:
                print("Invalid key code")
            KF.close()
            keyFile_Lock.release()
            keypadInput = ""  # Reset buffer
            print("Wait for 5 seconds to input again")
            time.sleep(5)     # Add 5 second delay to prevent spamming
            print("Keypad is ready")

    # Clean up GPIO
    GPIO.cleanup()
    print("Keypad thread terminated")
    return

# Thread that automatically deletes expired keys
def expKeyChecker():
    global SYSTEM_RUNNING
    global keyFile_Lock
    global activeKeys

    while SYSTEM_RUNNING:
        time.sleep(0)

        # Keeps track of a list of expired keys to be removed
        expKeyList = []
        # Today's date is the reference point
        today = datetime.now()

        keyFile_Lock.acquire()           # Acquire lock to key file
        KF = open("keyList.dat", "r")    # Open the key list file
        keyList = KF.readlines()
        expKeyCount = 0                  # Number of expired keys detected
        # Check through the key file for expired dates and time
        for i in range(0, activeKeys):
            keyInfo = keyList[i].split()
            expDate = datetime(int(keyInfo[5][6:]) + 2000, int(keyInfo[5][:-6]), int(keyInfo[5][3:-3]))
            # Compute the period offset
            if keyInfo[7] == "PM":
                expTime = int(keyInfo[6][:-3]) + 12
            else:
                expTime = int(keyInfo[6][:-3])

            if expDate <= today and expTime <= today.hour:
                expKeyList.append(keyInfo[0])  # Store expired key's number
                expKeyCount += 1               # Increment the count
        KF.close()
        keyFile_Lock.release()           # Release lock to the key file
        for i in range(0, expKeyCount):
            removeKey(expKeyList[i])
    print("Expired key checker thread has terminated")

# Thread that monitors the MPU6050 (Accelerometer)
def accelMonitor():
    global SYSTEM_RUNNING
    global UART_Lock

    while SYSTEM_RUNNING:
        #UART_Lock.acquire()    # Acquire lock to the UART
        time.sleep(1)
        #UART_Lock.release()    # Release lock to the UART

    print("Accelerometer monitor thread has terminated")

# Captures frames from the camera using CV2
def camera():
    global SYSTEM_RUNNING
    global faces
    global frame
    global faceFlag
    global personName
    
    # Load the face haar classifier
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Initiate the webcam
    video_capture = cv2.VideoCapture(0)

    while SYSTEM_RUNNING:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.1,
            minNeighbors = 10,
            minSize = (200,000),
            flags = cv2.FONT_HERSHEY_SIMPLEX
            )
        
        # Draw a rectangle around the faces
        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if faceFlag:
                cv2.putText(frame, personName, (x, y), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 3)
        
        # Display the captured frame
        cv2.imshow('Video', frame)
        cv2.waitKey(1)
        
    video_capture.release()
    cv2.destroyAllWindows()

    print("Camera thread has terminated")

# Checks and verifies the face
def FCheck():
    global SYSTEM_RUNNING
    global faceFlag
    global faces
    global frame
    global personImg
    global distSensitivity
    global model_name
    global distance_metric
    global model
    global input_shape
    global lock
    global lockStatus
    
    threshold = functions.findThreshold(model_name, distance_metric)

    # Image PATH GOES HERE
    img1 = functions.detectFace("Face_Database/" + personImg, input_shape)
    img1_representation = model.predict(img1)[0,:]

    while SYSTEM_RUNNING:
        time.sleep(0)
        if len(faces) > 0:
            # Take the first face only
            x, y, w, h = faces[0]
            # Crop the detected face
            detected_face = frame[int(y):int(y+h), int(x):int(x+w)]
            detected_face = cv2.resize(detected_face, input_shape)
            img_pixels = image.img_to_array(detected_face)
            img_pixels = np.expand_dims(img_pixels, axis = 0)
            #normalize input in [0, 1]
            img_pixels /= 255 
            # Predict if the given face is valid
            img2_representation = model.predict(img_pixels)[0,:]
            distance = dst.findCosineDistance(img1_representation, img2_representation)
            print(distance)
            
            # Checks the distance (farther means the person is not valid)
            if distance < distSensitivity:
                faceFlag = True
                lock = False
                lockStatus = "UNLOCKED"
            else:
                faceFlag = False

    print("FCheck thread has terminated")

# Thread that controls the door lock
def doorLock():
    global SYSTEM_RUNNING
    global lock
    global lockStatus
    global CW
    global CCW
    
    while SYSTEM_RUNNING:
        time.sleep(0)
        if not lock:
            # Unlock the door
            UART_Send(CCW)
            print("Lock is unlocked for 5 s")
            time.sleep(5)
            
            # Relock the door
            UART_Send(CW)
            lock = True
            lockStatus = "LOCKED"
    
    print("Door lock thread has terminated")
#----------------
# LAYER #2
#----------------

# Removes a key once user specifies the number '1.', '2.', etc.
def removeKey(keyNum):
    global activeKeys
    global keyFile_Lock

    keyFile_Lock.acquire()
    KF = open("keyList.dat", "r")
    keyList = KF.readlines()
    KF.close()
    KF = open("keyList.dat", "w")
    count = 0
    for i in range(0, activeKeys):
        keyInfo = keyList[i].split();
        if (str(keyNum)) != keyInfo[0]:
            count += 1
            KF.write(str(count) + ".\t" +                                        # Key No.
                     keyInfo[1] + "\t" +                                         # Key
                     keyInfo[2] + " " + keyInfo[3] + " " + keyInfo[4] + "\t" +   # Creation Date & Time
                     keyInfo[5] + " " + keyInfo[6] + " " + keyInfo[7] + "\n")    # Expiration Date & Time
    activeKeys -= 1
    KF.close()
    keyFile_Lock.release()
    return

def refresh():
    return

# Generate a 5-digit key
# TO DO:
# a) Needs to check if the newly generated key already exist in the list.
# c) Create a custom master key with user permission to login.
def keyGen():
    global activeKeys
    global keyFile_Lock

    if activeKeys < 10:
        print("\033[2J\033[H")
        print("Generating key...")
        key = ""
        # Key is generated in this loop
        for i in range(0, 5):
            key += str(random.randrange(0, 9, 1))

        # Prompt the user for the expiration date
        print("What is the life expectancy of this key?")
        while True:
            numDays = input("Enter number of days between 0-30: ")
            try:
                days = int(numDays)
                if days > 30 or days < 0:
                    print("Life expectancy must be between 0-30 days!\nTry again")
                else:
                    break
            except ValueError:
                print("Invalid input for the number of days!\nTry again")

        # Prompt the user for the expiration time on that day
        while True:
            inputTime = input("Enter the time of day [1-12] (Rounded to the nearest hour): ")
            try:
                time = int(inputTime)
                if time < 1 or time > 12:
                    print("Time of the day must be between 1-12 o' clock!\nTry again")
                else:
                    # Format the time string
                    if time < 10:
                        inputTime = "0" + inputTime + ":00"
                    else:
                        inputTime = inputTime + ":00"
                    break
            except ValueError:
                print("Invalid input for the time of the day!\nTry again")

        # Prompt the user for the period of that expiration time
        while True:
            period = input("Enter the period [AM/PM] of that expiration time: ")
            if period != "AM" and period != "PM":
                print("Invalid input for the period of the day!\nTry again")
            else:
                break

        print("Key Generated: ", key)

        # Stamp the creation and expiration time of the key in the key file
        today = datetime.now()
        expiration = today + timedelta(days)

        keyFile_Lock.acquire()   # Acquire lock to the key file
        KF = open("keyList.dat", "a")
        KF.write(str(activeKeys + 1) + ".\t" +                          # Key No.
             key + "\t" +                                               # Key
             today.strftime("%m/%d/%y %I:%M %p") + "\t"                 # Creation date & time
             + expiration.strftime("%m/%d/%y ")                         # Expiration date & time
             + inputTime + " " + period + "\n")

        activeKeys = activeKeys + 1
        KF.close()
        keyFile_Lock.release()   # Releaes lock to the key file
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

# Select to remove an active key
def selectKeyRemoval():
    global keyFile_Lock
    # Exit this option if the list is empty
    if activeKeys < 1:
        print("Key list is empty!")
        time.sleep(2)
        return

    # Display the active keys
    print("\033[2J\033[H")
    print("List of Active Key(s)")
    print("No.\tKey\tCreation Date & Time\tExpiration Date & Time")
    keyFile_Lock.acquire()
    KF = open("keyList.dat", "r")
    keys = KF.read()
    KF.seek(0, 0)
    keyList = KF.readlines()
    print(keys)

    keyNum = input("Which key is to be removed[No.] or type 'exit' to exit: ")
    if keyNum == "exit":
        return
    if int(keyNum) > activeKeys or int(keyNum) < 1:
        print("Invalid [No.]!")
        time.sleep(2)
        return
    KF.close()
    keyFile_Lock.release()

    # Call the function to remove that key
    removeKey(keyNum + ".")
    return

# This piece of code is to soon be removed and replaced
#def lockCont():
#    global lock
#    global lockStatus
#    global serialport

#    if lock:
#        serialport.write(str.encode("2"))
#        lock = False
#        lockStatus = "UNLOCKED"
#    else:
#        serialport.write(str.encode("1"))
#        lock = True
#        lockStatus = "LOCKED"

# Completely clear out all known keys
def deleteAllKeys():
    global activeKeys

    # Get confirmation from the user
    while True:
        action = input("Are you sure if you want to clear out the keys (y/n): ")
        if (action == "y"):
            KF = open("keyList.dat", "w")
            KF.close()
            activeKeys = 0
            print("Entire key list will be cleared")
            time.sleep(3)
            return
        elif (action == "n"):
            print("Action has been cancelled")
            time.sleep(3)
            return
        else:
            print("Invalid input, please enter 'y' for yes or 'n' for no...")
            time.sleep(3)

# Sends the commmand using UART
def UART_Send(command):
    global UART_Lock
    global serialport

    # Signals to initiate/terminate the UART message
    global STX
    global ETX

    UART_Lock.acquire()
    serialport.write(STX)
    serialport.write(str.encode(command))
    serialport.write(ETX)
    UART_Lock.release()

# Controls the ATmega board using UART.
# The commands are listed near the top of this code
def ATmegaSettings():
    global serialport
    global UART_Lock

    # Variables that represent the command to be sent
    global CW
    global CCW
    global ACCX
    global ACCY
    global ACCZ

    # Status variables of the lock
    global lock
    global lockStatus

    while True:
        print("\033[2J\033[H")
        print("ATmega328 Settings\n")
        print("\t1. Rotate motor CW")
        print("\t2. Rotate motor CCW")
        print("\t3. Retrieve acceleration on X-axis")
        print("\t4. Retrieve acceleration on Y-axis")
        print("\t5. Retrieve acceleration on Z-axis")
        print("\nType 'exit' to exit")
        command = input("\nSelect an option: ")

        # Rotate motor CW
        if (command == "1"):
            UART_Send(CW)
        # Rotate motor CCW
        elif (command == "2"):
            UART_Send(CCW)
        # Request acceleration of X-axis
        elif (command == "3"):
            UART_Send(ACCX)
            message = serialport.readline()
            print(message.decode("utf-8"))
            time.sleep(1)
        elif (command == "4"):
            UART_Send(ACCY)
            message = serialport.readline()
            print(message.decode("utf-8"))
            time.sleep(1)
        elif (command == "5"):
            UART_Send(ACCZ)
            message = serialport.readline()
            print(message.decode("utf-8"))
            time.sleep(1)
        elif(command == "exit"):
            return
    
    