# DỮ LIỆU KIỂM THỬ VÀ KẾT QUẢ TÍNH TOÁN - THUẬT TOÁN SJF (NON-PREEMPTIVE)

---

## Bộ Test 1: Các tiến trình đến ở thời điểm khác nhau (Cơ bản)

### 1. Dữ liệu đầu vào
| Tiến trình | Arrival Time (AT) | Burst Time (BT) |
| :--- | :---: | :---: |
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

### 2. Kết quả tính toán đối chiếu
* **Biểu đồ Gantt:** `[0 -> 7] P1` | `[7 -> 8] P3` | `[8 -> 12] P2` | `[12 -> 16] P4`
* **Bảng chỉ số:**

| Tiến trình | AT | BT | Start (ST) | Completion (CT) | Turnaround (TAT) | Waiting (WT) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 0 | 7 | 0 | 7 | 7 | 0 |
| **P2** | 2 | 4 | 8 | 12 | 10 | 6 |
| **P3** | 4 | 1 | 7 | 8 | 4 | 3 |
| **P4** | 5 | 4 | 12 | 16 | 11 | 7 |

* **Trung bình:** `AVG WT = 4.0` | `AVG TAT = 8.0` | `CPU Utilization = 100%`

---

## Bộ Test 2: Trường hợp CPU bị rảnh (IDLE) và đồng hạng Burst Time

### 1. Dữ liệu đầu vào
| Tiến trình | Arrival Time (AT) | Burst Time (BT) |
| :--- | :---: | :---: |
| P1 | 1 | 3 |
| P2 | 6 | 4 |
| P3 | 7 | 2 |
| P4 | 8 | 4 |

### 2. Kết quả tính toán đối chiếu
* **Biểu đồ Gantt:** `[0 -> 1] IDLE` | `[1 -> 4] P1` | `[4 -> 6] IDLE` | `[6 -> 10] P2` | `[10 -> 12] P3` | `[12 -> 16] P4`
* **Bảng chỉ số:**

| Tiến trình | AT | BT | Start (ST) | Completion (CT) | Turnaround (TAT) | Waiting (WT) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 1 | 3 | 1 | 4 | 3 | 0 |
| **P2** | 6 | 4 | 6 | 10 | 4 | 0 |
| **P3** | 7 | 2 | 10 | 12 | 5 | 3 |
| **P4** | 8 | 4 | 12 | 16 | 8 | 4 |

* **Trung bình:** `AVG WT = 1.75` | `AVG TAT = 5.0` | `CPU Utilization = 81.25%`
