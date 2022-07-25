import socket

address = ('server.veloren.net', 14005)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(address)

print("[Debug] Connected to server")

while True:
    data = s.recv(1024)
    if not data:
        break
    print(data.decode('utf-8'))
    print(data)