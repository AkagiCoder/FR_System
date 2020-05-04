import socket

HOST = '192.168.1.21'  # The server's hostname or IP address
PORT = 5689        # The port used by the server

HEADERSIZE = 10

s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.close()

