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

server = None
server_thread = None
is_server_running = False  # Trạng thái server
stop_event = threading.Event()  # Sự kiện để dừng server

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
        
# Mã PIN mặc định
SERVER_PIN = "0000"

client_connections = [] 
def handle_client(conn, addr):
    try:
        client_connections.append(conn)  # Lưu kết nối
        client_pin = conn.recv(1024).decode()
        if not client_pin or client_pin != SERVER_PIN:
            conn.send("PIN_FAILED".encode())
            conn.close()
            add_log(f"Authentication failed for client {addr}", "red")
            return

        conn.send("PIN_OK".encode())

        client_name = conn.recv(BUFFER_SIZE).decode()
        if not client_name:
            conn.send("INVALID_CLIENT_NAME".encode())
            conn.close()
            add_log(f"Invalid client name from {addr}. Connection closed.", "red")
            return

        add_log(f"Client '{client_name}' connected from {addr}", "green")

        while not stop_event.is_set():
            mes = conn.recv(BUFFER_SIZE).decode()
            if not mes:
                break
            elif "upload" in mes:
                upload(conn, addr, client_name)
            elif "download" in mes:
                download(conn, addr)
            else:
                message = f"{client_name}: {mes}"
                add_log(message, "midnightblue")
                save_message(message)
    except Exception as e:
        add_log(f"Error with client {addr}: {e}", "red")
    finally:
        conn.close()
        add_log(f"Client from {addr} disconnected.", "blue")

def stop_all_clients():
    """Đóng tất cả các kết nối từ client."""
    for conn in client_connections:
        try:
            conn.close()
        except:
            pass
    client_connections.clear()

def start_server():
    global server, is_server_running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 50745))
    server.listen(5)
    add_log("Server started and listening on port 50745", "blue")

    is_server_running = True

    while not stop_event.is_set():
        try:
            server.settimeout(1.0)  # Timeout để kiểm tra stop_event
            conn, addr = server.accept()
            if stop_event.is_set():
                conn.close()
                break
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
        except OSError:
            break  # Server đã đóng socket

    # Đảm bảo dừng server (không ghi log ở đây nữa)
    stop_all_clients()
    if server:
        server.close()
    server = None
    is_server_running = False

def toggle_server():
    global server_thread, is_server_running, server

    if not is_server_running:
        # Khởi động server
        stop_event.clear()
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        is_server_running = True
        add_log("Starting server...", "green")
        start_button.config(text="Close Server")
    else:
        # Dừng server
        stop_event.set()
        stop_all_clients()  # Đóng tất cả các kết nối client
        if server:
            server.close()  # Đảm bảo đóng socket server
            server = None
        if server_thread and server_thread.is_alive():
            server_thread.join(timeout=2)  # Chờ luồng server dừng
        is_server_running = False
        add_log("Server stopped.", "red")
        start_button.config(text="Start Server")
    
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
root.title("Server Application")
root.after(100, lambda: toggle_server())

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

# Nút khởi động/dừng server
start_button = tk.Button(root, text="Start Server", command=toggle_server)
start_button.pack()

# Đọc và hiển thị tin nhắn trước đó
load_previous_messages()

# Bắt đầu cập nhật đồng hồ thời gian thực
update_clock()

root.mainloop()
