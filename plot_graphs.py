import matplotlib.pyplot as plt
import numpy as np
from performance import get_past_system_metrics

def plot_side_by_side_bar_charts():
    # Get historical data
    past_data, time_unit = get_past_system_metrics()
    
    # Extract time values
    time_values = np.array([float(t.split()[0]) for t in past_data["Time (Unit)"]])
    total_period = time_values[-1]
    
    # Select 5 time points
    selected_times = np.linspace(total_period / 5, total_period, 5)
    selected_indices = [np.abs(time_values - t).argmin() for t in selected_times]
    selected_time_labels = [f'{time_values[i]:.1f}' for i in selected_indices]
    
    # Extract CPU and Memory values
    cpu_values = past_data["CPU Usage"].iloc[selected_indices]
    mem_values = past_data["Memory Usage"].iloc[selected_indices]
    
    # ---------------- Side-by-Side Subplots ---------------- #
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))  # 1 row, 2 columns

    # CPU Plot
    cpu_bars = axes[0].bar(selected_time_labels, cpu_values, color='#1f77b4', alpha=0.8)
    axes[0].set_title(f'CPU Usage Over Time\n({total_period:.1f} {time_unit[:3]})')
    axes[0].set_xlabel(f'Time ({time_unit[:3]})')
    axes[0].set_ylabel('CPU Usage (%)')
    axes[0].set_ylim(0, 105)
    axes[0].grid(axis='y', linestyle=':', alpha=0.5)
    
    for bar in cpu_bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.1f}%', ha='center', fontsize=9)

    # Memory Plot
    mem_bars = axes[1].bar(selected_time_labels, mem_values, color='#ff7f0e', alpha=0.8)
    axes[1].set_title(f'Memory Usage Over Time\n({total_period:.1f} {time_unit[:3]})')
    axes[1].set_xlabel(f'Time ({time_unit[:3]})')
    axes[1].set_ylabel('Memory Usage (%)')
    axes[1].set_ylim(0, 105)
    axes[1].grid(axis='y', linestyle=':', alpha=0.5)
    
    for bar in mem_bars:
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.1f}%', ha='center', fontsize=9)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_side_by_side_bar_charts()
