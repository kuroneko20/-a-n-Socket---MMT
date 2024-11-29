from pickle import TRUE
import socket
import threading

HOST = "127.0.0.1"
# IP = "192.168.1.60"
SERVER_PORT = 58773
FORMAT = "utf8"
BUFFER_SIZE = 1024 

def handleClient(conn: socket, addr, nClient):
    print("conn: ", conn.getsockname())
    
    msg = None
    while (msg != "x"):
        msg = conn.recv(BUFFER_SIZE).decode(FORMAT)
        print("client ", addr, " says ", msg)
        
        #upload file
        if(msg.find("upload") != -1):
            #response
            conn.sendall("OK, send it!".encode(FORMAT))
            
            fileNameInp = conn.recv(BUFFER_SIZE).decode(FORMAT); #receive file name
           
            fileNameOut = ""
            for i in range(len(fileNameInp) - 1, -1, -1):
                if (fileNameInp[i] == "\\"):
                    fileName = fileNameInp[i + 1:len(fileNameInp) - 1]
                    fileNameOut = "output_" + fileName
                    
                    break
                
            destFolderPath = input('Enter the folder path you want to upload file: ') #Nhập đường dẫn thư mục mà file sẽ upload lên đó (Vd: D:\\000MINHTHONG\\Năm 2)
            destFilePath = destFolderPath + "\\" + fileNameOut 

            conn.sendall(msg.encode(FORMAT))

            #nhận dữ liệu file cần được upload và upload lên thư mục chỉ định
            with open(destFilePath, "wb") as fo:
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if data == b"END":
                        break;
                    fo.write(data)
                   
            print() 
            print('Receiving file from client', nClient)
            print('Received successfully! New filename is:', fileNameOut)
    
            
    print("client ", addr, " finished")
    print("client(", nClient, ") ", conn.getsockname(), " close")
    conn.close()
        

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Kết nối theo giao thức IP/TCP

s.bind((HOST,SERVER_PORT))
s.listen()

print("Waiting for sever: ")
print("Server: ", HOST, SERVER_PORT)
print("Waiting for client...")

nClient = 0

while (TRUE):
    try:
        conn, addr = s.accept()

        thr = threading.Thread(target = handleClient, args = (conn, addr, nClient))
        
        thr.daemon = False
        thr.start()
    
    except:
        print("Error!")
        
    nClient += 1

print("End")
input()

#test