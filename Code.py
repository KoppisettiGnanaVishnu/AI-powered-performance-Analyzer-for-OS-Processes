import psutil
import pandas as pd
import time
import os
from datetime import datetime

# Define threshold values
CPU_THRESHOLD = 85  
MEMORY_THRESHOLD = 90  
DISK_THRESHOLD = 90  
STARVATION_THRESHOLD = 30  # Process waiting for CPU for too long (in seconds)

# File name
file_name = "system_advanced_monitoring_log.csv"

# Delete existing log file if it exists
if os.path.exists(file_name):
    os.remove(file_name)
    print(f"Deleted existing log file: {file_name}")

# Initialize an empty list to store data
data_log = []

# Monitoring duration (in seconds) and interval
monitor_duration = 60  
interval = 2  

def collect_system_metrics():
    """Collects real-time system performance metrics."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    net_io = psutil.net_io_counters()
    
    net_sent = net_io.bytes_sent / (1024 * 1024)  
    net_recv = net_io.bytes_recv / (1024 * 1024)  

    return [timestamp, cpu_usage, memory_usage, disk_usage, net_sent, net_recv]

def detect_bottlenecks(cpu, memory, disk):
    """Checks if system metrics exceed defined thresholds."""
    alerts = []
    bottleneck_detected = "No"
    
    if cpu > CPU_THRESHOLD:
        alerts.append(f"⚠️ High CPU Usage: {cpu}%")
    if memory > MEMORY_THRESHOLD:
        alerts.append(f"⚠️ High Memory Usage: {memory}%")
    if disk > DISK_THRESHOLD:
        alerts.append(f"⚠️ High Disk Usage: {disk}%")
    
    if alerts:
        bottleneck_detected = "Yes"

    return alerts, bottleneck_detected

def detect_deadlocks():
    """Detects processes stuck in uninterruptible sleep state (D state)."""
    deadlocks = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        if proc.info['status'] == 'disk-sleep':  
            deadlocks.append(f"🔴 Deadlock Detected: Process {proc.info['name']} (PID {proc.info['pid']})")
    return deadlocks

def detect_starvation():
    """Detects processes that are waiting too long for CPU time."""
    starved_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        if proc.info['cpu_percent'] < 1:  # Very low CPU usage
            starved_processes.append(f"⚠️ Starvation Risk: Process {proc.info['name']} (PID {proc.info['pid']})")
    return starved_processes

def check_cpu_affinity():
    """Detects processes bound to a single CPU core (potential load imbalance)."""
    affinity_issues = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            affinity = proc.cpu_affinity()
            if len(affinity) == 1:  
                affinity_issues.append(f"⚠️ CPU Affinity Issue: Process {proc.info['name']} (PID {proc.info['pid']}) assigned to Core {affinity}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  
    return affinity_issues

def suggest_optimizations(bottlenecks, deadlocks, starvation, affinity_issues):
    """Suggests system optimizations based on detected issues."""
    suggestions = []
    
    if bottlenecks:
        suggestions.append("🔹 Close background apps to free up resources.")
        suggestions.append("🔹 Optimize high-CPU processes.")
    
    if deadlocks:
        suggestions.append("🔹 Restart affected processes to resolve deadlocks.")
    
    if starvation:
        suggestions.append("🔹 Adjust CPU priority for starved processes.")
    
    if affinity_issues:
        suggestions.append("🔹 Reassign processes across multiple CPU cores for better balance.")

    return suggestions if suggestions else ["✅ System running optimally. No actions needed."]

def monitor_system():
    print("Monitoring system for advanced performance issues...\n")
    
    start_time = time.time()
    
    while (time.time() - start_time) < monitor_duration:
        metrics = collect_system_metrics()
        bottleneck_alerts, bottleneck_status = detect_bottlenecks(metrics[1], metrics[2], metrics[3])
        deadlock_issues = detect_deadlocks()
        starvation_issues = detect_starvation()
        affinity_issues = check_cpu_affinity()
        optimizations = suggest_optimizations(bottleneck_alerts, deadlock_issues, starvation_issues, affinity_issues)

        # Append results to metrics
        metrics.append(bottleneck_status)
        metrics.append(" | ".join(deadlock_issues) if deadlock_issues else "None")
        metrics.append(" | ".join(starvation_issues) if starvation_issues else "None")
        metrics.append(" | ".join(affinity_issues) if affinity_issues else "None")
        metrics.append(" | ".join(optimizations))  

        data_log.append(metrics)

        # Print system status
        print(f"[{metrics[0]}] CPU: {metrics[1]}% | Memory: {metrics[2]}% | Disk: {metrics[3]}% | Bottleneck: {metrics[6]}")
        
        # Print alerts
        for alert in bottleneck_alerts + deadlock_issues + starvation_issues + affinity_issues:
            print(alert)

        # Print AI-based optimization suggestions
        print("🔧 Suggested Optimizations:")
        for suggestion in optimizations:
            print(suggestion)
        
        print("-" * 50)
        time.sleep(interval)

    # Save collected data to CSV
    df = pd.DataFrame(data_log, columns=[
        "Timestamp", "CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)", 
        "Network Sent (MB)", "Network Received (MB)", "Bottleneck Detected",
        "Deadlock Issues", "Starvation Issues", "CPU Affinity Issues", "Optimization Suggestions"
    ])
    df.to_csv(file_name, index=False)
    print(f"\nMonitoring complete. Data saved to '{file_name}'.")

if _name_ == "_main_":
    monitor_system()
