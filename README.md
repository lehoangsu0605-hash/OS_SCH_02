# OS_SCH_02 - SJF và SRTF

## Mô tả
Ứng dụng desktop Python + Tkinter mô phỏng:
- SJF không độc quyền (Non-preemptive)
- SRTF có độc quyền (Preemptive)
- Biểu đồ Gantt
- Completion Time, Turnaround Time, Waiting Time, Response Time
- Đọc/lưu input CSV và xuất kết quả CSV

## Yêu cầu
- Python 3.10 trở lên
- Tkinter (thường được tích hợp sẵn trong Python trên Windows)

## Cách chạy trên Windows
1. Giải nén thư mục dự án.
2. Mở thư mục bằng VS Code.
3. Mở Terminal tại thư mục dự án.
4. Chạy: `python main.py`
5. Dữ liệu mẫu được nạp sẵn. Nhấn `Chạy mô phỏng`.
6. Có thể thêm/xóa tiến trình hoặc tải `input/sample_processes.csv`.

Nếu lệnh `python` không hoạt động, thử `py main.py`.

## Định dạng CSV đầu vào
CSV phải có ba cột: `pid,arrival,burst`.
- `pid`: mã tiến trình, không trùng.
- `arrival`: thời điểm đến, số nguyên >= 0.
- `burst`: thời gian CPU, số nguyên > 0.

## Công thức
- Completion Time (CT): thời điểm tiến trình hoàn thành.
- Turnaround Time (TAT) = CT - Arrival Time.
- Waiting Time (WT) = TAT - Burst Time.
- Response Time (RT) = thời điểm chạy lần đầu - Arrival Time.

## Cấu trúc
- `main.py`: mã nguồn chương trình.
- `input/sample_processes.csv`: dữ liệu mẫu.
- `tests/test_cases.csv`: các bộ dữ liệu kiểm thử.
- `report/report.md`: khung báo cáo để hoàn thiện.
- `output/`: nơi lưu kết quả xuất ra.

## Lưu ý
Đây là mô phỏng lập lịch CPU ở mức thuật toán. Thời gian chuyển ngữ cảnh thực tế được giả định bằng 0; số lần chuyển tiến trình được minh họa trong biểu đồ.
