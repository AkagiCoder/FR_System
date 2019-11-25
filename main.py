import threading
import FR_Tasks as FR

          
# Main Thread
# List of threads
t0 = threading.Thread(target = FR.mainMenu(),)
t1 = threading.Thread(target = FR.keyPad(), )

# Initialize the thread
t0.start()   # Main menu
t1.start()   # Keypad

# Wait for the threads
t0.join()
t1.join()

print("\nPROGRAM ENDED")
