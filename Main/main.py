import threading
import FR_Functions as FR

# Count the current active keys
try:
    KF = open("keyList.dat", "r")
    EOF = KF.readline()
    while EOF:
        FR.activeKeys += 1
        EOF = KF.readline()
    KF.close()

# If the keyList.dat file doesn't exist, create one
except FileNotFoundError:
    KF = open("keyList.dat", "w")
    KF.close()
    FR.activeKeys = 0

# Main Thread
# List of threads
t0 = threading.Thread(target = FR.mainMenu,)
#t1 = threading.Thread(target = FR.keypad, )
#t2 = threading.Thread(target = FR.camera, )
t3 = threading.Thread(target = FR.expKeyChecker, )
t4 = threading.Thread(target = FR.accelMonitor, )

# Initialize the thread
t0.start()   # Main menu
#t1.start()   # Keypad
#t2.start()   # Camera
t3.start()   # Expired key checker
t4.start()   # Accelerometer checker

# Wait for the threads to terminate
t0.join()
#t1.join()
#t2.join()
t3.join()
t4.join()
print("===== PROGRAM SUCCESSFULLY TERMINATED =====")
