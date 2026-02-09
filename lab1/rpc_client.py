import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:6000/")

print("Choose: palindrome / armstrong / exit")

while True:
    op = input("\nEnter choice: ").strip().lower()

    if op == "exit":
        print("Exiting program.")
        break

    if op not in ("palindrome", "armstrong"):
        print("Invalid choice, try again.")
        continue

    num = input("Enter number: ").strip()

    if not num.isdigit():
        print("Only digits allowed.")
        continue

    num = int(num)

    result = proxy.check(op, num)

    if op == "palindrome":
        print("Palindrome result:", "YES" if result else "NO")
    else:
        print("Armstrong result:", "YES" if result else "NO")
