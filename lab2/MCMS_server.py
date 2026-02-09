import socket
import sys
import threading
import traceback
from collections import defaultdict, deque
from datetime import datetime


# ---------------------------
# Task logger
# ---------------------------
class TaskLogger:
    def __init__(self, max_entries=1000):
        self._lock = threading.Lock()
        self._logs = deque(maxlen=max_entries)

    def log(self, port, peer, command, result):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "port": port,
            "peer": peer,
            "command": command,
            "result": result,
        }
        with self._lock:
            self._logs.append(entry)

    def snapshot(self, n=None):
        with self._lock:
            items = list(self._logs)
        if n is None:
            return items
        if n <= 0:
            return []
        return items[-n:]

    def clear(self):
        with self._lock:
            self._logs.clear()


# ---------------------------
# Shutdown signal
# ---------------------------
class ShutdownSignal:
    def __init__(self):
        self.event = threading.Event()

    def stop(self):
        self.event.set()

    def is_set(self):
        return self.event.is_set()

    def wait(self, t):
        self.event.wait(t)


# ---------------------------
# Client registry
# ---------------------------
class ClientRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._clients = defaultdict(set)  # {port: {peer, ...}}

    def add(self, port, peer):
        with self._lock:
            self._clients[port].add(peer)

    def remove(self, port, peer):
        with self._lock:
            self._clients[port].discard(peer)
            if not self._clients[port]:
                del self._clients[port]

    def snapshot(self):
        with self._lock:
            return {p: set(peers) for p, peers in self._clients.items()}


# ---------------------------
# Request handler
# ---------------------------
class RequestHandler:
    @staticmethod
    def handle(request: str) -> str:
        request = request.strip()
        if not request:
            return "ERROR: empty request"

        parts = request.split()
        cmd = parts[0].lower()

        if cmd in ("add", "sub", "mul", "div"):
            if len(parts) != 3:
                return "ERROR: arithmetic requires 2 operands"

            try:
                a = float(parts[1])
                b = float(parts[2])
            except ValueError:
                return "ERROR: operands must be numbers"

            if cmd == "add":
                res = a + b
            elif cmd == "sub":
                res = a - b
            elif cmd == "mul":
                res = a * b
            elif cmd == "div":
                if b == 0:
                    return "ERROR: division by zero"
                res = a / b

            return f"RESULT: {int(res) if getattr(res, 'is_integer', lambda: False)() else res}"

        elif cmd == "analyze":
            if len(parts) < 2:
                return "ERROR: analyze requires a string"

            s = " ".join(parts[1:])
            return (
                "ANALYSIS:\n"
                f"UPPERCASE: {s.upper()}\n"
                f"WORDS: {len(s.split())}\n"
                f"CHARS(including spaces): {len(s)}\n"
                f"CHARS(excluding spaces): {len(s.replace(' ', ''))}"
            )

        return "ERROR: unknown command"


# ---------------------------
# Server (per-port)
# ---------------------------
class Server:
    def __init__(
        self,
        host,
        port,
        registry: ClientRegistry,
        shutdown: ShutdownSignal,
        logger: TaskLogger,
    ):
        self.host = host
        self.port = port
        self.registry = registry
        self.shutdown = shutdown
        self.logger = logger

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
        except OSError as e:
            print(f"[Port {self.port}] bind error: {e}")
            return

        sock.listen(32)
        sock.settimeout(1.0)

        print(f"[Port {self.port}] Server listening on {self.host}:{self.port}")

        try:
            while not self.shutdown.is_set():
                try:
                    conn, addr = sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                threading.Thread(
                    target=self._client_thread,
                    args=(conn, addr),
                    daemon=True,
                ).start()
        finally:
            try:
                sock.close()
            except Exception:
                pass
            print(f"[Port {self.port}] Server stopped.")

    def _client_thread(self, conn: socket.socket, addr):
        peer = f"{addr[0]}:{addr[1]}"
        print(f"[Port {self.port}] Connected: {peer}")
        self.registry.add(self.port, peer)

        try:
            with conn:
                conn.settimeout(300)  # idle timeout
                while not self.shutdown.is_set():
                    try:
                        data = conn.recv(4096)
                    except socket.timeout:
                        # Idle timeout — close connection
                        break
                    except ConnectionResetError:
                        break

                    if not data:
                        # client closed connection
                        break

                    text = data.decode(errors="ignore")
                    responses = []

                    for line in text.splitlines():
                        if not line:
                            continue

                        if line.strip().lower() in ("exit", "quit"):
                            # log the quit command as a task as well
                            result = "BYE"
                            responses.append(result)
                            try:
                                conn.sendall(("\n".join(responses) + "\n").encode())
                            except Exception:
                                pass
                            self.logger.log(self.port, peer, line.strip(), result)
                            return

                        # handle request
                        result = RequestHandler.handle(line)
                        responses.append(result)

                        # Log the task (store only first line of result for brevity)
                        first_result_line = (
                            result.splitlines()[0]
                            if isinstance(result, str)
                            else str(result)
                        )
                        self.logger.log(
                            self.port, peer, line.strip(), first_result_line
                        )

                    # send all responses for this recv
                    try:
                        conn.sendall(("\n".join(responses) + "\n").encode())
                    except BrokenPipeError:
                        break

        except Exception:
            traceback.print_exc()

        finally:
            self.registry.remove(self.port, peer)
            print(f"[Port {self.port}] Disconnected: {peer}")


# ---------------------------
# Admin console
# ---------------------------
class AdminConsole:
    def __init__(
        self, registry: ClientRegistry, logger: TaskLogger, shutdown: ShutdownSignal
    ):
        self.registry = registry
        self.logger = logger
        self.shutdown = shutdown

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while not self.shutdown.is_set():
            try:
                raw = input()
            except EOFError:
                break
            except KeyboardInterrupt:
                # allow Ctrl+C in admin console to propagate to main shutdown
                self.shutdown.stop()
                break

            if raw is None:
                continue

            cmd = raw.strip().lower()
            if not cmd:
                continue

            if cmd in ("exit", "quit"):
                print("Admin requested shutdown.")
                self.shutdown.stop()
                break

            if cmd == "clients":
                snapshot = self.registry.snapshot()
                if not snapshot:
                    print("No connected clients.")
                else:
                    print("Connected clients:")
                    for port, peers in sorted(snapshot.items()):
                        print(f"  Port {port}:")
                        for p in sorted(peers):
                            print(f"    - {p}")
                continue

            if cmd.startswith("logs"):
                parts = cmd.split()
                n = None
                if len(parts) == 2:
                    try:
                        n = int(parts[1])
                    except ValueError:
                        print("Usage: logs [n]   (n must be an integer)")
                        continue

                entries = self.logger.snapshot(n)
                if not entries:
                    print("No task logs.")
                else:
                    print(
                        f"Showing last {len(entries) if n is None else min(len(self.logger.snapshot()), n)} log entries:"
                    )
                    for e in entries:
                        print(
                            f"[{e['time']}] Port {e['port']} | {e['peer']} | {e['command']} -> {e['result']}"
                        )
                continue

            if cmd == "clearlogs":
                self.logger.clear()
                print("Logs cleared.")
                continue

            print(f"Unknown admin command: {cmd}")


# ---------------------------
# Server manager (composition root)
# ---------------------------
class ServerManager:
    def __init__(self, ports):
        self.shutdown = ShutdownSignal()
        self.registry = ClientRegistry()
        self.logger = TaskLogger()

        # Create one server instance per port
        self.servers = [
            Server("0.0.0.0", p, self.registry, self.shutdown, self.logger)
            for p in ports
        ]

        # Admin console composed into manager
        self.admin = AdminConsole(self.registry, self.logger, self.shutdown)

    def start(self):
        # Start all servers
        for server in self.servers:
            server.start()

        # Start admin console
        self.admin.start()

        print("Servers running on ports:", [s.port for s in self.servers])
        print("Admin commands: clients | logs [n] | clearlogs | exit")

        try:
            while not self.shutdown.is_set():
                self.shutdown.wait(1)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received.")
            self.shutdown.stop()

        print("Shutdown complete.")


def main():
    DEFAULT_PORTS = [5000, 5001]  # if no command line args this will be chosen

    if len(sys.argv) > 1:
        try:
            ports = [int(p) for p in sys.argv[1:]]
        except ValueError:
            print("Usage: python server.py [port1 port2 ...]")
            sys.exit(1)
    else:
        ports = DEFAULT_PORTS

    ServerManager(ports).start()


if __name__ == "__main__":
    main()
