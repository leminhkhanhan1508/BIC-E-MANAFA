import json
import subprocess
import threading
import queue
import time
class ReadLogManager:
    """
    Một trình quản lý để đọc log từ thiết bị Android thông qua ADB.
    Nó lắng nghe log trên một thread riêng biệt và có thể kiểm tra xem
    một log kết thúc cụ thể đã xuất hiện chưa.
    """
    def __init__(self, log_tag, finish_log_message):
        self.log_tag = log_tag
        self.finish_log_message = finish_log_message
        self.log_queue = queue.Queue()
        self.log_thread = None
        self.is_finished = False
        self.stop_event = threading.Event()
        self.process = None

    def _read_logcat(self):
        """
        Hàm private để chạy trong một thread riêng, đọc log từ adb.
        """
        # Lệnh ADB để lọc log dựa trên tag đã cho
        cmd = ["adb", "logcat", "-s", f"{self.log_tag}:I", "*:S"]
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            # Đọc log cho đến khi sự kiện dừng được kích hoạt
            for line in iter(self.process.stdout.readline, ""):
                if self.stop_event.is_set():
                    break
                self.log_queue.put(line.strip())

        except Exception as e:
            print(f"Lỗi khi bắt đầu adb logcat: {e}")
        finally:
            if self.process:
                self.process.stdout.close()
                self.process.wait()
                self.process = None

    def start_listening(self):
        """
        Bắt đầu lắng nghe log trên một thread mới.
        """
        if self.log_thread is None or not self.log_thread.is_alive():
            print(f"Bắt đầu lắng nghe log với tag: {self.log_tag}")
            self.log_thread = threading.Thread(target=self._read_logcat, daemon=True)
            self.log_thread.start()

    def stop_listening(self):
        """
        Dừng thread lắng nghe log.
        """
        if self.process:
            self.process.terminate()
        self.stop_event.set()
        if self.log_thread:
            self.log_thread.join()
            print("Đã dừng lắng nghe log.")

    def is_finish(self, callback=None):
        """
        Kiểm tra xem thông điệp log kết thúc đã được tìm thấy chưa.
        Nếu tìm thấy, gọi hàm callback và trả về True.
        Ngược lại, trả về False.
        """
        if self.is_finished:
            return True
        data = None
        while not self.log_queue.empty():
            log_line = self.log_queue.get()
            print(f"Đã nhận log: {log_line}")
            # Tìm JSON trong log
            json_start = log_line.find('{')
            if json_start != -1:
                json_str = log_line[json_start:]
                data = json.loads(json_str)
            if self.finish_log_message in log_line:
                self.is_finished = True
                
                # Gọi hàm callback nếu được cung cấp
                if callback and callable(callback):
                    print("Gọi hàm callback...")
                    callback(data)
                
                self.stop_listening() # Dừng lắng nghe ngay khi tìm thấy log
                return True
        
        return False