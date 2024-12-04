import socket

HOST = "127.0.0.1"

# IP (Thong) = "10.131.7.226"
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
        if (msg.find("upload") != -1): #Ex: upload D:\000MINHTHONG\Năm 2\Vovab\vocab01.txt
            #wait response
            response = client.recv(BUFFER_SIZE).decode(FORMAT)
            
            #upload file
            if (response == "OK, send it!"):
                index = msg.find(" ")
                fileName = msg[index + 1:] 
                
                #reponse file name
                client.sendall(fileName.encode(FORMAT))
                
                client.recv(BUFFER_SIZE).decode(FORMAT)
            
                try:
                    #read data from file to upload và send to server
                    with open(fileName, "rb") as fi:
                        data = fi.read(BUFFER_SIZE)
                        while data:
                            client.sendall(data)
                            data = fi.read(BUFFER_SIZE)
                            
                    client.sendall(b"END")
                    
                except:
                    print("File is error to read! Please try again")
                    
                msg = "x"
              
        
except:
    print("Error!")
    
input("Press any key to close client!")

client.close()