import os
import random
import pandas as pd
from collections import Counter

# CSV file name
CSV_FILE = "test_data.csv"

# Delete existing CSV file if it exists
try:
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        print(f"Deleted existing {CSV_FILE}")
except PermissionError:
    print(f"Warning: Could not delete {CSV_FILE} due to permissions")

def get_time_interval():
    """Generate time intervals with 90% between 10-60 mins and 10% between 61-180 mins."""
    if random.random() < 0.9:  # 90% chance
        return random.randint(10, 60)  # 10-60 minutes
    else:  # 10% chance
        return random.randint(61, 180)  # 61-180 minutes (1-3 hours)

def generate_random_usage_data(max_intervals=50, cpu_base_range=(15, 30), mem_base_range=(20, 40)):
    """Generate random, logical CPU and memory usage data with consistent time intervals per runtime."""
    num_intervals = random.randint(25, max_intervals)  # Minimum 25 observations
    time_step = get_time_interval()  # Consistent interval for this run
    
    # Base values for realistic starting points
    base_cpu = random.uniform(*cpu_base_range)  # Default: 15-30%
    base_memory = random.uniform(*mem_base_range)  # Default: 20-40%
    
    time_units = []
    cpu_usage = []
    memory_usage = []
    current_time = 0
    
    print(f"Using consistent time interval of {time_step} minutes for this run")
    
    for i in range(num_intervals):
        current_time += time_step
        time_units.append(f"{current_time} Min")
        
        # CPU usage: smaller trend for realism
        cpu_trend = base_cpu + (i * random.uniform(0, 0.3))  # Max 0.3% increase per step
        cpu_fluctuation = random.uniform(-3, 3)  # Smaller fluctuation
        current_cpu = max(10, min(60, round(cpu_trend + cpu_fluctuation, 1)))  # Cap at 60%
        cpu_usage.append(current_cpu)
        
        # Memory usage: smaller trend
        memory_trend = base_memory + (i * random.uniform(0, 0.2))  # Max 0.2% increase per step
        memory_fluctuation = random.uniform(-2, 2)  # Smaller fluctuation
        current_memory = max(15, min(65, round(memory_trend + memory_fluctuation, 1)))  # Cap at 65%
        memory_usage.append(current_memory)
    
    data = {
        "Time (Unit)": time_units,
        "CPU Usage": cpu_usage,
        "Memory Usage": memory_usage
    }
    return pd.DataFrame(data)

def save_to_csv(df, filename=CSV_FILE):
    """Save the generated data to a CSV file."""
    try:
        df.to_csv(filename, index=False)
        print(f"Generated test data saved to {filename} with {len(df)} intervals")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

if __name__ == "__main__":
    # Test interval distribution (optional)
    # intervals = [get_time_interval() for _ in range(1000)]
    # print("Interval distribution:", sorted(Counter(intervals).items()))
    
    test_data = generate_random_usage_data(max_intervals=50)
    save_to_csv(test_data)