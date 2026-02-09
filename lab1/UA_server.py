import json
import socket


def multiply(A, B):
    rA, cA = len(A), len(A[0])
    rB, cB = len(B), len(B[0])

    if cA != rB:
        return None

    result = [[0 for _ in range(cB)] for _ in range(rA)]

    for i in range(rA):
        for j in range(cB):
            for k in range(cA):
                result[i][j] += A[i][k] * B[k][j]

    return result


server = socket.socket()
server.bind(("localhost", 5000))
server.listen(1)

print("Socket Matrix Server running...")

conn, addr = server.accept()
data = conn.recv(8192).decode()

payload = json.loads(data)
A = payload["A"]
B = payload["B"]

result = multiply(A, B)

if result is None:
    response = {"error": "Invalid matrix dimensions"}
else:
    response = {"result": result}

conn.send(json.dumps(response).encode())
conn.close()
