import time
# Append and read, pointer is placed at the EOF
keyFile = open("keyList.dat", "a+")
print("Opened Key File")

# Place file pointer at the beginning
keyFile.seek(0, 0)

count = 0

key = keyFile.readline()
while key:
    count = count + 1
    key = keyFile.readline()

print("Count: ", count)
#keyFile.write("Hello World\n")
time.sleep(1)
keyFile.close()
print("Closed Key File")