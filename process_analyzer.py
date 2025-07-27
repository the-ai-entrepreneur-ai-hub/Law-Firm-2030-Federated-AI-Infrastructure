import subprocess
import os

# List of critical process names that should not be killed.
# This list is not exhaustive and might need to be adjusted.
CRITICAL_PROCESSES = [
    "svchost.exe",
    "wininit.exe",
    "csrss.exe",
    "winlogon.exe",
    "lsass.exe",
    "services.exe",
    "explorer.exe",
    "spoolsv.exe",
    "taskhostw.exe",
    "dwm.exe",
    "conhost.exe",
    "runtimebroker.exe",
    "system",
    "registry",
    "smss.exe",
    "sihost.exe",
    "fontdrvhost.exe",
    "ctfmon.exe"
]

# CPU time threshold in seconds. Processes with less CPU time than this will be considered idle.
# WMIC reports time in 100-nanosecond units. 1 second = 10,000,000 of these units.
# Let's set a threshold of 5 seconds of total CPU time.
CPU_TIME_THRESHOLD = 5 * 10_000_000

def analyze_processes():
    """
    Analyzes running processes to identify potentially idle ones and suggests killing them.
    """
    try:
        # Get process list from WMIC
        wmic_cmd = "wmic process get Name,ProcessId,UserModeTime,KernelModeTime,WorkingSetSize"
        output = subprocess.check_output(wmic_cmd, shell=True, text=True, stderr=subprocess.DEVNULL)

        processes = []
        lines = output.strip().split('\n')
        # The first line is the header, we can find the column positions from it
        header = lines[0]
        # Find the start index of each column
        kernel_mode_time_idx = header.find("KernelModeTime")
        name_idx = header.find("Name")
        process_id_idx = header.find("ProcessId")
        user_mode_time_idx = header.find("UserModeTime")
        working_set_size_idx = header.find("WorkingSetSize")

        for line in lines[1:]:
            if not line.strip():
                continue
            try:
                kernel_mode_time_str = line[kernel_mode_time_idx:name_idx].strip()
                name = line[name_idx:process_id_idx].strip()
                process_id_str = line[process_id_idx:user_mode_time_idx].strip()
                user_mode_time_str = line[user_mode_time_idx:working_set_size_idx].strip()
                working_set_size_str = line[working_set_size_idx:].strip()

                kernel_mode_time = int(kernel_mode_time_str) if kernel_mode_time_str else 0
                process_id = int(process_id_str) if process_id_str else 0
                user_mode_time = int(user_mode_time_str) if user_mode_time_str else 0
                working_set_size = int(working_set_size_str) if working_set_size_str else 0

                processes.append({
                    "name": name,
                    "pid": process_id,
                    "cpu_time": user_mode_time + kernel_mode_time,
                    "memory": working_set_size
                })
            except (ValueError, IndexError) as e:
                print(f"Could not parse line: '{line}'. Error: {e}")
                continue

        idle_processes = []
        for p in processes:
            if p['name'].lower() not in CRITICAL_PROCESSES and p['cpu_time'] < CPU_TIME_THRESHOLD:
                idle_processes.append(p)

        if not idle_processes:
            print("No idle processes found to suggest killing.")
            return

        print("The following processes are identified as potentially idle and safe to kill.")
        print("They are not critical system processes and have low CPU usage.")
        print("-" * 80)
        print(f"{'Process Name':<30} {'PID':<10} {'Memory (KB)':<15} {'CPU Time (s)':<15}")
        print("-" * 80)

        for p in idle_processes:
            mem_kb = p['memory'] / 1024
            cpu_s = p['cpu_time'] / 10_000_000
            print(f"{p['name']:<30} {p['pid']:<10} {mem_kb:<15.2f} {cpu_s:<15.2f}")

        print("\n" + "="*80)
        print("WARNING: Killing processes can cause data loss or system instability.")
        print("Review the list carefully. If you are unsure, do not proceed.")
        print("="*80 + "\n")

        print("To kill all the processes listed above, run the following commands in your terminal:")
        print("-" * 80)
        for p in idle_processes:
            print(f"taskkill /F /PID {p['pid']}")
        print("-" * 80)

    except FileNotFoundError:
        print("WMIC command not found. This script is intended for Windows.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    analyze_processes()