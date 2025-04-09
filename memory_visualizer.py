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