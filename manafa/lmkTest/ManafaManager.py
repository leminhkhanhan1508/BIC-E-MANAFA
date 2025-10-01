import csv
import json
import time
from manafa.emanafa import EManafa

class ManafaManager:
    def __init__(self):
        self.manafa = None

    def start(self):
        print("Starting Manafa...")
        self.manafa = EManafa()
        self.manafa.init()
        self.manafa.start()
        print("Manafa started successfully.")

    def stop(self,model_size,total_parameters,gflops,data):
        if not self.manafa:
            print("Manafa is not running.")
            return

        self.manafa.stop()

        events = self.manafa.perf_events.events
        if not events:
            print("No perfetto events recorded.")
            return

        begin, end = events[0].time, events[-1].time
        total, per_component, timeline = self.manafa.get_consumption_in_between(begin, end)

        print(f"Total energy consumed: {total} Joules")
        print(f"Elapsed time: {end - begin} secs")
        print("--------------------------------------")
        print("Per-component consumption")
        print(per_component)
        print("--------------------------------------")
        # Gắn cả value và percent
        result = {
            k: {
                "value": v,
                "percent": round(v / total * 100, 2) if total > 0 else 0.0
            }
            for k, v in per_component.items()
        }

        # Xuất JSON
        json_output = json.dumps(result, indent=4)
        print(json_output)
            # Đoạn code mới để xuất ra file CSV
        output_filename = "energy_data.csv"
        
        # Chuẩn bị dữ liệu để ghi
        headers = ['total_energy_J', 'elapsed_time_s',"model_size","total_parameters","GFLOPs"]
        # Thêm tất cả key JSON (đã flattened) vào header
        if data:
            headers += list(data.keys())
        for comp, metrics in result.items():
            # if isinstance(metrics, dict):  # chỉ thêm nếu metrics là dict
            headers += [f"{comp}_value", f"{comp}_percent"]
            # else:
            #     headers += [comp]  # ví dụ "total"
        
        data_row = [total, end - begin,model_size, total_parameters, gflops]
        if data:
            data_row += list(data.values())
        for comp, metrics in result.items():
            data_row += [metrics["value"], metrics["percent"]]

        try:
            # Ghi vào file CSV. Chế độ 'a' để thêm dữ liệu vào cuối file nếu đã tồn tại.
            # newline='' để tránh thêm dòng trống không mong muốn.
            with open(output_filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Nếu file trống, ghi header trước
                if csvfile.tell() == 0:
                    writer.writerow(headers)
                
                # Ghi dữ liệu
                writer.writerow(data_row)
            
            print(f"Successfully exported data to {output_filename}")
            
        except IOError as e:
            print(f"Error writing to CSV file: {e}")
        
