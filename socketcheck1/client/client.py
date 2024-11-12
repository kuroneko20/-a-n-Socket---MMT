import socket

HOST = "127.0.0.1"
# IP = "10.131.3.60"
SERVER_PORT = 58772
FORMAT = "utf8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("CLIENT SIDE: ")
client.connect((HOST, SERVER_PORT))
print("Client adress: ", client.getsockname())

username = input("Username: ")
psw = input("Password: ")

client.sendall(username.encode(FORMAT))

client.recv(1024)

client.sendall(psw.encode(FORMAT))

input()

