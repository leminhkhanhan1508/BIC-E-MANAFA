import subprocess
import time

from manafa.emanafa import EManafa
from ManafaManager import ManafaManager
from ReadLogManager import ReadLogManager
# 1. Định nghĩa các biến cần thiết
PACKAGE_NAME = "com.example.aimodelbench"  # Thay bằng package name của ứng dụng của bạn
ACTIVITY_NAME = "com.example.aimodelbench.MainActivity" # Thay bằng main activity của ứng dụng
# Thay thế bằng log tag và thông điệp bạn muốn kiểm tra
LOG_TAG = "LMKTAG"
MODEL_SIZE = 0
TOTAL_PARAMETERS = 0
GFLOPS = 0
FINISH_MESSAGE = "myFunction: execution finished" 
def run_adb_command(command):
    """Hàm chạy lệnh adb và trả về kết quả."""
    try:
        process = subprocess.run(command, check=True, text=True, capture_output=True, shell=True)
        print(f"Lệnh thành công: {' '.join(command)}")
        print("Output:", process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy lệnh: {' '.join(command)}")
        print("Lỗi:", e.stderr)
        return False
    return True

# 2. Quy trình tự động hóa
def auto_profile_app():
    
    print("Bắt đầu quy trình tự động hóa...")
    manager = ManafaManager()
    log_manager = ReadLogManager(log_tag=LOG_TAG, finish_log_message=FINISH_MESSAGE)

    manager.start()
    print("Profiling đang chạy...")
    # Bắt đầu lắng nghe log
    log_manager.start_listening()

    # Bước 1: Khởi động ứng dụng
    print("Khởi động ứng dụng...")
    start_app_command = f"adb shell am start -n {PACKAGE_NAME}/{ACTIVITY_NAME}"
    if not run_adb_command(start_app_command):
        return
       
    # Vòng lặp chính để chờ log kết thúc
    while not log_manager.is_finish(
            callback=lambda data:  (
                print("\n🎉 Đã tìm thấy log kết thúc."),
                manager.stop(model_size=MODEL_SIZE,
                            total_parameters= TOTAL_PARAMETERS,
                            gflops= GFLOPS,
                            data=data),
                print("\nDừng ứng dụng..."),
                run_adb_command(f"adb shell am force-stop {PACKAGE_NAME}"),
                print("Quy trình profiling đã hoàn thành.")
            )
        ):
            print("Đang chờ log kết thúc...")
            time.sleep(0.5) # Chờ 0.5 giây trước khi kiểm tra lại

# Chạy auto_profile_app nhiều lần theo tham số truyền vào.
# :param number_of_runs: số lần chạy
# :param interval_seconds: số giây nghỉ giữa các lần chạy (mặc định = 0, tức là không nghỉ)
def main(number_of_runs: int, interval_seconds: int = 0):
    for run_index in range(1, number_of_runs + 1):
        print(f"--- Bắt đầu lần chạy thứ {run_index} ---")
        auto_profile_app()
        if interval_seconds > 0 and run_index < number_of_runs:
            print(f"Nghỉ {interval_seconds} giây...")
            time.sleep(interval_seconds) # nghỉ interval_seconds giây giữa các lần

# 3. Chạy hàm chính
if __name__ == "__main__":
    main(number_of_runs=1, interval_seconds=2)