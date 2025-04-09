# memory_visualizer.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Placeholder for main app
root = tk.Tk()
root.title("Memory Management Visualizer")
root.geometry("800x600")
root.mainloop()
# memory_visualizer.py (updated)
class MemorySimulator:
    def __init__(self, total_memory, page_size):
        self.total_memory = total_memory  # in KB
        self.page_size = page_size  # in KB
        self.num_pages = total_memory // page_size
        self.memory = [None] * self.num_pages  # None = free, 'Pn' = process ID
        self.page_faults = 0
        self.fifo_queue = []  # For FIFO
        self.lru_tracker = {}  # For LRU: {page: last_used_time}

    def allocate_process(self, process_id, process_size, algorithm, time_step):
        pages_needed = (process_size + self.page_size - 1) // self.page_size
        free_pages = self.memory.count(None)

        if free_pages >= pages_needed:
            # Allocate directly if enough free pages
            for i in range(self.num_pages):
                if self.memory[i] is None and pages_needed > 0:
                    self.memory[i] = process_id
                    self.fifo_queue.append(i)
                    self.lru_tracker[i] = time_step
                    pages_needed -= 1
        else:
            # Page replacement needed
            self.page_faults += pages_needed
            for _ in range(pages_needed):
                if algorithm == "FIFO":
                    old_page = self.fifo_queue.pop(0)
                    self.memory[old_page] = None
                elif algorithm == "LRU":
                    oldest = min(self.lru_tracker, key=self.lru_tracker.get)
                    del self.lru_tracker[oldest]
                    self.memory[oldest] = None

                # Allocate new page
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        break

    def get_state(self):
        return self.memory.copy(), self.page_faults

# Test MMS
if __name__ == "__main__":
    sim = MemorySimulator(32, 4)  # 32 KB, 4 KB pages = 8 pages
    sim.allocate_process("P1", 10, "FIFO", 1)  # Needs 3 pages
    sim.allocate_process("P2", 12, "FIFO", 2)  # Needs 3 pages
    state, faults = sim.get_state()
    print(f"Memory: {state}, Page Faults: {faults}")

# memory_visualizer.py (updated)
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
        self.algo_var = tk.StringVar(value="FIFO")
        algo_menu = ttk.OptionMenu(input_frame, self.algo_var, "FIFO", "FIFO", "LRU")
        algo_menu.grid(row=3, column=1)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=4, column=0, columnspan=2)
        ttk.Button(input_frame, text="Simulate", command=self.run_simulation).grid(row=5, column=0, columnspan=2)

        # Output Frame (placeholder)
        self.output_label = ttk.Label(root, text="Simulation Results Here")
        self.output_label.grid(row=1, column=0, pady=10)

    def add_process(self):
        if not self.sim:
            self.sim = MemorySimulator(int(self.mem_entry.get()), int(self.page_entry.get()))
        proc_size = int(self.proc_entry.get())
        algorithm = self.algo_var.get()
        self.sim.allocate_process(f"P{len(self.sim.fifo_queue) + 1}", proc_size, algorithm, len(self.sim.fifo_queue))
        self.output_label.config(text="Process Added")

    def run_simulation(self):
        if self.sim:
            state, faults = self.sim.get_state()
            self.output_label.config(text=f"Page Faults: {faults}")
            self.plot_memory(state)
    def plot_memory(self, memory_state):
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.set_title("Memory Map")
        ax.set_xlabel("Page Number")
        ax.set_yticks([])

        colors = ['gray' if p is None else 'green' for p in memory_state]
        ax.bar(range(len(memory_state)), [1] * len(memory_state), color=colors, edgecolor='black')
        ax.set_xticks(range(len(memory_state)))

        # Embed in Tkinter
        for widget in self.root.grid_slaves(row=2, column=0):
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, pady=10)
        plt.close(fig)

root = tk.Tk()
app = MemoryVisualizerApp(root)
root.mainloop()