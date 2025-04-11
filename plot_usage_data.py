import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Run the test data generator
subprocess.run(["python", "generate_test_data.py"], check=True)

# Step 2: Load the generated CSV
df = pd.read_csv("test_data.csv")

# Step 3: Convert "Time (Unit)" to numeric minutes
df["Time"] = df["Time (Unit)"].str.replace(" Min", "").astype(float)

# Step 4: Define 5 equal time intervals
total_time = df["Time"].iloc[-1]
target_times = np.linspace(total_time / 5, total_time, 5)

# Step 5: Interpolate values at those time points
cpu_interp = np.interp(target_times, df["Time"], df["CPU Usage"])
mem_interp = np.interp(target_times, df["Time"], df["Memory Usage"])
labels = [f"{int(t)} Min" for t in target_times]

# Step 6: Plot two side-by-side graphs
fig, axes = plt.subplots(1, 2, figsize=(10, 5))  # ⬅️ Narrower layout

# CPU Plot
axes[0].bar(labels, cpu_interp, color='skyblue')
axes[0].set_title('CPU Usage', fontsize=12)
axes[0].set_ylabel('Usage (%)')
axes[0].set_ylim(0, 100)
axes[0].grid(axis='y', linestyle='--', alpha=0.5)
for i, v in enumerate(cpu_interp):
    axes[0].text(i, v + 2, f"{v:.1f}%", ha='center', fontsize=9)

# Memory Plot
axes[1].bar(labels, mem_interp, color='salmon')
axes[1].set_title('Memory Usage', fontsize=12)
axes[1].set_ylabel('Usage (%)')
axes[1].set_ylim(0, 100)
axes[1].grid(axis='y', linestyle='--', alpha=0.5)
for i, v in enumerate(mem_interp):
    axes[1].text(i, v + 2, f"{v:.1f}%", ha='center', fontsize=9)

# Final Layout
fig.suptitle(f'System Performance Summary (Total Time: {int(total_time)} Min)', fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.show()
