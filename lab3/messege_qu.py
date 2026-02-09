import socket
import sys
import threading


class Node:
    def __init__(self, my_ip, my_port, peer_ip, peer_port):
        self.my_ip = my_ip
        self.my_port = my_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port

    # ---------------- SERVER ----------------
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.my_ip, self.my_port))
        server_socket.listen(1)

        print(f"[SERVER] Listening on {self.my_ip}:{self.my_port}")

        conn, addr = server_socket.accept()
        print(f"[SERVER] Connected by {addr}")

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"\n[FROM PEER] {data.decode().strip()}")
            except:
                break

        conn.close()
        server_socket.close()

    # ---------------- CLIENT ----------------
    def start_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                client_socket.connect((self.peer_ip, self.peer_port))
                break
            except:
                continue

        print(f"[CLIENT] Connected to peer {self.peer_ip}:{self.peer_port}")

        while True:
            msg = input()
            if msg.lower() in ("exit", "quit"):
                break
            client_socket.sendall((msg + "\n").encode())

        client_socket.close()

    # ---------------- RUN ----------------
    def run(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        client_thread = threading.Thread(target=self.start_client, daemon=True)

        server_thread.start()
        client_thread.start()

        server_thread.join()
        client_thread.join()


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python node.py <my_ip> <my_port> <peer_ip> <peer_port>")
        sys.exit(1)

    my_ip = sys.argv[1]
    my_port = int(sys.argv[2])
    peer_ip = sys.argv[3]
    peer_port = int(sys.argv[4])

    node = Node(my_ip, my_port, peer_ip, peer_port)
    node.run()
