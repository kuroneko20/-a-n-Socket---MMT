import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime
import os

ROOT_FOLDER = "D:\\000MINHTHONG\\Năm 2\\SocketGr\\Server_files" #change root folder in here
HOST = "127.0.0.1"
# IP = "192.168.1.60"
SERVER_PORT = 58773
FORMAT = "utf8"
BUFFER_SIZE = 1024 

# Đường dẫn file lưu trữ tin nhắn
message_log_file = "server_message_log.txt"

def start_server():
    def handle_client(conn, addr):
        try:
            client_name = conn.recv(BUFFER_SIZE).decode()  # Nhận tên client đầu tiên sau khi kết nối
            add_log(f"Client '{client_name}' connected from {addr}", "green")
            
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                
                timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
                if data.startswith(b'FILE:'):
                    # filename = data[5:].decode()
                    # filepath = f"./{filename}"  # Lưu file tạm tại thư mục hiện tại
                    # #Bắt đầu ghi file
                    # with open(filepath, "wb") as f:
                    #     while True:
                    #         data = conn.recv(BUFFER_SIZE)
                    #         if data == b"END":
                    #             break
                    #         f.write(data)
                        
                    # message = f"[{timestamp}] File received from {client_name}: {filename}"
                    # add_log(message, "red")
                    # files_received.append(filepath)
                    # save_message(message)  # Lưu vào file log
                    #response
                    #conn.sendall("OK, send it!".encode(FORMAT))
                                
                    # fileNameInp = conn.recv(BUFFER_SIZE).decode(FORMAT); #receive file name
                            
                    # fileNameOut = ""
                    # for i in range(len(fileNameInp) - 1, -1, -1):
                    #     if (fileNameInp[i] == "\\"):
                    #         fileName = fileNameInp[i + 1:]
                    #         current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                    #         str_current_datetime = str(current_datetime)
                    #         fileNameOut = "output_" + str_current_datetime + "_" + fileName

                    #         break
                                    
                    # destFolderPath = input('Enter the folder path you want to upload file: ') #Nhập đường dẫn thư mục mà file sẽ upload lên đó (Vd: D:\\000MINHTHONG\\Năm 2)
                    # #D:\000MINHTHONG\Năm 2\SocketGr\Server_files\MMT_DATH_Socket_Nov_2024 (1).pdf
                    # destFilePath = destFolderPath + "\\" + fileNameOut 

                    # #response ready to receive data from file
                    # msg = "response"
                    # conn.sendall(msg.encode(FORMAT))

                    filename = data[5:].decode()
                    filepath = f"./{filename}"  # Lưu file tạm tại thư mục hiện tại
                    #Receive file data that needs to be uploaded and upload to the specified folder
                    with open(filepath, "wb") as fo:
                        while True:
                            data = conn.recv(BUFFER_SIZE)
                            if data == b"END":
                                break
                            fo.write(data)        
                            
                    message = f"[{timestamp}] {client_name}: {data.decode()}"
                    add_log(message, "midnightblue")
                    save_message(message)  # Lưu vào file log
        except Exception as e:
            add_log(f"Error with client {addr}: {e}", "red")
        finally:
            conn.close()
            add_log(f"Client '{client_name}' disconnected.", "blue")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 50745))
    server.listen(5)
    add_log("Server started and listening on port 50745", "blue")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def start_server_thread():
    threading.Thread(target=start_server, daemon=True).start()

def download_file():
    if not files_received:
        add_log("No files available to download.", "blue")
        return

    filepath = filedialog.asksaveasfilename(title="Save File", initialfile=files_received[-1].split("/")[-1])
    if filepath:
        try:
            with open(files_received[-1], 'rb') as src, open(filepath, 'wb') as dest:
                dest.write(src.read())
            add_log(f"File saved to: {filepath}", "red")
        except Exception as e:
            add_log(f"Error saving file: {e}", "red")

def add_log(message, color):
    log_area.insert(tk.END, f"{message}\n", color)
    log_area.see(tk.END)

def save_message(message):
    """Ghi tin nhắn vào file lưu trữ."""
    with open(message_log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_previous_messages():
    """Đọc các tin nhắn đã lưu và hiển thị trên giao diện."""
    if os.path.exists(message_log_file):
        with open(message_log_file, "r", encoding="utf-8") as f:
            messages = f.readlines()
            for message in messages:
                add_log(message.strip(), "midnightblue")

def update_clock():
    """Cập nhật thời gian hiện tại trên giao diện."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=f"Current Time: {now}")
    root.after(1000, update_clock)  # Lặp lại sau 1 giây

# Tkinter GUI
root = tk.Tk()
root.title("Server")

# Tiêu đề ứng dụng
title = tk.Label(root, text="Server Application", fg="firebrick", font=("Arial", 16, "bold"))
title.pack()

# Đồng hồ thời gian thực
clock_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
clock_label.pack()

# Khu vực hiển thị log
log_area = scrolledtext.ScrolledText(root, width=50, height=20)
log_area.tag_configure("blue", foreground="blue")
log_area.tag_configure("red", foreground="red")
log_area.tag_configure("green", foreground="green")
log_area.tag_configure("midnightblue", foreground="midnightblue")
log_area.pack()

# Danh sách lưu đường dẫn các file đã nhận
files_received = []

# Nút khởi động server
start_button = tk.Button(root, text="Start Server", command=start_server_thread)
start_button.pack()

# Nút tải xuống file gần nhất
download_button = tk.Button(root, text="Download Last File", command=download_file)
download_button.pack()

# Đọc và hiển thị tin nhắn trước đó
load_previous_messages()

# Bắt đầu cập nhật đồng hồ thời gian thực
update_clock()

root.mainloop()
