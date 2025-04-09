import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MemorySimulator:
    def __init__(self, total_memory, page_size):
        try:
            self.total_memory = int(total_memory)
            self.page_size = int(page_size)
            if self.total_memory <= 0 or self.page_size <= 0:
                raise ValueError("Memory and page size must be positive integers.")
            if self.total_memory < self.page_size:
                raise ValueError("Total memory must be greater than page size.")
            self.num_pages = self.total_memory // self.page_size
            self.memory = [None] * self.num_pages
            self.page_faults = 0
            self.fifo_queue = []
            self.lru_tracker = {}
        except ValueError as e:
            raise ValueError(f"Initialization error: {e}")

    def allocate_process(self, process_id, process_size, algorithm, time_step):
        try:
            process_size = int(process_size)
            if process_size <= 0 or process_size > self.total_memory:
                raise ValueError("Process size must be positive and not exceed total memory.")
            pages_needed = (process_size + self.page_size - 1) // self.page_size
            free_pages = self.memory.count(None)

            if free_pages >= pages_needed:
                for i in range(self.num_pages):
                    if self.memory[i] is None and pages_needed > 0:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        pages_needed -= 1
            else:
                self.page_faults += pages_needed
                for _ in range(pages_needed):
                    if not self.fifo_queue and not self.lru_tracker:
                        raise ValueError("No pages available to replace.")
                    if algorithm not in ["FIFO", "LRU"]:
                        raise ValueError("Invalid algorithm. Use 'FIFO' or 'LRU'.")
                    if algorithm == "FIFO" and self.fifo_queue:
                        old_page = self.fifo_queue.pop(0)
                        self.memory[old_page] = None
                    elif algorithm == "LRU" and self.lru_tracker:
                        oldest = min(self.lru_tracker, key=self.lru_tracker.get)
                        del self.lru_tracker[oldest]
                        self.memory[oldest] = None
                    else:
                        raise ValueError("No pages to replace with current algorithm.")
                    for i in range(self.num_pages):
                        if self.memory[i] is None:
                            self.memory[i] = process_id
                            self.fifo_queue.append(i)
                            self.lru_tracker[i] = time_step
                            break
        except ValueError as e:
            raise ValueError(f"Allocation error: {e}")

    def get_state(self):
        return self.memory.copy(), self.page_faults

class MemoryVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.sim = None

        # Input Frame
        input_frame = ttk.Frame(root, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(input_frame, text="Total Memory (KB):").grid(row=0, column=0)
        self.mem_entry = ttk.Entry(input_frame)
        self.mem_entry.grid(row=0, column=1)
        self.mem_entry.insert(0, "32")

        ttk.Label(input_frame, text="Page Size (KB):").grid(row=1, column=0)
        self.page_entry = ttk.Entry(input_frame)
        self.page_entry.grid(row=1, column=1)
        self.page_entry.insert(0, "4")

        ttk.Label(input_frame, text="Process Size (KB):").grid(row=2, column=0)
        self.proc_entry = ttk.Entry(input_frame)
        self.proc_entry.grid(row=2, column=1)

        ttk.Label(input_frame, text="Algorithm:").grid(row=3, column=0)
        self.algo_var = tk.StringVar(value="LRU")  # Updated to match screenshot
        algo_menu = ttk.OptionMenu(input_frame, self.algo_var, "LRU", "FIFO", "LRU")
        algo_menu.grid(row=3, column=1)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=4, column=0, columnspan=2)
        ttk.Button(input_frame, text="Simulate", command=self.run_simulation).grid(row=5, column=0, columnspan=2)
        ttk.Button(input_frame, text="Help", command=self.show_help).grid(row=6, column=0, columnspan=2)

        # Output Frame
        self.output_label = ttk.Label(root, text="Page Faults: 0", font=("Arial", 12))
        self.output_label.grid(row=1, column=0, pady=10)

    def add_process(self):
        try:
            if not self.sim:
                self.sim = MemorySimulator(self.mem_entry.get(), self.page_entry.get())
            proc_size = self.proc_entry.get()
            algorithm = self.algo_var.get()
            self.sim.allocate_process(f"P{len(self.sim.fifo_queue) + 1}", proc_size, algorithm, len(self.sim.fifo_queue))
            self.output_label.config(text="Process Added Successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def run_simulation(self):
        if self.sim:
            try:
                state, faults = self.sim.get_state()
                self.output_label.config(text=f"Page Faults: {faults}")
                self.plot_memory(state)
            except Exception as e:
                messagebox.showerror("Error", f"Simulation error: {e}")

    def plot_memory(self, memory_state):
        try:
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.set_title("Memory Map")
            ax.set_xlabel("Page Number")
            ax.set_yticks([])
            colors = ['gray' if p is None else 'green' for p in memory_state]
            ax.bar(range(len(memory_state)), [1] * len(memory_state), color=colors, edgecolor='black')
            ax.set_xticks(range(len(memory_state)))

            for widget in self.root.grid_slaves(row=2, column=0):
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().grid(row=2, column=0, pady=10)
            plt.close(fig)
        except Exception as e:
            messagebox.showerror("Error", f"Visualization error: {e}")

    def show_help(self):
        messagebox.showinfo("Help", "1. Enter total memory and page size.\n2. Add processes with sizes.\n3. Choose FIFO or LRU.\n4. Simulate to see memory state and faults.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Memory Management Visualizer")
    root.geometry("800x600")
    app = MemoryVisualizerApp(root)
    root.mainloop()