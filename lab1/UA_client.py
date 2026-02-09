import json
import socket


def input_matrix(name):
    rows = int(input(f"Enter rows for Matrix {name}: "))
    cols = int(input(f"Enter columns for Matrix {name}: "))

    matrix = []
    print(f"Enter elements for Matrix {name}:")
    for i in range(rows):
        row = list(map(int, input(f"Row {i + 1}: ").split()))
        matrix.append(row)

    return matrix


A = input_matrix("A")
B = input_matrix("B")

client = socket.socket()
client.connect(("localhost", 5000))

client.send(json.dumps({"A": A, "B": B}).encode())

response = json.loads(client.recv(8192).decode())
client.close()

if "error" in response:
    print("Error:", response["error"])
else:
    print("\nResultant Matrix:")
    for row in response["result"]:
        print(row)
