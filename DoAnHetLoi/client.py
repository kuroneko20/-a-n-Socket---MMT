import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext
from datetime import datetime
import os

HOST = "127.0.0.1"
# IP = "192.168.1.60"
SERVER_PORT = 58773
FORMAT = "utf8"
BUFFER_SIZE = 100000 

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
    client.sendall("upload".encode())
    client.recv(1)
    filepath = filedialog.askopenfilename()
        
    if not filepath: #Thông báo lỗi nếu không chọn file để upload
        add_log("No file selected for upload.", "red")
        return
    
    filename = filepath.split("/")[-1]
    timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại
    #reponse file name
    client.send(f"FILE:{filename}".encode())
        
    try:
        # Lấy kích thước file để tính toán tiến độ
        file_size = os.path.getsize(filepath)
        bytes_sent = 0  # Số byte đã gửi
        progress["value"] = 0  # Reset thanh tiến trình
        progress["maximum"] = 100  # Tối đa 100%
        #read data from file to upload và send to server
        with open(filepath, "rb") as fi:
            data = fi.read(BUFFER_SIZE)
            while data:
                client.sendall(data)
                
                bytes_sent += len(data)
                progress_percentage = (bytes_sent / file_size) * 100  # Tính phần trăm
                progress["value"] = progress_percentage  # Cập nhật ProgressBar

                # Cập nhật label phần trăm
                percent_label.config(text=f"{int(progress_percentage)}%")

                root.update_idletasks()  # Làm mới giao diện
                    
                data = fi.read(BUFFER_SIZE)
                    
        client.sendall(b"END")
        print(f"Uploaded successfully: {filepath}")
    except:
        print("File is error to read! Please try again")
        
    finally:
        log_message = f"File sent [{timestamp}]: {filepath}"
        add_log(log_message, "red")  # Thêm thời gian vào log
        save_message(log_message)  # Lưu tin nhắn        
        client.close()  # Đóng kết nối
        root.destroy()  # Thoát giao diện        

def download_file():
    client.sendall("download".encode())
    client.recv(1)

    # Lấy tên file từ trường nhập
    filename = download_entry.get().strip()
    if not filename:
        add_log("Please enter a filename to download.", "red")
        return

    client.sendall(filename.encode())
    data = client.recv(BUFFER_SIZE)
    if not data:
        add_log("No data received from server. File might not exist.", "red")
        return                

    # Hộp thoại lưu file
    filepath = filedialog.asksaveasfilename(
        title="Save File",
        initialfile=filename,  # Tên file mặc định
        filetypes=[("All Files", "*.*")]
    )
    
    if not filepath: #Thông báo lỗi nếu không chọn nơi lưu file
        add_log("No file selected for saving.", "red")
        return

    try:
        # Nhận và ghi dữ liệu file từ server vào tệp tin
        with open(filepath, "wb") as fo:
            while True:
                data = client.recv(BUFFER_SIZE)
                if data == b"END":
                    break
                fo.write(data)

        add_log(f"File downloaded successfully to: {filepath}", "green")
    except Exception as e:
        add_log(f"Error downloading file: {e}", "red")
    
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
    with open(message_log_file, "a", encoding=FORMAT) as f:
        f.write(message + "\n")

def load_previous_messages():
    """Đọc các tin nhắn đã lưu và hiển thị trên giao diện."""
    if os.path.exists(message_log_file):
        with open(message_log_file, "r", encoding=FORMAT) as f:
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

# Thêm ProgressBar vào giao diện
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack()

# Label để hiển thị phần trăm
percent_label = tk.Label(root, text="0%", font=("Arial", 12))
percent_label.pack()

# Thêm trường nhập tên file
download_label = tk.Label(root, text="Enter filename to download:", font=("Arial", 12))
download_label.pack()

download_entry = tk.Entry(root, width=40)
download_entry.pack()

# Nút tải file
download_button = tk.Button(root, text="Download File", command=download_file)
download_button.pack()

# Đọc và hiển thị tin nhắn trước đó
load_previous_messages()

# Bắt đầu cập nhật đồng hồ
update_clock()

# Thêm hàm xử lý đóng cửa sổ
def on_close():
    """Hủy các vòng lặp và thoát ứng dụng."""
    root.quit()  # Thoát vòng lặp chính
    root.destroy()  # Hủy tất cả widget và đóng cửa sổ

# Gắn sự kiện đóng cửa sổ
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
