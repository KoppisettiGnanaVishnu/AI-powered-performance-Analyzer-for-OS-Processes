import psutil
import numpy as np
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

# Constants
PAST_INTERVALS = 25

def get_real_time_metrics():
    """Get current CPU and memory usage metrics."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    data = {
        "Metric": ["CPU Usage (%)", "Memory Usage (%)"],
        "Value": [cpu_usage, memory_usage]
    }
    return pd.DataFrame(data)

def detect_performance_issues():
    """Detect performance issues based on current metrics."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    results = []
    if cpu_usage > 80:
        results.append(f"⚠️ High CPU Usage: {cpu_usage}%")
    if memory > 80:
        results.append(f"⚠️ High Memory Usage: {memory}%")
    if not results:
        results.append("✅ No significant performance issues detected")
    return results

def get_system_uptime():
    """Return system uptime in seconds."""
    return time.time() - psutil.boot_time()

def format_time_values(time_values):
    """Convert time values to appropriate units."""
    time_unit = "Seconds"
    if max(time_values) >= 60:
        time_values = time_values / 60
        time_unit = "Minutes"
    if max(time_values) >= 60:
        time_values = time_values / 60
        time_unit = "Hours"
    return time_values, time_unit

def get_past_system_metrics():
    """Collect past system metrics over PAST_INTERVALS."""
    uptime = get_system_uptime()
    time_points = np.linspace(0, uptime, num=PAST_INTERVALS)
    time_points, time_unit = format_time_values(time_points)

    history = []
    for idx, t in enumerate(time_points, start=1):
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory_usage = psutil.virtual_memory().percent
        time_with_unit = f"{round(t, 2)} {time_unit[:3]}"
        history.append([idx, time_with_unit, cpu_usage, memory_usage])

    df = pd.DataFrame(history, columns=["Index", "Time (Unit)", "CPU Usage", "Memory Usage"])
    df.set_index("Index", inplace=True)
    return df, time_unit

def load_user_data_from_csv(csv_path):
    """Load user-provided CPU and memory data from a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        required_columns = ["Time (Unit)", "CPU Usage", "Memory Usage"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV must contain 'Time (Unit)', 'CPU Usage', 'Memory Usage' columns")
        df["Index"] = range(1, len(df) + 1)
        df.set_index("Index", inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV: {str(e)}")

def generate_future_time_series(total_period_min, interval_min):
    """Generate future time points for prediction."""
    intervals = int(total_period_min / interval_min)
    return [f"{i * interval_min} Min" for i in range(1, intervals + 1)]

def predict_future_trends(past_data, total_period_hours=1, interval_min=5):
    """Predict future CPU and memory usage using linear regression."""
    total_period_min = total_period_hours * 60
    X = np.array(range(1, len(past_data) + 1)).reshape(-1, 1)
    y_cpu = np.array(past_data["CPU Usage"]).reshape(-1, 1)
    y_mem = np.array(past_data["Memory Usage"]).reshape(-1, 1)

    model_cpu = LinearRegression().fit(X, y_cpu)
    model_mem = LinearRegression().fit(X, y_mem)

    future_intervals = int(total_period_min / interval_min)
    future_indices = np.array(range(1, future_intervals + 1)).reshape(-1, 1)
    
    future_cpu = model_cpu.predict(future_indices).flatten()
    future_mem = model_mem.predict(future_indices).flatten()

    cpu_variation = np.std(y_cpu) * np.random.uniform(-0.5, 0.5, size=len(future_cpu))
    mem_variation = np.std(y_mem) * np.random.uniform(-0.3, 0.3, size=len(future_mem))

    future_cpu = np.clip(future_cpu + cpu_variation, 0, 100)
    future_mem = np.clip(future_mem + mem_variation, 0, 100)

    future_times = generate_future_time_series(total_period_min, interval_min)

    future_data = pd.DataFrame({
        "Index": range(1, future_intervals + 1),
        "Time (Unit)": future_times,
        "Predicted CPU Usage": np.round(future_cpu, 2),
        "Predicted Memory Usage": np.round(future_mem, 2),
    }).set_index("Index")

    return future_data

def get_metrics_and_predictions(data_source="real-time", csv_path=None, total_period_hours=1, interval_min=5):
    """Unified function to get metrics and predictions based on data source."""
    if data_source == "real-time":
        past_data, _ = get_past_system_metrics()
    elif data_source == "csv" and csv_path:
        past_data = load_user_data_from_csv(csv_path)
    else:
        raise ValueError("Invalid data source or missing CSV path")
    
    current_metrics = get_real_time_metrics() if data_source == "real-time" else past_data.tail(1)
    performance_issues = detect_performance_issues() if data_source == "real-time" else ["N/A for CSV data"]
    predictions = predict_future_trends(past_data, total_period_hours, interval_min)
    
    return current_metrics, performance_issues, predictions

# Example usage
if __name__ == "__main__":
    metrics, issues, predictions = get_metrics_and_predictions("real-time")
    print("Real-Time Metrics:\n", metrics)
    print("\nPerformance Issues:\n", issues)
    print("\nPredictions:\n", predictions)