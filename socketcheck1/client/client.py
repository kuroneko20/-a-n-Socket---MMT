import socket

HOST = "127.0.0.1"
# IP = "10.131.3.60"
SERVER_PORT = 58773
FORMAT = "utf8"

def sendList(client, list):
    for item in list:
        client.sendall(item.encode(FORMAT))
        #wait response
        client.recv(1024)
        
    msg = "end"
    client.send(msg.encode(FORMAT))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("CLIENT SIDE: ")

try:
    client.connect((HOST, SERVER_PORT))
    print("Client adress: ", client.getsockname())
    
    list = ["thong", "20", "hello"]
    
    msg = None
    while (msg != "x"):
        msg = input("talk: ")
        client.sendall(msg.encode(FORMAT))
        #gửi dữ liệu phức tạp
        if (msg == "sendList"):
            #wait response
            client.recv(1024)
            sendList(client, list)
        
except:
    print("Error!")
    
input()

client.close()