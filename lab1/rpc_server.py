from xmlrpc.server import SimpleXMLRPCServer


def is_palindrome(n):
    s = str(n)
    return s == s[::-1]


def is_armstrong(n):
    s = str(n)
    power = len(s)
    total = sum(int(d) ** power for d in s)
    return total == n


def check(operation, number):
    if operation == "palindrome":
        return is_palindrome(number)
    elif operation == "armstrong":
        return is_armstrong(number)
    else:
        return None


server = SimpleXMLRPCServer(("0.0.0.0", 6000))
print("RPC Server running...")

server.register_function(check, "check")
server.serve_forever()
