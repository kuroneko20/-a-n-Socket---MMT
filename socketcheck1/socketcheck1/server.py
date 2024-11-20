import socket
import threading

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

def handleClient(conn: socket, addr):
    print("conn: ", conn.getsockname())
    
    msg = None
    while (msg != "x"):
        msg = conn.recv(1024).decode(FORMAT)
        print("client ", addr, " says ", msg)
        
        #gửi dữ liệu phức tạp
        if (msg == "sendList"):
            #response
            conn.sendall(msg.encode(FORMAT))
            list = recvList(conn)
            
            print("Receive: ")
            print(list)
            
    print("client ", addr, " finished")
    print("client ", conn.getsockname(), " close")
    conn.close()
        

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Kết nối theo giao thức IP/TCP

s.bind((HOST,SERVER_PORT))
s.listen()

print("Waiting for sever: ")
print("Server: ", HOST, SERVER_PORT)
print("Waiting for client...")

nClient = 0

while (nClient < 3):
    try:
        conn, addr = s.accept()

        thr = threading.Thread(target = handleClient, args = (conn, addr))
        #Nếu daemon = True và số client >= 3 thì server sẽ dừng và mặc kệ client1, client2 vẫn đang chạy,
        #nếu daemon = False thì dù số client >= 3 thì server vẫn sẽ đợi cli1 và cl2 chạy xong rồi mới tắt
        thr.daemon = False
        thr.start()
    
    except:
        print("Error!")
        
    nClient += 1

print("End")
input()

#test