import threading
import FR_Functions as FR

# Count the current active keys
KF = open("keyList.dat", "r")
EOF = KF.readline()
while EOF:
    FR.activeKeys += 1
    EOF = KF.readline()
KF.close()

# Main Thread
# List of threads
t0 = threading.Thread(target = FR.mainMenu,)
#t1 = threading.Thread(target = FR.keypad, )
#t2 = threading.Thread(target = FR.camera, )

# Initialize the thread
t0.start()   # Main menu
#t1.start()   # Keypad
#t2.start()   # Camera

# Wait for the threads to terminate
t0.join()
#t1.join()
#t2.join()
print("\nPROGRAM SUCCESSFULLY TERMINATED")
