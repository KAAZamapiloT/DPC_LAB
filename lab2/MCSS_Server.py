import socket  # Import socket module for network communication
import threading  # Import threading module to handle multiple clients concurrently
from datetime import datetime  # Import datetime to add timestamps in responses

HOST = "127.0.0.1"  # Server IP address (localhost – same machine)

PORT = 5000  # Port number on which the server will listen


def handle_client(conn, addr):
    # This function handles communication with a single client

    print(f"[+] Connected: {addr}")  # Print when a client connects

    with conn:  # Ensure connection is properly closed after use
        while True:  # Keep communicating until client disconnects
            data = conn.recv(1024)  # Receive up to 1024 bytes from client

            if not data:  # If no data is received
                break  # Client has disconnected, exit loop
                # Decode received bytes into string

            msg = data.decode("utf-8", errors="ignore").strip()

            # Prepare reply message with timestamp and client info

            reply = (
                f"[{datetime.now().isoformat(timespec='seconds')}] "
                f"Server got '{msg}' from {addr}\n"
            )
            print(f"Received : {msg} from :{addr}")
            conn.sendall(reply.encode("utf-8"))  # Send response back to client

    print(f"[-] Disconnected: {addr}")  # Print when client disconnects


def main():
    # Main function to start the server

    # Create a TCP socket using IPv4

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow reuse of address and port after server restart

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((HOST, PORT))  # Bind socket to IP address and port

    s.listen()  # Start listening for incoming connections

    print(f"Server listening on {HOST}:{PORT}")  # Server startup message

    while True:  # Run server indefinitely
        conn, addr = s.accept()  # Accept a new client

        # Create a new thread for each client

        threading.Thread(
            target=handle_client,  # Function to handleclient
            args=(conn, addr),  # Arguments passed to handler
            daemon=True,  # Thread exits when main program exits
        ).start()

        # Entry point of the program


if __name__ == "__main__":
    main()  # Start the server
