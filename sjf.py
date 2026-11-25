from copy import deepcopy


def run_sjf_non_preemptive(processes):
    if not processes:
        return {"schedule": [], "gantt_chart": [], "metrics": {}}

    proc_list = deepcopy(processes)
    n = len(proc_list)

    for p in proc_list:
        p["is_completed"] = False

    current_time = 0
    completed_count = 0
    total_idle_time = 0
    gantt_chart = []
    completed_processes = []

    while completed_count < n:
        available_processes = [
            p
            for p in proc_list
            if p["arrival_time"] <= current_time and not p["is_completed"]
        ]

        if not available_processes:
            next_arrival = min(
                p["arrival_time"] for p in proc_list if not p["is_completed"]
            )
            gantt_chart.append({
                "id": "IDLE",
                "start": current_time,
                "end": next_arrival,
            })
            total_idle_time += next_arrival - current_time
            current_time = next_arrival
            continue

        selected_proc = min(
            available_processes,
            key=lambda x: (x["burst_time"], x["arrival_time"], x["id"]),
        )

        start_time = current_time
        completion_time = start_time + selected_proc["burst_time"]
        turnaround_time = completion_time - selected_proc["arrival_time"]
        waiting_time = turnaround_time - selected_proc["burst_time"]
        response_time = waiting_time

        selected_proc["start_time"] = start_time
        selected_proc["completion_time"] = completion_time
        selected_proc["turnaround_time"] = turnaround_time
        selected_proc["waiting_time"] = waiting_time
        selected_proc["response_time"] = response_time
        selected_proc["is_completed"] = True

        gantt_chart.append(
            {"id": selected_proc["id"], "start": start_time, "end": completion_time}
        )

        current_time = completion_time
        completed_count += 1
        completed_processes.append(selected_proc)

    completed_processes.sort(key=lambda x: x["id"])
    for p in completed_processes:
        del p["is_completed"]

    avg_waiting_time = sum(p["waiting_time"] for p in completed_processes) / n
    avg_turnaround_time = (
        sum(p["turnaround_time"] for p in completed_processes) / n
    )
    avg_response_time = sum(p["response_time"] for p in completed_processes) / n
    total_time = current_time
    cpu_utilization = (
        ((total_time - total_idle_time) / total_time) * 100
        if total_time > 0
        else 0
    )

    return {
        "schedule": completed_processes,
        "gantt_chart": gantt_chart,
        "metrics": {
            "avg_waiting_time": round(avg_waiting_time, 2),
            "avg_turnaround_time": round(avg_turnaround_time, 2),
            "avg_response_time": round(avg_response_time, 2),
            "total_time": total_time,
            "cpu_utilization": round(cpu_utilization, 2),
        },
    }


if __name__ == "__main__":
    test_data_1 = [
        {"id": "P1", "arrival_time": 0, "burst_time": 7},
        {"id": "P2", "arrival_time": 2, "burst_time": 4},
        {"id": "P3", "arrival_time": 4, "burst_time": 1},
        {"id": "P4", "arrival_time": 5, "burst_time": 4},
    ]

    result = run_sjf_non_preemptive(test_data_1)

    print("--- BIEU DO GANTT ---")
    for block in result["gantt_chart"]:
        print(f"[{block['start']} -> {block['end']}]: {block['id']}")

    print("\n--- BANG KET QUA CHI TIET ---")
    print(f"{'ID':<5} {'AT':<5} {'BT':<5} {'ST':<5} {'CT':<5} {'TAT':<5} {'WT':<5}")
    for p in result["schedule"]:
        print(
            f"{p['id']:<5} {p['arrival_time']:<5} {p['burst_time']:<5} "
            f"{p['start_time']:<5} {p['completion_time']:<5} "
            f"{p['turnaround_time']:<5} {p['waiting_time']:<5}"
        )

    print("\n--- CHI SO TRUNG BINH ---")
    print(f"AVG WT: {result['metrics']['avg_waiting_time']}")
    print(f"AVG TAT: {result['metrics']['avg_turnaround_time']}")
    print(f"CPU Utilization: {result['metrics']['cpu_utilization']}%")
