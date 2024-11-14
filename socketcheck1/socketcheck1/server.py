
import socket

HOST = "127.0.0.1"
# IP = "10.131.3.60"
SERVER_PORT = 58772
FORMAT = "utf8"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Kết nối theo giao thức IP/TCP

s.bind((HOST,SERVER_PORT))
s.listen()

print("Waiting for sever: ")
print("Server: ", HOST, SERVER_PORT)
print("Waiting for client...")

conn,addr = s.accept()

print("Client address: ", addr)
print("Conn: ",conn.getsockname())

username = conn.recv(1024).decode(FORMAT)

conn.sendall(username.encode(FORMAT))

psw = conn.recv(1024).decode(FORMAT)

print("Username: ",username)
print("Password: ", psw)


input()

#test