import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime
import os

HOST = "127.0.0.1"
SERVER_PORT = 58773
FORMAT = "utf8"
BUFFER_SIZE = 1024

# Đường dẫn file lưu trữ tin nhắn
message_log_file = "server_message_log.txt"

def upload(conn,addr,client_name):
    while True:
        conn.sendall("Ok, you can upload!".encode())
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
                
        timestamp_fn = datetime.now().strftime("%H%M%S")  # Lấy thời gian hiện tại thêm vào tên file để đảm bảo tính duy nhất
        timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
        if data.startswith(b'FILE:'):
            filename = data[5:].decode()
            filepath = f"./uploadfile/{client_name}_{timestamp_fn}_{filename}"  # Lưu file tạm tại thư mục hiện tại với tên file phân biệt
           
            with open(filepath, "wb") as fo:
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if data == b"END":
                        break
                    fo.write(data)                                 
            message = f"[{timestamp}] {client_name}: {data.decode()}"
            add_log(message, "midnightblue")
            save_message(message)  # Lưu vào file log
            print(f"File received successfully: {filepath}")
        else:
            print("Invalid data received from client")

def download(conn,addr):
    while True:
        conn.sendall("Ok, you can download".encode())
        filename = conn.recv(BUFFER_SIZE).decode()
        filepath = f"./uploadfile/{filename}"   
        timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
        
        if not os.path.exists(filepath):  # Kiểm tra nếu file không tồn tại
            conn.sendall(b"FILE_NOT_FOUND")  # Gửi thông báo lỗi về client
            print(f"File '{filename}' not found on the server.")
            continue
        
        try:
            file_size = os.path.getsize(filepath)  # Lấy kích thước file
            conn.sendall(f"{file_size}".encode())  # Gửi kích thước file cho client
            
            with open(filepath, "rb") as fi:
                data = fi.read(BUFFER_SIZE)
                while data:
                    conn.sendall(data)
                    data = fi.read(BUFFER_SIZE)
                        
            conn.sendall(b"END")
            print(f"Download successfully: {filepath}")
        except:
            print("File is error to read! Please try again") 
            
        log_message = f"File sent [{timestamp}]: {filepath}"
        add_log(log_message, "red")  # Thêm thời gian vào log
        save_message(log_message)  # Lưu tin nhắn    
        
def start_server():
    def handle_client(conn, addr):
        try:
            client_name = conn.recv(BUFFER_SIZE).decode()  # Nhận tên client đầu tiên sau khi kết nối
            add_log(f"Client '{client_name}' connected from {addr}", "green")
            
            timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
            while True:
                mes = conn.recv(BUFFER_SIZE).decode()
                if not mes: #Xử lí trường hợp tin nhắn rỗng hoặc k hợp lệ
                    break
                
                elif mes.find("upload")!=-1: #Lệnh upload file
                    upload(conn,addr,client_name)
                    
                elif mes.find("download")!=-1: #Lệnh download file
                    download(conn,addr)
                    
                else: #Tin nhắn được gửi từ client
                    message = f"[{timestamp}] {client_name}: {mes}"
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

# Đọc và hiển thị tin nhắn trước đó
load_previous_messages()

# Bắt đầu cập nhật đồng hồ thời gian thực
update_clock()

root.mainloop()
