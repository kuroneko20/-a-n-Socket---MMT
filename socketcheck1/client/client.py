import socket

HOST = "127.0.0.1"
# IP = "10.131.3.60"
SERVER_PORT = 58773
FORMAT = "utf8"
BUFFER_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("CLIENT SIDE: ")

try:
    client.connect((HOST, SERVER_PORT))
    print("Client adress: ", client.getsockname())
    
    msg = None
    while (msg != "x"):
        msg = input("talk: ")
        client.sendall(msg.encode(FORMAT))
        #gửi dữ liệu phức tạp
        if (msg == "send file"):
            #wait response
            response = client.recv(BUFFER_SIZE).decode(FORMAT)
            
            #upload file
            if (response == "OK, send it!"):
                fileName = input('The file name of file you want to upload: ') #D:\000MINHTHONG\Năm 2\Vovab\vocab01.txt
                client.sendall(fileName.encode(FORMAT))
                
                client.recv(BUFFER_SIZE).decode(FORMAT)
            
                try:
                    with open(fileName, "rb") as fi:
                        data = fi.read(BUFFER_SIZE)
                        while data:
                            client.sendall(data)
                            data = fi.read(BUFFER_SIZE)
                            
                    client.sendall(b"END")
                except:
                    print("File is error to read! Please try again")
              
        
except:
    print("Error!")
    
input("Press any key to close client!")

client.close()