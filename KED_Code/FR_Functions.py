import RPi.GPIO as GPIO         # GPIO for keypad
import random                   # Key generator
import time                     # Delay
import serial                   # UART
import cv2                      # Camera, haar classifier, cropping
import sys
import matplotlib.pyplot as plt
import numpy as np
import curses
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
activeKeys = 0             # Total number of active keys (Max = 10)
keypadInput = ""           # Variable to store the inputs from keypad
keypadMessage = "Keypad is ready"
keyFile_Lock = Lock()      # Mutex for accessing the key file
UART_Lock = Lock()         # Mutex for accessing the UART

#-----------------
# Curses Variables
#-----------------
stdscr = curses.initscr()  # Initiate the curses terminal
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

#------------------------
# Accelerometer Variables
#------------------------
accelX = ""
accelY = ""
accelZ = ""

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
#model = Facenet.loadModel()
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
    global SYSTEM_RUNNING
    global lockStatus
    global activeKeys
    global keypadInput
    global keyFile_Lock
    global stdscr
    global keypadInput
    global keypadMessage
    global accelX, accelY, accelZ

    # Curses settings
    stdscr.timeout(500)
    k = 0
    optNum = 1
    curses.curs_set(0)
    curses.noecho()
        
    while SYSTEM_RUNNING:
        # Screen setup
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        XCursor = width // 6
        YCursor = height // 6

        # Print title of the menu
        stdscr.attron(curses.color_pair(3))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(YCursor, XCursor, "Facial Recognition System Menu")
        stdscr.attroff(curses.color_pair(3))
        stdscr.attroff(curses.A_BOLD)

        # Print STATUS
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "STATUS", curses.A_UNDERLINE)
        # Shift a column to the right
        XCursor = XCursor + 2
        YCursor = YCursor + 1
        # Lock status
        stdscr.addstr(YCursor, XCursor, "Door Lock: ")
        XTemp = stdscr.getyx()[1]
        if lockStatus == "LOCKED":
            stdscr.addstr(YCursor, XTemp, lockStatus, curses.color_pair(2))
        else:
            # Blink red when door is unlocked
            stdscr.attron(curses.color_pair(1))
            stdscr.attron(curses.A_BLINK)
            stdscr.addstr(YCursor, XTemp, lockStatus)
            stdscr.attroff(curses.color_pair(1))
            stdscr.attroff(curses.A_BLINK)

        # Current number of active keys
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Active Keys: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, str(activeKeys))

        # Current accelerometer reading
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Accel-X: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, accelX)
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Accel-Y: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, accelY)
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Accel-Z: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, accelZ)
                      
        # Current keypad input
        XCursor = XCursor - 2
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "Keypad", curses.A_UNDERLINE)
        XCursor = XCursor + 2
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Keypad state: " + keypadMessage)
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Current Input: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, keypadInput)
        
        # Print active keys
        XCursor = XCursor - 2
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "List of Active Key(s)", curses.A_UNDERLINE)
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "No.\tKey\tCreation Date & Time\tExpiration Date & Time", curses.A_BOLD)
        KF = open("keyList.dat", "r")   # Read only
        EOF = KF.readline()
        while EOF:  # Parse line by line
            YCursor = YCursor + 1
            stdscr.addstr(YCursor, XCursor, EOF)
            EOF = KF.readline()
        KF.close()                      # Close the file

        # Print OPTIONS
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "Select an opton using UP/DOWN arrows and ENTER:")
        
        XCursor = XCursor + 5    
        YCursor = YCursor + 2

        if optNum == 1:
            stdscr.addstr(YCursor, XCursor, "1. LOCK/UNLOCK the door", curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "1. LOCK/UNLOCK the door")

        YCursor = YCursor + 1
        if optNum == 2:
            stdscr.addstr(YCursor, XCursor, "2. Generate key", curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "2. Generate key")
                
        YCursor = YCursor + 1
        if optNum == 3:
            stdscr.addstr(YCursor, XCursor, "3. Key removal", curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "3. Key removal")

        YCursor = YCursor + 1
        if optNum == 4:
            stdscr.addstr(YCursor, XCursor, "4. Key usage history", curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "4. Key usage history")

        YCursor = YCursor + 1
        if optNum == 5:
            stdscr.addstr(YCursor, XCursor, "5. ATmega settings", curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "5. ATmega settings")

        XCursor = XCursor - 5
        YCursor = YCursor + 3
        if optNum == 6:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(YCursor, XCursor, "TERMINATE PROGRAM")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(YCursor, XCursor, "TERMINATE PROGRAM", curses.color_pair(1))   
            
        stdscr.refresh()
        k = stdscr.getch()

        # Key up
        if k == 65:
            optNum = optNum - 1
            if optNum < 1:
                optNum = 1
        # Key down
        elif k == 66:
            optNum = optNum + 1
            if optNum > 6:
                optNum = 6
        # Enter
        elif k == 10:
            # Commands
            if optNum == 1:
                print("hello")
            elif optNum == 2:
                keyGen()
            elif optNum == 3:
                selectKeyRemoval()
            elif optNum == 4:
                keyHist()
            elif optNum == 6:
                SYSTEM_RUNNING = False
                
    curses.curs_set(1)
    curses.echo()
    curses.endwin()
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
    global keypadMessage
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
                keypadMessage = "Valid key code; Releasing the lock"
            else:
                keypadMessage = "Invalid key code; Try again after 5 seconds"
            KF.close()
            keyFile_Lock.release()
            keypadInput = ""  # Reset buffer
            time.sleep(5)     # Add 5 second delay to prevent spamming
            keypadMessage = "Keypad is ready"

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

# Generate a 5-digit key
# TO DO:
# a) Needs to check if the newly generated key already exist in the list.
# c) Create a custom master key with user permission to login.
def keyGen():
    global activeKeys
    global keyFile_Lock
    global stdscr

    k = 0
    optNum = 1
    
    key = ""
    # Key is generated in this loop
    for i in range(0, 5):
        key += str(random.randrange(0, 9, 1))

    numDays = 0
    inputTime = 0
    period = "AM"
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        XCursor = width // 6
        YCursor = height // 6

        # Print title
        stdscr.attron(curses.color_pair(3))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(YCursor, XCursor, "Key Generation Menu")
        stdscr.attroff(curses.color_pair(3))
        stdscr.attroff(curses.A_BOLD)

        XCursor = XCursor + 2
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "Generated key: ")
        XTemp = stdscr.getyx()[1]
        stdscr.addstr(YCursor, XTemp, key, curses.color_pair(2))

        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "Use LEFT/RIGHT keys to increase/decrease/select", curses.color_pair(1)) 
        
        YCursor = YCursor + 1
        if optNum == 1:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.addstr(YCursor, XCursor, "Regenerate KEY [Press ENTER]")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
        else:
            stdscr.addstr(YCursor, XCursor, "Regenerate KEY [Press ENTER]")

        YCursor = YCursor + 1
        if optNum == 2:
            stdscr.addstr(YCursor, XCursor, "Key life expectancy [0-30 days]:", curses.A_STANDOUT)
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + str(numDays), curses.color_pair(2))
        else:
            stdscr.addstr(YCursor, XCursor, "Key life expectancy [0-30 days]:")
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + str(numDays), curses.color_pair(2))

        YCursor = YCursor + 1
        if optNum == 3:
            stdscr.addstr(YCursor, XCursor, "Enter the expiration time of day [0-12 o' clock]:", curses.A_STANDOUT)
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + str(inputTime), curses.color_pair(2))
        else:
            stdscr.addstr(YCursor, XCursor, "Enter the expiration time of day [0-12 o' clock]:")
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + str(inputTime), curses.color_pair(2))                  

        YCursor = YCursor + 1
        if optNum == 4:
            stdscr.addstr(YCursor, XCursor, "Peiod of the expiration time:", curses.A_STANDOUT)
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + period, curses.color_pair(2))
        else:
            stdscr.addstr(YCursor, XCursor, "Peiod of the expiration time:")
            XTemp = stdscr.getyx()[1]
            stdscr.addstr(YCursor, XTemp, " " + period, curses.color_pair(2))

        XCursor = XCursor - 2
        YCursor = YCursor + 3
        if optNum == 5:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(YCursor, XCursor, "Cancel")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
            stdscr.attroff(curses.color_pair(1))
            XCursor = stdscr.getyx()[1] + 3
        else:
            stdscr.addstr(YCursor, XCursor, "Cancel", curses.color_pair(1))
            XCursor = stdscr.getyx()[1] + 3

        if optNum == 6:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(YCursor, XCursor, "Confirm")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
            stdscr.attroff(curses.color_pair(2))
        else:
            stdscr.addstr(YCursor, XCursor, "Confirm", curses.color_pair(2))

            
        stdscr.refresh()
        k = stdscr.getch()

        # Key up
        if k == 65:
            optNum = optNum - 1
            if optNum < 1:
                optNum = 1
         # Key down       
        elif k == 66:
            optNum = optNum + 1
            if optNum > 5:
                optNum = 5

        # Increase/decrease numDays using arrow keys
        if optNum == 2:
            if k == 67:
                if numDays < 30:
                    numDays = numDays + 1
            if k == 68:
                if numDays > 0:
                    numDays = numDays - 1

        # Increase/decrease inputTime using arrow keys
        elif optNum == 3:
            if k == 67:
                if inputTime < 12:
                    inputTime = inputTime + 1
            if k == 68:
                if inputTime > 0:
                    inputTime = inputTime - 1

        # Select period [AM/PM]  using arrow keys
        elif optNum == 4:
            if k == 67 or k == 68:
                if period == "AM":
                    period = "PM"
                else:
                    period = "AM"
                    
        # Selection between "Cancel" and "Confirm"
        elif optNum == 5:
            if k == 67:
                optNum = 6
        elif optNum == 6:
            if k == 68:
                optNum = 5                
                    
        # Enter
        if k == 10:
            if optNum == 1:
                key = ""
                # Key is generated in this loop
                for i in range(0, 5):
                    key += str(random.randrange(0, 9, 1))
            elif optNum == 5:
                return
            elif optNum == 6:
                if activeKeys < 10:
                    # Format the time string
                    time = ""
                    if inputTime < 10:
                        time = "0" + str(inputTime) + ":00"
                    else:
                        time = str(inputTime) + ":00"
                
                    # Stamp the creation and expiration time of the key in the key file
                    today = datetime.now()
                    expiration = today + timedelta(int(numDays))
                    keyFile_Lock.acquire()   # Acquire lock to the key file
                    KF = open("keyList.dat", "a")
                    KF.write(str(activeKeys + 1) + ".\t" +                          # Key No.
                         key + "\t" +                                               # Key
                         today.strftime("%m/%d/%y %I:%M %p") + "\t"                 # Creation date & time
                         + expiration.strftime("%m/%d/%y ")                         # Expiration date & time
                         + time + " " + period + "\n")

                    activeKeys = activeKeys + 1
                    KF.close()
                    keyFile_Lock.release()   # Releaes lock to the key file
                    return
                else:
                    XCursor = stdscr.getyx()[1] + 3
                    stdscr.attron(curses.A_STANDOUT)
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(YCursor, XCursor, "Maximum key limit reached!")
                    stdscr.attroff(curses.A_STANDOUT)
                    stdscr.attroff(curses.color_pair(1))
                    stdscr.refresh()
                    curses.napms(5000)
                    return  

# Shows the history of key usage
def keyHist():
    global stdscr

    k = 0
    optNum = 1
    while k != ord('q'):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        XCursor = width // 6
        YCursor = height // 6
        
        # Print title
        stdscr.attron(curses.color_pair(3))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(YCursor, XCursor, "Key Usage History")
        stdscr.attroff(curses.color_pair(3))
        stdscr.attroff(curses.A_BOLD)

        XCursor = XCursor + 2
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "Key\tDate\t\tTime", curses.A_BOLD)
        KF = open("keyHistory.dat", "r")   # Read only
        EOF = KF.readline()
        while EOF:  # Parse line by line
            YCursor = YCursor + 1
            stdscr.addstr(YCursor, XCursor, EOF)
            EOF = KF.readline()
        KF.close()                      # Close the file
        
        stdscr.refresh()
        k = stdscr.getch()

        
        
    #KH = open("keyHistory.dat", "r")
    #while(True):
    #    print("\033[2J\033[H")
    #    print("Key Usage History\n")
    #    print("Key\tDate\t\tTime")
    #    usage = KH.read()
    #    print(usage)
    #    command = input("Enter 'clear' to clear history\nor 'back' to return to the main menu\n>> ")
    #    if command == "clear":
    #        KHTemp = open("keyHistory.dat", "w")
    #        KHTemp.close()
    #        print("Key history has been cleared!")
    #        time.sleep(2)
    #    elif command == "back":
    #        KH.close()
    #        return
    #    else:
    #        print("Invalid option")
    #        time.sleep(2)
            #print("\033[2J\033[H")
            #print("Key Usage History\n")
            #print("Key\tDate\t\tTime")
            #print(usage)

# Select to remove an active key
def selectKeyRemoval():
    global keyFile_Lock
    global stdscr

    k = 0
    optNum = 1
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        XCursor = width // 6
        YCursor = height // 6

        # Print title
        stdscr.attron(curses.color_pair(3))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(YCursor, XCursor, "Key Removal")
        stdscr.attroff(curses.color_pair(3))
        stdscr.attroff(curses.A_BOLD)

        XCursor = XCursor + 2
        YCursor = YCursor + 2
        stdscr.addstr(YCursor, XCursor, "List of Active Key(s)", curses.A_UNDERLINE)
        YCursor = YCursor + 1
        stdscr.addstr(YCursor, XCursor, "No.\tKey\tCreation Date & Time\tExpiration Date & Time", curses.A_BOLD)
        KF = open("keyList.dat", "r")   # Read only
        EOF = KF.readline()
        lineNum = 0
        while EOF:  # Parse line by line
            lineNum = lineNum + 1
            YCursor = YCursor + 1
            if optNum == lineNum:
                stdscr.addstr(YCursor, XCursor, EOF, curses.A_STANDOUT)
            else:
                stdscr.addstr(YCursor, XCursor, EOF)
            EOF = KF.readline()
        KF.close()                      # Close the file

        YCursor = YCursor + 2
        YRemoveAll = YCursor
        if optNum == lineNum + 1:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(YCursor, XCursor, "REMOVE ALL ACTIVE KEYS")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.addstr(YCursor, XCursor, "REMOVE ALL ACTIVE KEYS", curses.color_pair(4))
        XRemoveAll = stdscr.getyx()[1] + 3
        
        XCursor = XCursor - 2
        YCursor = YCursor + 3
        if optNum == lineNum + 2:
            stdscr.attron(curses.A_BLINK)
            stdscr.attron(curses.A_STANDOUT)
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(YCursor, XCursor, "Cancel")
            stdscr.attroff(curses.A_BLINK)
            stdscr.attroff(curses.A_STANDOUT)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(YCursor, XCursor, "Cancel", curses.color_pair(1))
        
        stdscr.refresh()
        k = stdscr.getch()
        
        # Key up
        if k == 65:
            optNum = optNum - 1
            if optNum < 1:
                optNum = 1
         # Key down       
        elif k == 66:
            optNum = optNum + 1
            if optNum > lineNum + 2:
                optNum = lineNum + 2
        # Enter
        elif k == 10:
            # Cancel
            if optNum == lineNum + 2:
                return
            # Remove all keys options
            elif optNum == lineNum + 1:
                k = 0
                optRemove = 0
                while True:                    
                    if optRemove == 1:
                        stdscr.attron(curses.A_BOLD)
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(YRemoveAll, XRemoveAll, "YES")
                        stdscr.attroff(curses.A_BOLD)
                        stdscr.attroff(curses.color_pair(2))
                    else:
                        stdscr.addstr(YRemoveAll, XRemoveAll, "YES", curses.color_pair(2))
                        
                    if optRemove == 0:
                        stdscr.attron(curses.A_BOLD)
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(YRemoveAll, stdscr.getyx()[1] + 2, "NO")
                        stdscr.attroff(curses.A_BOLD)
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(YRemoveAll, stdscr.getyx()[1] + 2, "NO", curses.color_pair(1))
                        
                    stdscr.refresh()
                    k = stdscr.getch()

                    # Prompt user for confirmation on deleting all keys
                    if k == 68:
                        optRemove = 1
                    elif k == 67:
                        optRemove = 0
                    elif k == 10:
                        if optRemove == 0:
                            break;
                        else:
                            deleteAllKeys()
                            break;
                
            # Select key to remove
            elif optNum <= lineNum:
                removeKey(str(lineNum) + ".")
                if optNum == lineNum:
                    optNum = optNum - 1                

# Completely clear out all known keys
def deleteAllKeys():
    global activeKeys
    global keyFile_Lock
    keyFile_Lock.acquire()
    KF = open("keyList.dat", "w")
    KF.close()
    activeKeys = 0
    keyFile_Lock.release()
    return
    
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
    
    
