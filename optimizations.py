import psutil

def suggest_optimizations():
    optimizations = []

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    if cpu_percent > 80:
        optimizations.append("🔴 High CPU usage detected. Consider closing background apps or upgrading your CPU.")
    elif cpu_percent > 50:
        optimizations.append("🟠 Moderate CPU usage. Monitor active tasks.")

    if memory.percent > 80:
        optimizations.append("🔴 High RAM usage. Close unused programs or upgrade RAM.")
    elif memory.percent > 50:
        optimizations.append("🟠 Moderate memory usage. Optimize memory-intensive tasks.")

    if disk.percent > 85:
        optimizations.append("🔴 Disk space almost full. Clean up files or extend storage.")
    elif disk.percent > 70:
        optimizations.append("🟠 Disk space usage high. Consider cleaning temporary files.")

    if not optimizations:
        optimizations.append("✅ System performance is optimal. No action needed.")

    return optimizations
