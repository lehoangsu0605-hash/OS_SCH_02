import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def parse_processes(rows):
    processes = []
    seen = set()
    for i, row in enumerate(rows, start=1):
        pid = str(row["pid"]).strip()
        if not pid:
            raise ValueError(f"Dòng {i}: PID không được để trống.")
        if pid in seen:
            raise ValueError(f"Dòng {i}: PID '{pid}' bị trùng.")
        seen.add(pid)
        try:
            arrival = int(row["arrival"])
            burst = int(row["burst"])
        except (ValueError, TypeError):
            raise ValueError(f"Dòng {i}: Arrival Time và Burst Time phải là số nguyên.")
        if arrival < 0:
            raise ValueError(f"Dòng {i}: Arrival Time phải >= 0.")
        if burst <= 0:
            raise ValueError(f"Dòng {i}: Burst Time phải > 0.")
        processes.append({"pid": pid, "arrival": arrival, "burst": burst})
    if not processes:
        raise ValueError("Hãy nhập ít nhất một tiến trình.")
    return processes


def calculate_metrics(processes, segments, first_start):
    completion = {}
    for seg in segments:
        if seg["pid"] != "IDLE":
            completion[seg["pid"]] = seg["end"]
    result = []
    for p in processes:
        pid = p["pid"]
        ct = completion[pid]
        tat = ct - p["arrival"]
        wt = tat - p["burst"]
        rt = first_start[pid] - p["arrival"]
        result.append({
            "pid": pid, "arrival": p["arrival"], "burst": p["burst"],
            "start": first_start[pid], "completion": ct,
            "turnaround": tat, "waiting": wt, "response": rt
        })
    return result


def sjf_non_preemptive(processes):
    pending = [dict(p) for p in processes]
    time = 0
    segments = []
    first_start = {}
    done = set()
    while len(done) < len(pending):
        ready = [p for p in pending if p["pid"] not in done and p["arrival"] <= time]
        if not ready:
            next_arrival = min(p["arrival"] for p in pending if p["pid"] not in done)
            if time < next_arrival:
                segments.append({"pid": "IDLE", "start": time, "end": next_arrival})
                time = next_arrival
            continue
        p = min(ready, key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        first_start[p["pid"]] = time
        end = time + p["burst"]
        segments.append({"pid": p["pid"], "start": time, "end": end})
        time = end
        done.add(p["pid"])
    return calculate_metrics(processes, segments, first_start), segments


def srtf_preemptive(processes):
    remaining = {p["pid"]: p["burst"] for p in processes}
    by_pid = {p["pid"]: p for p in processes}
    first_start = {}
    segments = []
    time = 0
    finished = set()
    while len(finished) < len(processes):
        ready = [p for p in processes
                 if p["arrival"] <= time and remaining[p["pid"]] > 0]
        if not ready:
            next_arrival = min(p["arrival"] for p in processes
                               if remaining[p["pid"]] > 0)
            if not segments or segments[-1]["pid"] != "IDLE":
                segments.append({"pid": "IDLE", "start": time, "end": next_arrival})
            else:
                segments[-1]["end"] = next_arrival
            time = next_arrival
            continue
        p = min(ready, key=lambda x: (remaining[x["pid"]], x["arrival"], x["pid"]))
        pid = p["pid"]
        if pid not in first_start:
            first_start[pid] = time
        if segments and segments[-1]["pid"] == pid and segments[-1]["end"] == time:
            segments[-1]["end"] += 1
        else:
            segments.append({"pid": pid, "start": time, "end": time + 1})
        remaining[pid] -= 1
        time += 1
        if remaining[pid] == 0:
            finished.add(pid)
    merged = []
    for seg in segments:
        if merged and merged[-1]["pid"] == seg["pid"] and merged[-1]["end"] == seg["start"]:
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(dict(seg))
    return calculate_metrics(processes, merged, first_start), merged


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS_SCH_02 - Mô phỏng SJF và SRTF")
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.last_results = {}
        self._build_ui()
        self._load_sample()

    def _build_ui(self):
        title = ttk.Label(self.root, text="MÔ PHỎNG LẬP LỊCH CPU: SJF & SRTF",
                          font=("Arial", 17, "bold"))
        title.pack(pady=(12, 6))

        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill="x")
        ttk.Button(controls, text="Thêm tiến trình", command=self.add_row).pack(side="left", padx=3)
        ttk.Button(controls, text="Xóa dòng chọn", command=self.delete_row).pack(side="left", padx=3)
        ttk.Button(controls, text="Tải CSV", command=self.load_csv).pack(side="left", padx=3)
        ttk.Button(controls, text="Lưu input CSV", command=self.save_input_csv).pack(side="left", padx=3)
        ttk.Button(controls, text="Chạy mô phỏng", command=self.run_simulation).pack(side="left", padx=3)
        ttk.Button(controls, text="Xuất kết quả CSV", command=self.export_results).pack(side="left", padx=3)

        entry_frame = ttk.LabelFrame(self.root, text="Danh sách tiến trình", padding=8)
        entry_frame.pack(fill="x", padx=10, pady=5)
        cols = ("pid", "arrival", "burst")
        self.input_tree = ttk.Treeview(entry_frame, columns=cols, show="headings", height=5)
        for col, label, width in [("pid", "PID", 180), ("arrival", "Arrival Time", 180), ("burst", "Burst Time", 180)]:
            self.input_tree.heading(col, text=label)
            self.input_tree.column(col, width=width, anchor="center")
        self.input_tree.pack(fill="x")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=8)
        self.sjf_tab = ttk.Frame(self.tabs, padding=8)
        self.srtf_tab = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(self.sjf_tab, text="SJF không độc quyền")
        self.tabs.add(self.srtf_tab, text="SRTF có độc quyền")
        self.sjf_canvas = tk.Canvas(self.sjf_tab, height=120, background="white")
        self.sjf_canvas.pack(fill="x", pady=(0, 8))
        self.srtf_canvas = tk.Canvas(self.srtf_tab, height=120, background="white")
        self.srtf_canvas.pack(fill="x", pady=(0, 8))
        self.sjf_table = self._make_result_table(self.sjf_tab)
        self.srtf_table = self._make_result_table(self.srtf_tab)

        self.summary = ttk.Label(self.root, text="Nhập dữ liệu rồi nhấn Chạy mô phỏng.",
                                 padding=8, justify="left")
        self.summary.pack(fill="x")

    def _make_result_table(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        cols = ("pid", "arrival", "burst", "start", "completion", "turnaround", "waiting", "response")
        labels = ["PID", "Arrival", "Burst", "Start", "Completion", "Turnaround", "Waiting", "Response"]
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=9)
        for col, label in zip(cols, labels):
            tree.heading(col, text=label)
            tree.column(col, width=95, anchor="center")
        tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        return tree

    def _load_sample(self):
        sample = [
            {"pid": "P1", "arrival": 0, "burst": 7},
            {"pid": "P2", "arrival": 2, "burst": 4},
            {"pid": "P3", "arrival": 4, "burst": 1},
            {"pid": "P4", "arrival": 5, "burst": 4},
        ]
        for item in self.input_tree.get_children():
            self.input_tree.delete(item)
        for p in sample:
            self.input_tree.insert("", "end", values=(p["pid"], p["arrival"], p["burst"]))

    def add_row(self):
        self.input_tree.insert("", "end", values=(f"P{len(self.input_tree.get_children()) + 1}", 0, 1))

    def delete_row(self):
        selected = self.input_tree.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Hãy chọn dòng cần xóa.")
            return
        for item in selected:
            self.input_tree.delete(item)

    def get_input(self):
        rows = []
        for item in self.input_tree.get_children():
            pid, arrival, burst = self.input_tree.item(item, "values")
            rows.append({"pid": pid, "arrival": arrival, "burst": burst})
        return parse_processes(rows)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                required = {"pid", "arrival", "burst"}
                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    raise ValueError("CSV cần có các cột: pid, arrival, burst.")
                rows = list(reader)
            processes = parse_processes(rows)
            for item in self.input_tree.get_children():
                self.input_tree.delete(item)
            for p in processes:
                self.input_tree.insert("", "end", values=(p["pid"], p["arrival"], p["burst"]))
        except Exception as e:
            messagebox.showerror("Không thể tải CSV", str(e))

    def save_input_csv(self):
        try:
            processes = self.get_input()
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["pid", "arrival", "burst"])
                writer.writeheader()
                writer.writerows(processes)
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu đầu vào.")
        except Exception as e:
            messagebox.showerror("Dữ liệu không hợp lệ", str(e))

    def draw_gantt(self, canvas, segments):
        canvas.delete("all")
        if not segments:
            return
        width = max(canvas.winfo_width(), 700)
        left, right = 35, width - 25
        total = max(seg["end"] for seg in segments)
        total = max(total, 1)
        scale = min((right - left) / total, 70)
        used = scale * total
        start_x = left + max(0, ((right - left) - used) / 2)
        colors = ["#a8d5e5", "#f6c98d", "#b9dfb0", "#d7c5f2", "#f2b7c4", "#c8d8f0"]
        for i, seg in enumerate(segments):
            x1 = start_x + seg["start"] * scale
            x2 = start_x + seg["end"] * scale
            color = "#eeeeee" if seg["pid"] == "IDLE" else colors[(sum(map(ord, seg["pid"])) % len(colors))]
            canvas.create_rectangle(x1, 25, x2, 68, fill=color, outline="#333333")
            canvas.create_text((x1 + x2) / 2, 46, text=seg["pid"], font=("Arial", 9))
            canvas.create_text(x1, 82, text=str(seg["start"]), anchor="n", font=("Arial", 8))
        canvas.create_text(start_x + total * scale, 82, text=str(total), anchor="n", font=("Arial", 8))
        switches = sum(1 for i in range(1, len(segments))
                       if segments[i]["pid"] != segments[i - 1]["pid"]
                       and segments[i]["pid"] != "IDLE" and segments[i - 1]["pid"] != "IDLE")
        canvas.create_text(10, 8, anchor="nw",
                           text=f"Thời gian CPU: 0 → {total} | Các đoạn chạy: {len(segments)} | Chuyển giữa tiến trình: {switches}",
                           font=("Arial", 9, "bold"))

    def fill_table(self, tree, results):
        for item in tree.get_children():
            tree.delete(item)
        for r in results:
            tree.insert("", "end", values=(r["pid"], r["arrival"], r["burst"], r["start"],
                                           r["completion"], r["turnaround"], r["waiting"], r["response"]))

    def run_simulation(self):
        try:
            processes = self.get_input()
            sjf_results, sjf_segments = sjf_non_preemptive(processes)
            srtf_results, srtf_segments = srtf_preemptive(processes)
            self.last_results = {
                "SJF": (sjf_results, sjf_segments),
                "SRTF": (srtf_results, srtf_segments),
            }
            self.fill_table(self.sjf_table, sjf_results)
            self.fill_table(self.srtf_table, srtf_results)
            self.root.update_idletasks()
            self.draw_gantt(self.sjf_canvas, sjf_segments)
            self.draw_gantt(self.srtf_canvas, srtf_segments)
            sjf_wt = sum(r["waiting"] for r in sjf_results) / len(sjf_results)
            srtf_wt = sum(r["waiting"] for r in srtf_results) / len(srtf_results)
            sjf_tat = sum(r["turnaround"] for r in sjf_results) / len(sjf_results)
            srtf_tat = sum(r["turnaround"] for r in srtf_results) / len(srtf_results)
            self.summary.config(text=(
                f"SJF: Waiting trung bình = {sjf_wt:.2f}; Turnaround trung bình = {sjf_tat:.2f}.    "
                f"SRTF: Waiting trung bình = {srtf_wt:.2f}; Turnaround trung bình = {srtf_tat:.2f}.\n"
                "Lưu ý: kết quả phụ thuộc dữ liệu đầu vào; SRTF có thể ngắt tiến trình đang chạy khi có tiến trình ngắn hơn đến."
            ))
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", str(e))

    def export_results(self):
        if not self.last_results:
            messagebox.showinfo("Chưa có kết quả", "Hãy chạy mô phỏng trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        fields = ["algorithm", "pid", "arrival", "burst", "start", "completion",
                  "turnaround", "waiting", "response"]
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for algorithm, (results, segments) in self.last_results.items():
                    for r in results:
                        row = {"algorithm": algorithm, **r}
                        writer.writerow(row)
            messagebox.showinfo("Thành công", "Đã xuất kết quả CSV.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
