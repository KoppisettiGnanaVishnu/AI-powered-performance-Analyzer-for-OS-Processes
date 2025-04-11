import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import time
import pandas as pd
from typing import Optional, Tuple

# Import modules
from performance import get_past_system_metrics, predict_future_trends, load_user_data_from_csv
from bottlenecks import get_real_time_metrics, detect_bottlenecks
from optimizations import suggest_optimizations
from generate_test_data import generate_random_usage_data, save_to_csv

class ConsoleOutput:
    """Class to capture console output and display in GUI"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.original_stdout.write(message)
        
    def flush(self):
        pass

class SystemMonitorApp:
    """Main application class for the System Performance Monitor"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("System Performance Monitor")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.test_csv_path = "test_data.csv"
        self.default_period = 1  # hours
        self.default_interval = 6  # minutes
        
        self.setup_ui()
        self.ensure_test_data_exists()
        
        self.dark_mode = False
        self.setup_theme()
        
        self.console_output = ConsoleOutput(self.output_text)
        sys.stdout = self.console_output
        sys.stderr = self.console_output
        
        print("System Monitor initialized. Ready to analyze performance.")
    
    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_control_panel()
        self.setup_output_panel()
        self.setup_status_bar()
    
    def setup_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Actions", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons = [
            ("📊 Performance", self.show_performance_input),
            ("⚠️ Bottlenecks", self.display_bottlenecks),
            ("🔧 Optimizations", self.display_optimizations),
            ("🧹 Clear", self.clear_output),
            ("🌙 Toggle Theme", self.toggle_theme)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(control_frame, text=text, command=command, width=15).grid(row=0, column=i, padx=5, sticky="ew")
        
        for i in range(len(buttons)):
            control_frame.columnconfigure(i, weight=1)
    
    def setup_output_panel(self):
        output_frame = ttk.LabelFrame(self.main_frame, text="Analysis Results", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, font=('Consolas', 10), height=20, padx=10, pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        self.setup_text_tags()
    
    def setup_text_tags(self):
        self.output_text.tag_config('header', foreground='blue', font=('Consolas', 11, 'bold'))
        self.output_text.tag_config('warning', foreground='orange')
        self.output_text.tag_config('error', foreground='red')
        self.output_text.tag_config('success', foreground='green')
        self.output_text.tag_config('tip', foreground='purple')
    
    def setup_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_theme(self):
        if self.dark_mode:
            self.root.tk_setPalette(
                background='#2d2d2d', foreground='#ffffff',
                activeBackground='#3d3d3d', activeForeground='#ffffff'
            )
            self.output_text.config(bg='#1e1e1e', fg='#ffffff', insertbackground='white')
        else:
            self.root.tk_setPalette(background='#f0f0f0')
            self.output_text.config(bg='white', fg='black', insertbackground='black')
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setup_theme()
    
    def ensure_test_data_exists(self):
        if not os.path.exists(self.test_csv_path):
            self.status_var.set("Generating test data...")
            self.root.update()
            time.sleep(0.1)
            try:
                test_data = generate_random_usage_data(max_intervals=50)
                save_to_csv(test_data, self.test_csv_path)
                self.status_var.set("Test data generated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate test data: {str(e)}")
                self.status_var.set("Error generating test data")
    
    def show_performance_input(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("Performance Analysis Settings")
        input_window.transient(self.root)
        input_window.grab_set()
        self.center_window(input_window, 350, 200)
        
        ttk.Label(input_window, text="Data Source:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.data_source_var = tk.StringVar(value="real-time")
        data_source_menu = ttk.Combobox(
            input_window, textvariable=self.data_source_var, values=["real-time", "csv"], state="readonly"
        )
        data_source_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_window, text="Total Period (hours):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.total_period_entry = ttk.Entry(input_window)
        self.total_period_entry.insert(0, str(self.default_period))
        self.total_period_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_window, text="Interval (minutes):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.interval_entry = ttk.Entry(input_window)
        self.interval_entry.insert(0, str(self.default_interval))
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        button_frame = ttk.Frame(input_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(button_frame, text="Run Analysis", command=self.run_performance_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=input_window.destroy).pack(side=tk.LEFT, padx=5)
        
        input_window.columnconfigure(1, weight=1)
    
    def run_performance_analysis(self):
        try:
            total_period = float(self.total_period_entry.get())
            interval = int(self.interval_entry.get())
            data_source = self.data_source_var.get()
            
            if total_period <= 0 or interval <= 0:
                raise ValueError("Values must be positive numbers")
            
            self.clear_output()
            self.status_var.set("Running performance analysis...")
            self.root.update()
            time.sleep(0.1)
            
            if data_source == "real-time":
                past_data, time_unit = get_past_system_metrics()
                source_info = "Real-time system data"
            else:
                past_data = load_user_data_from_csv(self.test_csv_path)
                time_unit = "User-defined intervals"
                source_info = f"CSV data from {self.test_csv_path}"
            
            future_data = predict_future_trends(past_data, total_period, interval)
            self.display_performance_results(past_data, future_data, source_info)
            self.status_var.set("Performance analysis completed")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            self.status_var.set("Error in analysis")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Analysis failed")
    
    def display_performance_results(self, past_data: pd.DataFrame, future_data: pd.DataFrame, source_info: str):
        self.output_text.insert(tk.END, "=== SYSTEM PERFORMANCE ANALYSIS ===\n", 'header')
        self.output_text.insert(tk.END, f"Data Source: {source_info}\n\n")
        self.output_text.insert(tk.END, "=== PAST METRICS ===\n", 'header')
        self.output_text.insert(tk.END, past_data.to_string() + "\n\n")
        self.output_text.insert(tk.END, "=== FUTURE PREDICTIONS ===\n", 'header')
        self.output_text.insert(tk.END, future_data.to_string() + "\n")
        self.output_text.see(tk.END)
    
    def display_bottlenecks(self):
        try:
            self.clear_output()
            self.status_var.set("Detecting bottlenecks...")
            self.root.update()
            time.sleep(0.1)
            
            metrics = get_real_time_metrics()
            bottlenecks = detect_bottlenecks()
            
            self.output_text.insert(tk.END, "=== SYSTEM BOTTLENECKS ===\n", 'header')
            self.output_text.insert(tk.END, "Current Metrics:\n")
            self.output_text.insert(tk.END, metrics.to_string(index=False) + "\n\n")
            self.output_text.insert(tk.END, "Bottleneck Analysis:\n")
            
            for line in bottlenecks:
                if "⚠️ High" in line:
                    self.output_text.insert(tk.END, line + "\n", 'error')
                elif "Moderate" in line:
                    self.output_text.insert(tk.END, line + "\n", 'warning')
                elif "✅" in line:
                    self.output_text.insert(tk.END, line + "\n", 'success')
                else:
                    self.output_text.insert(tk.END, line + "\n")
            
            self.status_var.set("Bottleneck analysis completed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect bottlenecks: {str(e)}")
            self.status_var.set("Bottleneck analysis failed")
    
    def display_optimizations(self):
        try:
            self.clear_output()
            self.status_var.set("Generating optimization suggestions...")
            self.root.update()
            time.sleep(0.1)

            suggestions = suggest_optimizations()

            self.output_text.insert(tk.END, "=== OPTIMIZATION SUGGESTIONS ===\n", 'header')
            for line in suggestions:
                if "🔴" in line:
                    self.output_text.insert(tk.END, line + "\n", 'error')
                elif "🟠" in line:
                    self.output_text.insert(tk.END, line + "\n", 'warning')
                elif "✅" in line:
                    self.output_text.insert(tk.END, line + "\n", 'success')
                else:
                    self.output_text.insert(tk.END, line + "\n")
            
            self.status_var.set("Optimization suggestions displayed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate suggestions: {str(e)}")
            self.status_var.set("Optimization suggestion failed")
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Output cleared")
    
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_close(self):
        sys.stdout = self.console_output.original_stdout
        sys.stderr = self.console_output.original_stderr
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
