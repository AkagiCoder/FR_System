#192.168.1.27
import socket
import pickle
import cv2
from PIL import Image

HOST = '192.168.1.28'  # Standard loopback interface address (localhost)
PORT = 5678        # Port to listen on (non-privileged ports are > 1023)

#print(HOST)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

imgBreak = Image.open(r"Face_Database/Adrian.jpg")
#imgBreak.show()
msg = pickle.dumps(imgBreak)

msg = bytes("KED DETECTED BREAK-IN AT ADDRESS 1234", "utf-8") + msg  
#print(msg)

clientsocket, address = s.accept()
print(f"Connection from {address} has been established!")
clientsocket.send(bytes(msg))
#clientsocket.send(bytes("KED DETECTED BREAK-IN AT ADDRESS 1234", "utf-8"))
clientsocket.close()
