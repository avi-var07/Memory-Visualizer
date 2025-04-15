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
        self.page_accesses = []

    def allocate_process(self, process_id, process_size, algorithm, time_step):
        if not (0 < process_size <= self.total_memory):
            raise ValueError("Invalid process size")
        pages_needed = (process_size + self.page_size - 1) // self.page_size
        free_pages = self.memory.count(None)
        allocated_pages = []

        if free_pages >= pages_needed:
            for _ in range(pages_needed):
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        allocated_pages.append(i)
                        break
        else:
            self.page_faults += pages_needed - free_pages
            for _ in range(pages_needed - free_pages):
                if algorithm == "FIFO" and self.fifo_queue:
                    old_page = self.fifo_queue.pop(0)
                    self.memory[old_page] = None
                    if old_page in self.lru_tracker:
                        del self.lru_tracker[old_page]
                elif algorithm == "LRU" and self.lru_tracker:
                    oldest = min(self.lru_tracker, key=self.lru_tracker.get)
                    del self.lru_tracker[oldest]
                    self.memory[oldest] = None
                    if oldest in self.fifo_queue:
                        self.fifo_queue.remove(oldest)
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        self.memory[i] = process_id
                        self.fifo_queue.append(i)
                        self.lru_tracker[i] = time_step
                        allocated_pages.append(i)
                        break
        return allocated_pages

    def deallocate_process(self, process_id):
        allocated_pages = []
        for i in range(self.num_pages):
            if self.memory[i] == process_id:
                self.memory[i] = None
                allocated_pages.append(i)
                if i in self.fifo_queue:
                    self.fifo_queue.remove(i)
                if i in self.lru_tracker:
                    del self.lru_tracker[i]
        return allocated_pages

    def simulate_page_access(self, page_sequence, algorithm, time_step):
        faults = 0
        for page in page_sequence:
            found = False
            for i in range(self.num_pages):
                if self.memory[i] is not None and i == page:
                    found = True
                    self.lru_tracker[i] = time_step
                    time_step += 1
                    break
            if not found:
                faults += 1
                free_index = None
                for i in range(self.num_pages):
                    if self.memory[i] is None:
                        free_index = i
                        break
                if free_index is None:
                    if algorithm == "FIFO" and self.fifo_queue:
                        old_page = self.fifo_queue.pop(0)
                        self.memory[old_page] = None
                        if old_page in self.lru_tracker:
                            del self.lru_tracker[old_page]
                        free_index = old_page
                    elif algorithm == "LRU" and self.lru_tracker:
                        oldest = min(self.lru_tracker, key=self.lru_tracker.get)
                        del self.lru_tracker[oldest]
                        self.memory[oldest] = None
                        if oldest in self.fifo_queue:
                            self.fifo_queue.remove(oldest)
                        free_index = oldest
                if free_index is not None:
                    self.memory[free_index] = "Simulated"
                    self.fifo_queue.append(free_index)
                    self.lru_tracker[free_index] = time_step
                    time_step += 1
        self.page_faults += faults
        return faults

    def get_state(self):
        return self.memory.copy(), self.page_faults

    def get_page_table(self):
        page_table = {}
        for i, pid in enumerate(self.memory):
            if pid is not None:
                if pid not in page_table:
                    page_table[pid] = []
                page_table[pid].append(i)
        return page_table

    def plot_memory(self, root=None):
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.set_title("Memory Map")
        ax.set_xlabel("Page Number")
        ax.set_yticks([])
        colors = ['gray' if p is None else 'green' for p in self.memory]
        ax.bar(range(len(self.memory)), [1] * len(self.memory), color=colors, edgecolor='black')
        ax.set_xticks(range(len(self.memory)))
        if root:
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.draw()
            canvas.get_tk_widget().pack()
        plt.close(fig)
        return fig

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

        ttk.Label(input_frame, text="Process to Remove:").grid(row=4, column=0)
        self.process_list = ttk.Combobox(input_frame)
        self.process_list.grid(row=4, column=1)

        ttk.Label(input_frame, text="Page Access Sequence:").grid(row=5, column=0)
        self.page_access_entry = ttk.Entry(input_frame)
        self.page_access_entry.grid(row=5, column=1)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=6, column=0, columnspan=2)
        ttk.Button(input_frame, text="Remove Process", command=self.remove_process).grid(row=7, column=0, columnspan=2)
        ttk.Button(input_frame, text="Simulate Access", command=self.simulate_access).grid(row=8, column=0, columnspan=2)
        ttk.Button(input_frame, text="Show Memory", command=self.run_simulation).grid(row=9, column=0, columnspan=2)
        ttk.Button(input_frame, text="Help", command=self.show_help).grid(row=10, column=0, columnspan=2)

        self.output_label = ttk.Label(root, text="Page Faults: 0", font=("Arial", 12))
        self.output_label.grid(row=1, column=0, pady=10)

    def add_process(self):
        try:
            if not self.sim:
                self.sim = MemorySimulator(self.mem_entry.get(), self.page_entry.get())
            proc_size = int(self.proc_entry.get())
            algorithm = self.algo_var.get()
            pid = f"P{len(self.sim.fifo_queue) + 1}"
            self.sim.allocate_process(pid, proc_size, algorithm, len(self.sim.fifo_queue))
            current_processes = set(self.process_list['values'])
            current_processes.add(pid)
            self.process_list['values'] = tuple(current_processes)
            self.output_label.config(text="Process Added Successfully")
            self.run_simulation()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def remove_process(self):
        try:
            pid = self.process_list.get()
            if pid:
                self.sim.deallocate_process(pid)
                current_processes = set(self.process_list['values'])
                current_processes.discard(pid)
                self.process_list['values'] = tuple(current_processes)
                self.output_label.config(text="Process Removed Successfully")
                self.run_simulation()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def simulate_access(self):
        try:
            if not self.sim:
                messagebox.showerror("Error", "Initialize memory first by adding a process")
                return
            sequence = self.page_access_entry.get()
            if not sequence:
                messagebox.showerror("Error", "Enter a page access sequence")
                return
            pages = [int(x.strip()) for x in sequence.split(',') if x.strip()]
            algorithm = self.algo_var.get()
            faults = self.sim.simulate_page_access(pages, algorithm, len(self.sim.fifo_queue))
            self.output_label.config(text=f"Simulated Access - New Faults: {faults}")
            self.run_simulation()
        except ValueError:
            messagebox.showerror("Error", "Invalid page sequence (use comma-separated numbers)")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def run_simulation(self):
        if self.sim:
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Canvas) or (hasattr(widget, 'winfo_class') and widget.winfo_class() == 'Canvas'):
                    widget.destroy()
            state, faults = self.sim.get_state()
            self.output_label.config(text=f"Page Faults: {faults}")
            self.sim.plot_memory(self.root)

    def show_help(self):
        messagebox.showinfo("Help", "1. Enter total memory and page size.\n2. Add processes with sizes.\n3. Choose FIFO or LRU.\n4. Remove processes if needed.\n5. Enter page access sequence (e.g., 0,1,2).\n6. Show memory to see state and faults.")

# Streamlit Integration
def run_streamlit():
    st.title("🔹 Dynamic Memory Management Visualizer")

    st.write("Simulate and visualize memory management using Paging.")

    total_memory = st.number_input("Total Memory Size (KB)", min_value=100, value=1024, step=100)
    page_size = st.number_input("Page Size (KB)", min_value=1, value=4, step=1)
    replacement_algo = st.selectbox("Replacement Algorithm", ["FIFO", "LRU"])

    num_processes = st.number_input("Number of Processes", min_value=0, max_value=10, value=0, step=1)
    processes = {}
    for i in range(num_processes):
        pid = st.text_input(f"Process {i+1} ID", f"P{i+1}", key=f"pid_{i}")
        size = st.number_input(f"Memory Size for {pid} (KB)", min_value=1, value=4, step=1, key=f"size_{i}")
        processes[pid] = size

    page_sequence = st.text_input("Page Access Sequence (comma-separated, e.g., 0,1,2)", "")

    if st.button("Simulate Memory Management"):
        try:
            sim = MemorySimulator(total_memory, page_size)
            time_step = 0
            page_tables = {}
            for pid, size in processes.items():
                allocated_pages = sim.allocate_process(pid, size, replacement_algo, time_step)
                page_tables[pid] = allocated_pages
                time_step += 1
            memory, page_faults = sim.get_state()

            st.subheader("📊 Memory State")
            st.write(pd.DataFrame({"Frame": range(len(memory)), "Process": memory}))

            st.subheader("📋 Page Table")
            df_data = {pid: pages + [None] * (max(len(pages) for pages in page_tables.values()) - len(pages)) 
                      for pid, pages in page_tables.items()}
            st.write(pd.DataFrame(df_data))

            st.subheader("📈 Memory Allocation Chart")
            fig = sim.plot_memory()
            st.pyplot(fig)

            st.write(f"**🔹 Total Page Faults:** {page_faults}")

            if page_sequence:
                pages = [int(x.strip()) for x in page_sequence.split(',') if x.strip()]
                faults = sim.simulate_page_access(pages, replacement_algo, time_step)
                st.write(f"**🔹 Page Access Faults:** {faults}")
                st.write(f"**🔹 Updated Total Page Faults:** {sim.get_state()[1]}")

            open_canvas_panel(sim, page_faults)
        except ValueError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

def open_canvas_panel(sim, page_faults):
    st.sidebar.button("Open Canvas Panel", key="canvas_open")
    if st.session_state.get("canvas_open", False):
        st.sidebar.subheader("Canvas Panel")
        st.subheader("Memory Allocation Chart")
        fig = sim.plot_memory()
        st.pyplot(fig)
        st.subheader("Execute Simple Code")
        memory, updated_faults = sim.get_state()
        code = st.text_area("Enter Python Code", value=f"print('Total Page Faults: {updated_faults}')\nprint('Memory State: {memory}')")
        if st.button("Run Code"):
            try:
                exec(code, {"page_faults": updated_faults, "memory": memory})
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