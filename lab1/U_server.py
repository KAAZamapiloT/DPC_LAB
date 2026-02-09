import datetime
import socket
import threading


# Function to handle each client
def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    # Ask client name
    client_socket.send("Enter your name: ".encode())
    name = client_socket.recv(1024).decode()

    welcome_msg = f"Welcome {name}! Available commands:\nTIME, ECHO <msg>, EXIT"
    client_socket.send(welcome_msg.encode())

    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(f"[{name}] says: {message}")

            if message.upper() == "TIME":
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                client_socket.send(f"Server Time: {current_time}".encode())

            elif message.upper().startswith("ECHO"):
                reply = message[5:]  # remove "ECHO "
                client_socket.send(f"Echo: {reply}".encode())

            elif message.upper() == "EXIT":
                client_socket.send("Goodbye!".encode())
                break

            else:
                client_socket.send("Invalid command".encode())

        except:
            break

    client_socket.close()
    print(f"[DISCONNECTED] {client_address} disconnected.")


# ---------------- MAIN SERVER ----------------
server_socket = socket.socket()
server_socket.bind(("localhost", 12345))
server_socket.listen(5)

print("Server running and waiting for clients...")

while True:
    client_socket, client_address = server_socket.accept()

    # Create a new thread for every client
    thread = threading.Thread(
        target=handle_client, args=(client_socket, client_address)
    )
    thread.start()
