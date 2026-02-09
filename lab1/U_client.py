import socket

client_socket = socket.socket()
client_socket.connect(("localhost", 12345))

# Receive name request
msg = client_socket.recv(1024).decode()
print(msg)

name = input()
client_socket.send(name.encode())

# Welcome message
welcome = client_socket.recv(1024).decode()
print(welcome)

while True:
    message = input("Enter command: ")
    client_socket.send(message.encode())

    reply = client_socket.recv(1024).decode()
    print("Server:", reply)

    if message.upper() == "EXIT":
        break

client_socket.close()
