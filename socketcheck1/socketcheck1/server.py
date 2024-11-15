
import socket

HOST = "127.0.0.1"
# IP = "192.168.1.60"
SERVER_PORT = 58773
FORMAT = "utf8"

def recvList(conn):
    list = []
    item = None
    while (item != "end"):
        item = conn.recv(1024).decode(FORMAT)
        list.append(item)
        #response
        conn.sendall(item.encode(FORMAT))
        
    return list

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Kết nối theo giao thức IP/TCP

s.bind((HOST,SERVER_PORT))
s.listen()

print("Waiting for sever: ")
print("Server: ", HOST, SERVER_PORT)
print("Waiting for client...")

try:
    conn, addr = s.accept()

    print("Client address: ", addr)
    print("Conn: ",conn.getsockname())

    msg = None
    while (msg != "x"):
        msg = conn.recv(1024).decode(FORMAT)
        print("client ", addr, " says ", msg)
        
        if (msg == "sendL"):
            #response
            conn.sendall(msg.encode(FORMAT))
            list = recvList(conn)
            
            print("Receive: ")
            print(list)
    
except:
    print("Error!")


input()

#test