import socket
import tkinter as tk
from tkinter import filedialog, scrolledtext
from datetime import datetime
import os

# Đường dẫn file lưu trữ tin nhắn
message_log_file = "client_message_log.txt"

def send_message(event=None):  # Thêm tham số event để tương thích với bind
    message = message_entry.get()
    if message.strip():  # Chỉ gửi nếu tin nhắn không rỗng
        timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
        client.send(message.encode())
        log_message = f"You [{timestamp}]: {message}"
        add_log(log_message, "midnightblue")  # Thêm thời gian vào log
        save_message(log_message)  # Lưu tin nhắn
        message_entry.delete(0, tk.END)

def upload_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        filename = filepath.split("/")[-1]
        timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
        client.send(f"FILE:{filename}".encode())
        with open(filepath, 'rb') as f:
            file_data = f.read(1024)
            client.send(file_data)
        log_message = f"File sent [{timestamp}]: {filepath}"
        add_log(log_message, "red")  # Thêm thời gian vào log
        save_message(log_message)  # Lưu tin nhắn

def connect_to_server():
    global client
    client_name = name_entry.get().strip()
    if not client_name:
        add_log("Please enter your name before connecting!", "red")
        return

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 50745))
        client.send(client_name.encode())  # Gửi tên client ngay sau khi kết nối
        add_log(f"Connected to server as '{client_name}'", "green")
        save_message(f"Connected to server as '{client_name}'")  # Lưu tin nhắn
    except Exception as e:
        log_message = f"Error connecting to server: {e}"
        add_log(log_message, "red")
        save_message(log_message)  # Lưu tin nhắn

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
                add_log(message.strip(), "blue")

def update_clock():
    """Cập nhật thời gian hiện tại trên giao diện."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=f"Time: {now}")
    root.after(1000, update_clock)  # Lặp lại sau 1 giây

# Tkinter GUI
root = tk.Tk()
root.title("Client")

# Tiêu đề
title = tk.Label(root, text="Client Application", fg="firebrick", font=("Arial", 16, "bold"))
title.pack()

# Đồng hồ thời gian thực
clock_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
clock_label.pack()

# Nhập tên
name_label = tk.Label(root, text="Enter your name:", font=("Arial", 12))
name_label.pack()

name_entry = tk.Entry(root, width=40)
name_entry.pack()

# Kết nối
connect_button = tk.Button(root, text="Connect to Server", command=connect_to_server)
connect_button.pack()

# Khu vực log
log_area = scrolledtext.ScrolledText(root, width=50, height=20)
log_area.tag_configure("blue", foreground="blue")
log_area.tag_configure("red", foreground="red")
log_area.tag_configure("green", foreground="green")
log_area.tag_configure("midnightblue", foreground="midnightblue")
log_area.pack()

# Nhập tin nhắn
message_entry = tk.Entry(root, width=40)
message_entry.pack()

# Gắn phím Enter để gửi tin nhắn
message_entry.bind("<Return>", send_message)

# Nút gửi tin nhắn
send_button = tk.Button(root, text="Send Message", command=send_message)
send_button.pack()

# Nút gửi file
upload_button = tk.Button(root, text="Upload File", command=upload_file)
upload_button.pack()

# Đọc và hiển thị tin nhắn trước đó
load_previous_messages()

# Bắt đầu cập nhật đồng hồ
update_clock()

root.mainloop()
