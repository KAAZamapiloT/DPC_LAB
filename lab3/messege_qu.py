import socket
import sys
import threading
import time


class Node:
    def __init__(self, my_ip, my_port, peer_ip, peer_port):
        self.my_ip = my_ip
        self.my_port = my_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.peer_socket = None
        self.peer_lock = threading.Lock()


    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.my_ip, self.my_port))
        server_socket.listen(5)

        print(f"[SERVER] Listening on {self.my_ip}:{self.my_port}")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(
                target=self.handle_connection, args=(conn, addr), daemon=True
            ).start()

    def handle_connection(self, conn, addr):
        print(f"[SERVER] Connection from {addr}")

        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break

                    msg = data.decode().strip()

                   
                    if msg.startswith("PEER:"):
                        print(f"\n[FROM PEER] {msg[5:]}")
                    else:
                      
                        with self.peer_lock:
                            if self.peer_socket:
                                self.peer_socket.sendall(f"PEER:{msg}\n".encode())

                except:
                    break


    def start_client_to_own_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                client_socket.connect((self.my_ip, self.my_port))
                break
            except:
                time.sleep(0.5)

        while True:
            msg = input()
            if msg.lower() in ("exit", "quit"):
                break
            client_socket.sendall((msg + "\n").encode())

        client_socket.close()

   
    def connect_to_peer_server(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.peer_ip, self.peer_port))

                with self.peer_lock:
                    self.peer_socket = sock

                print(
                    f"[FORWARDER] Connected to peer server {self.peer_ip}:{self.peer_port}"
                )
                return

            except:
                time.sleep(0.5)


    def run(self):
        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.connect_to_peer_server, daemon=True).start()
        threading.Thread(target=self.start_client_to_own_server, daemon=True).start()

    
        while True:
            time.sleep(1)



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python node.py <my_ip> <my_port> <peer_ip> <peer_port>")
        sys.exit(1)

    my_ip = sys.argv[1]
    my_port = int(sys.argv[2])
    peer_ip = sys.argv[3]
    peer_port = int(sys.argv[4])

    Node(my_ip, my_port, peer_ip, peer_port).run()
