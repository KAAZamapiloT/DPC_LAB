import os  # Import OS module to get process information
import socket  # Import socket module for network communication

HOST = "127.0.0.1"  # Server IP address (localhost)

PORT = 5000  # Server port number


def main():
    # Main function for the client program

    pid = os.getpid()  # Get process ID of this client (helps identify multiple clients)

    # Create a TCP socket using IPv4

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # Connect to the server at given IP and port

        # Print client connection information

        print(f"Client PID={pid} connected. Type messages:")

        while True:  # Run client continuously
            msg = input("> ")  # Read message from user input

            # Send message to server (add newline for proper formatting)

            s.sendall((msg + "\n").encode("utf-8"))

            # Receive response from server (up to 4096 bytes)

            print(
                s.recv(4096).decode("utf-8", errors="ignore"),
                end="",  # Avoid adding extra newline
            )

    # Entry point of the program


if __name__ == "__main__":
    main()  # Start the client
