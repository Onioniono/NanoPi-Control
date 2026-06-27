import subprocess
import csv
from datetime import datetime
from pathlib import Path
import time

### Configuration #####################################

SSH_KEY = r"C:\Users\ajmen\.ssh\nanopi_telemetry"
SSH_TARGET = "amend@10.8.0.1"

BASE_DIR = Path(__file__).resolve().parent.parent # from .py to ~/tools to ~/NanoPi-Control
DATA_DIR = BASE_DIR / "data"
GRAPH_DIR = BASE_DIR / "graphs"
TOOLS_DIR = BASE_DIR / "tools"

CSV_PATH = DATA_DIR / "baseline.csv"

SAMPLE_INTERVAL = 5 # seconds
TOTAL_DURATION = 60 # seconds
SAMPLES = TOTAL_DURATION // SAMPLE_INTERVAL

### Function to run SSH command and return output #####################

def run_ssh(command):
    result = subprocess.run(
        ["ssh", "-i", SSH_KEY, SSH_TARGET, command],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

#### Collect Metrics #####################################

timestamp = datetime.now().isoformat(timespec="seconds")
loadavg = run_ssh("cat /proc/loadavg")
memory = run_ssh("free -m")
disk = run_ssh("df -h /")
temp = run_ssh("cat /sys/class/thermal/thermal_zone0/temp")
lan1_rx = run_ssh("cat /sys/class/net/lan1/statistics/rx_bytes")
lan1_tx = run_ssh("cat /sys/class/net/lan1/statistics/tx_bytes")
wg0_rx = run_ssh("cat /sys/class/net/wg0/statistics/rx_bytes")
wg0_tx = run_ssh("cat /sys/class/net/wg0/statistics/tx_bytes")

### Debugging Outputs #####################################

#print(timestamp)
#print(loadavg)
#print(memory)
#print(disk)
#print(int(temp) / 1000)
#print(lan1_rx, lan1_tx, wg0_rx, wg0_tx)

### Parse Outputs #####################################
# CPU Load: "0.00 0.00 0.00 1/148 2926"
load_parts = loadavg.split()
cpu_load_1min = float(load_parts[0])
cpu_load_5min = float(load_parts[1])
cpu_load_15min = float(load_parts[2])

# Memory: output from free -m
memory_lines = memory.splitlines()
mem_parts = memory_lines[1].split()

memory_total_mb = int(mem_parts[1])
memory_used_mb = int(mem_parts[2])
memory_free_mb = int(mem_parts[3])
memory_available_mb = int(mem_parts[6])
memory_used_percent = round((memory_used_mb / memory_total_mb) * 100, 2)

# Temperature: Convert millidegrees to degrees Celsius
cpu_temp_c = int(temp) / 1000

# Disk: output from df -h / 
disk_lines = disk.splitlines()
disk_parts = disk_lines[1].split()

disk_size = disk_parts[1]
disk_used = disk_parts[2]
disk_available = disk_parts[3]
disk_used_percent = int(disk_parts[4].replace('%', ''))

# Network Counters: in bytes
lan1_rx_bytes = int(lan1_rx)
lan1_tx_bytes = int(lan1_tx)
wg0_rx_bytes = int(wg0_rx)
wg0_tx_bytes = int(wg0_tx)

# Create one Row of Metrics Data
row = [
    timestamp,
    cpu_load_1min,
    cpu_load_5min,
    cpu_load_15min,
    memory_total_mb,
    memory_used_mb,
    memory_free_mb,
    memory_available_mb,
    memory_used_percent,
    cpu_temp_c,
    disk_size,
    disk_used,
    disk_available,
    disk_used_percent,
    lan1_rx_bytes,
    lan1_tx_bytes,
    wg0_rx_bytes,
    wg0_tx_bytes
]

# Create header row for CSV file
header = [
    "timestamp",
    "cpu_load_1min",
    "cpu_load_5min",
    "cpu_load_15min",
    "memory_total_mb",
    "memory_used_mb",
    "memory_free_mb",
    "memory_available_mb",
    "memory_used_percent",
    "cpu_temp_c",
    "disk_size",
    "disk_used",
    "disk_available",
    "disk_used_percent",
    "lan1_rx_bytes",
    "lan1_tx_bytes",
    "wg0_rx_bytes",
    "wg0_tx_bytes"
]


### Write metrics to CSV file #########################
with open(CSV_PATH, "w", newline="") as csvfile:
    # Create a CSV writer object
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(header)
    # Write data row
    for sample_number in range(SAMPLES):
        # collect commands
        # parse outputs
        # create row
        writer.writerow(row)
        print(f"Collected sample {sample_number + 1}/{SAMPLES}")
        time.sleep(SAMPLE_INTERVAL)