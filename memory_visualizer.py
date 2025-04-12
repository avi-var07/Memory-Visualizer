import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import threading

# Tkinter-based Memory Simulator Class
class MemorySimulator:
    def __init__(self, total_memory, page_size):
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

    def allocate_process(self, process_id, process_size, algorithm, time_step):
        if not (0 < process_size <= self.total_memory):
            raise ValueError("Invalid process size")
        pages_needed = (process_size + self.page_size - 1) // self.page_size
        free_pages = self.memory.count(None)

        if free_pages >= pages_needed:
            for _ in range(pages_needed):
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        break
        else:
            self.page_faults += pages_needed - free_pages
            for _ in range(pages_needed - free_pages):
                if algorithm == "FIFO" and self.fifo_queue:
                    old_page = self.fifo_queue.pop(0)
                    self.memory[old_page] = None
                elif algorithm == "LRU" and self.lru_tracker:
                    oldest = min(self.lru_tracker, key=self.lru_tracker.get)
                    del self.lru_tracker[oldest]
                    self.memory[oldest] = None
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        break

    def get_state(self):
        return self.memory.copy(), self.page_faults

    def plot_memory(self, root):
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.set_title("Memory Map")
        ax.set_xlabel("Page Number")
        ax.set_yticks([])
        colors = ['gray' if p is None else 'green' for p in self.memory]
        ax.bar(range(len(self.memory)), [1] * len(self.memory), color=colors, edgecolor='black')
        ax.set_xticks(range(len(self.memory)))
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        plt.close(fig)

# Tkinter GUI Class
class TkinterGUI:
    def __init__(self, root):
        self.root = root
        self.sim = None
        self.root.title("Memory Simulator")

        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(input_frame, text="Total Memory (KB):").grid(row=0, column=0)
        self.mem_entry = ttk.Entry(input_frame)
        self.mem_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Page Size (KB):").grid(row=1, column=0)
        self.page_entry = ttk.Entry(input_frame)
        self.page_entry.grid(row=1, column=1)

        ttk.Label(input_frame, text="Process Size (KB):").grid(row=2, column=0)
        self.proc_entry = ttk.Entry(input_frame)
        self.proc_entry.grid(row=2, column=1)

        ttk.Label(input_frame, text="Algorithm:").grid(row=3, column=0)
        self.algo_var = tk.StringVar(value="LRU")
        algo_menu = ttk.OptionMenu(input_frame, self.algo_var, "LRU", "FIFO", "LRU")
        algo_menu.grid(row=3, column=1)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=4, column=0, columnspan=2)
        ttk.Button(input_frame, text="Simulate", command=self.run_simulation).grid(row=5, column=0, columnspan=2)
        ttk.Button(input_frame, text="Help", command=self.show_help).grid(row=6, column=0, columnspan=2)

        self.output_label = ttk.Label(root, text="Page Faults: 0", font=("Arial", 12))
        self.output_label.grid(row=1, column=0, pady=10)

    def add_process(self):
        try:
            if not self.sim:
                self.sim = MemorySimulator(self.mem_entry.get(), self.page_entry.get())
            proc_size = int(self.proc_entry.get())
            algorithm = self.algo_var.get()
            self.sim.allocate_process(f"P{len(self.sim.fifo_queue) + 1}", proc_size, algorithm, len(self.sim.fifo_queue))
            self.output_label.config(text="Process Added Successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def run_simulation(self):
        if self.sim:
            state, faults = self.sim.get_state()
            self.output_label.config(text=f"Page Faults: {faults}")
            self.sim.plot_memory(self.root)

    def show_help(self):
        messagebox.showinfo("Help", "1. Enter total memory and page size.\n2. Add processes with sizes.\n3. Choose FIFO or LRU.\n4. Simulate to see memory state and faults.")

# Streamlit Integration
def run_streamlit():
    st.title("🔹 Dynamic Memory Management Visualizer")

    st.write("Simulate and visualize memory management techniques (Paging, Segmentation, Virtual Memory).")

    technique = st.selectbox("Select Memory Management Technique", ["Paging", "Segmentation", "Virtual Memory"])
    total_memory = st.number_input("Total Memory Size (KB)", min_value=100, value=1024, step=100)
    if technique == "Paging":
        page_size = st.number_input("Page Size (KB)", min_value=1, value=3, step=1)
        replacement_algo = st.selectbox("Replacement Algorithm", ["FIFO", "LRU"])

    num_processes = st.number_input("Number of Processes", min_value=1, max_value=10, value=10, step=1)
    processes = {}
    for i in range(num_processes):
        pid = st.text_input(f"Process {i+1} ID", f"P{i+1}")
        size = st.number_input(f"Memory Size for {pid} (KB)", min_value=1, value=2 if i < 5 else 3 if i < 7 else 4 if i < 8 else 5, step=1)
        processes[pid] = size

    if st.button("Simulate Memory Management"):
        if technique == "Paging":
            sim = MemorySimulator(total_memory, page_size)
            time_step = 0
            for pid, size in processes.items():
                sim.allocate_process(pid, size, replacement_algo, time_step)
                time_step += 1
            memory, page_faults = sim.get_state()
            st.subheader("📊 Memory State")
            st.write(pd.DataFrame({"Frame": range(len(memory)), "Process": memory}))
            st.subheader("📋 Page Table")
            max_pages = max((len([i for i, x in enumerate(memory) if x == pid]) for pid in processes), default=0)
            df_data = {pid: [i for i, x in enumerate(memory) if x == pid] + [None] * (max_pages - len([i for i, x in enumerate(memory) if x == pid])) for pid in processes}
            st.write(pd.DataFrame(df_data))
            st.write(f"**🔹 Number of Page Faults:** {page_faults}")
            open_canvas_panel(memory, page_faults)

def open_canvas_panel(memory, page_faults):
    st.sidebar.button("Open Canvas Panel", key="canvas_open")
    if st.session_state.get("canvas_open", False):
        st.sidebar.subheader("Canvas Panel")
        st.subheader("Memory Allocation Chart")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_title("Memory Map")
        ax.set_xlabel("Page Number")
        ax.set_yticks([])
        colors = ['gray' if p is None else 'green' for p in memory]
        ax.bar(range(len(memory)), [1] * len(memory), color=colors, edgecolor='black')
        ax.set_xticks(range(len(memory)))
        st.pyplot(fig)
        st.subheader("Execute Simple Code")
        code = st.text_area("Enter Python Code", value=f"print('Total Page Faults: {page_faults}')\nprint('Memory State: {memory}')")
        if st.button("Run Code"):
            try:
                exec(code, {"page_faults": page_faults, "memory": memory})
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--tk":
        root = tk.Tk()
        app = TkinterGUI(root)
        root.mainloop()
    else:
        if "canvas_open" not in st.session_state:
            st.session_state.canvas_open = False
        run_streamlit()