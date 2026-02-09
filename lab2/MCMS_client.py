import socket
import sys


class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")
        print("Type commands (add, sub, mul, div, analyze). Type 'quit' to exit.")

    def send(self, message: str):
        self.socket.sendall((message + "\n").encode())

    def receive(self) -> str:
        data = self.socket.recv(8192)
        if not data:
            raise ConnectionError("Server closed connection")
        return data.decode().rstrip()

    def close(self):
        self.socket.close()
        print("Connection closed.")

    def run(self):
        try:
            self.connect()
            while True:
                cmd = input("> ").strip()
                if not cmd:
                    continue

                self.send(cmd)
                response = self.receive()
                print(response)

                if cmd.lower() in ("quit", "exit"):
                    break

        except KeyboardInterrupt:
            print("\nClient interrupted.")
        except (ConnectionError, BrokenPipeError):
            print("Connection lost.")
        finally:
            self.close()


# ===== Entry point =====
def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = Client(host, port)
    client.run()


if __name__ == "__main__":
    main()
