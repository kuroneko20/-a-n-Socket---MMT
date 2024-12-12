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
BUFFER_SIZE = 1024 

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
    def upload_task():  # Tách logic ra thành một hàm con chạy trên luồng
        try:
            client.sendall("upload".encode())
            client.recv(1)
            
            # Hiển thị thanh Progress khi bắt đầu
            progress.pack(pady=5)
            percent_label.pack(pady=5)
            client.sendall("upload".encode())
            client.recv(1)
            
            filepath = filedialog.askopenfilename()
                
            if not filepath:  # Thông báo lỗi nếu không chọn file để upload
                add_log("No file selected for upload.", "red")
                return
            
            filename = filepath.split("/")[-1]
            timestamp = datetime.now().strftime("%H:%M:%S")  # Lấy thời gian hiện tại

            # Gửi tên file đến server
            client.send(f"FILE:{filename}".encode())
            
            try:
                # Lấy kích thước file để tính toán tiến độ
                file_size = os.path.getsize(filepath)
                bytes_sent = 0  # Số byte đã gửi
                progress["value"] = 0  # Reset thanh tiến trình
                progress["maximum"] = 100  # Tối đa 100%

                # Đọc dữ liệu từ file và gửi đến server
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
            except Exception as e:
                print(f"Error reading or sending file: {e}")
            
            finally:
                # Hiển thị thanh Progress thêm 3 giây trước khi ẩn
                root.after(3000, lambda: progress.pack_forget())
                root.after(3000, lambda: percent_label.pack_forget())
                
                log_message = f"File sent [{timestamp}]: {filepath}"
                add_log(log_message, "red")  # Thêm thời gian vào log
                save_message(log_message)  # Lưu tin nhắn        
        except Exception as e:
            add_log(f"Error in upload: {e}", "red")
    
    # Tạo và chạy luồng riêng cho upload_file
    upload_thread = threading.Thread(target=upload_task)
    upload_thread.start()

def download_file():
    def start_download(filename):
        client.sendall("download".encode())        
        try:

            client.recv(1)  # Xác nhận server sẵn sàng

            # Hiển thị thanh Progress khi bắt đầu
            progress.pack(pady=5)
            percent_label.pack(pady=5)

            client.sendall(filename.encode())
            # Nhận phản hồi từ server: kiểm tra xem file có tồn tại không
            server_response = client.recv(BUFFER_SIZE).decode(errors='ignore')
            if server_response == "FILE_NOT_FOUND":
                add_log(f"File '{filename}' not found on the server.", "red")
                return  # Không tiếp tục, không mở hộp thoại lưu file  

            # Hộp thoại lưu file
            filepath = filedialog.asksaveasfilename(
                title="Save File",
                initialfile=filename,  # Tên file mặc định
                filetypes=[("All Files", "*.*")]
            )

            if not filepath:  # Thông báo lỗi nếu không chọn nơi lưu file
                add_log("No file selected for saving.", "red")
                progress.pack_forget()
                percent_label.pack_forget()
                return

            # Nhận và ghi dữ liệu file từ server vào tệp tin
            total_received = 0
            with open(filepath, "wb") as fo:
                client.settimeout(10.0)  # Đặt timeout cho kết nối (10 giây)
                while True:
                    try:
                        data = client.recv(BUFFER_SIZE)
                        if not data or data == b"END":  # Kiểm tra tín hiệu kết thúc
                            break
                        fo.write(data)
                        total_received += len(data)
                        # Tạm thời giả lập tiến độ (cập nhật mỗi lần nhận dữ liệu)
                        progress["value"] = (total_received / BUFFER_SIZE) * 100
                        percent_label.config(text=f"Receiving...")
                        root.update_idletasks()
                    except socket.timeout:
                        add_log("Connection timeout while downloading file.", "red")
                        break

            add_log(f"File downloaded successfully to: {filepath}", "green")
        except Exception as e:
            add_log(f"Error downloading file: {e}", "red")
        finally:
            client.settimeout(None)  # Reset timeout về mặc định
            # Hiển thị thanh Progress thêm 3 giây trước khi ẩn
            root.after(3000, lambda: progress.pack_forget())
            root.after(3000, lambda: percent_label.pack_forget())

    def show_filename_prompt():
        def on_submit():
            filename = filename_entry.get().strip()
            if filename:
                filename_prompt.destroy()
                # Tạo luồng mới để tải file
                download_thread = threading.Thread(target=start_download, args=(filename,))
                download_thread.daemon = True  # Kết thúc thread nếu chương trình dừng
                download_thread.start()
            else:
                add_log("Please enter a valid filename.", "red")

        filename_prompt = tk.Toplevel(root)
        filename_prompt.title("Enter Filename")

        tk.Label(filename_prompt, text="Enter the filename to download:").pack(pady=5)

        filename_entry = tk.Entry(filename_prompt, width=30)
        filename_entry.pack(pady=5)

        submit_button = tk.Button(filename_prompt, text="Download", command=on_submit)
        submit_button.pack(pady=5)

        filename_entry.bind("<Return>", lambda _: on_submit())
        filename_entry.focus_set()

    show_filename_prompt()

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
        
        # Cập nhật nút: ẩn Connect, hiện Disconnect
        connect_button.config(text="Disconnect from Server", command=disconnect_from_server)
    except Exception as e:
        log_message = f"Error connecting to server: {e}"
        add_log(log_message, "red")
        save_message(log_message)  # Lưu tin nhắn

def disconnect_from_server():
    """Đóng kết nối và thoát giao diện."""
    try:
        client.close()  # Đóng kết nối với server
        add_log("Disconnected from server.", "red")
    except:
        add_log("Error while disconnecting.", "red")
    finally:
        root.destroy()  # Thoát giao diện

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

# Nút ngắt kết nối (ẩn ban đầu)
disconnect_button = tk.Button(root, text="Disconnect from Server", command=disconnect_from_server)
disconnect_button.pack_forget()  # Ẩn nút Disconnect ban đầu

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

# Frame chính chứa 2 cột
main_frame = tk.Frame(root)
main_frame.pack(pady=10)

# Frame bên trái
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=10, sticky="n")

# Frame bên phải
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=10, sticky="n")

# Bên trái: Upload và Progress
upload_button = tk.Button(left_frame, text="Upload File", command=upload_file)
upload_button.pack(pady=5)

progress = ttk.Progressbar(left_frame, orient="horizontal", length=150, mode="determinate")

percent_label = tk.Label(left_frame, text="0%", font=("Arial", 12))

# Bên phải: Download và Progress

download_button = tk.Button(right_frame, text="Download File", command=download_file)
download_button.pack(pady=5)

progress = ttk.Progressbar(left_frame, orient="horizontal", length=150, mode="determinate")

percent_label = tk.Label(left_frame, text="0%", font=("Arial", 12))

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
