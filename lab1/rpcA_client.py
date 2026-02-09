import xmlrpc.client


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

proxy = xmlrpc.client.ServerProxy("http://localhost:6000/")
result = proxy.multiply(A, B)

if result is None:
    print("Error: Invalid matrix dimensions")
else:
    print("\nResultant Matrix:")
    for row in result:
        print(row)
