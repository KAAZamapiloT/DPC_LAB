from xmlrpc.server import SimpleXMLRPCServer


def multiply(A, B):
    result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]
    return result


from xmlrpc.server import SimpleXMLRPCServer


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


server = SimpleXMLRPCServer(("localhost", 6000))
print("RPC Matrix Server running...")

server.register_function(multiply, "multiply")
server.serve_forever()
