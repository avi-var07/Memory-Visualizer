import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to simulate Paging with FIFO/LRU replacement
def simulate_paging(processes, page_size, total_memory, replacement_algo):
    num_pages = total_memory // page_size
    memory = [None] * num_pages
    page_table = {pid: [] for pid in processes.keys()}
    page_faults = 0
    timeline = []
    current_time = 0
    page_queue = []  # For FIFO
    page_access = {}  # For LRU (track last access time)

    for pid, size in processes.items():
        required_pages = (size + page_size - 1) // page_size
        for _ in range(required_pages):
            if None in memory:
                frame = memory.index(None)
                memory[frame] = pid
                page_table[pid].append(frame)
                timeline.append((pid, current_time, current_time + 1))
                current_time += 1
                page_queue.append(frame)
                page_access[frame] = current_time
            else:
                page_faults += 1
                if replacement_algo == "FIFO":
                    replaced_frame = page_queue.pop(0)
                else:  # LRU
                    replaced_frame = min(page_access, key=page_access.get)
                    del page_access[replaced_frame]
                old_pid = memory[replaced_frame]
                page_table[old_pid].remove(replaced_frame)
                memory[replaced_frame] = pid
                page_table[pid].append(replaced_frame)
                timeline.append((f"{pid} (replaces {old_pid})", current_time, current_time + 1))
                current_time += 1
                page_queue.append(replaced_frame)
                page_access[replaced_frame] = current_time

    # Convert page_table to a DataFrame-friendly format
    max_pages = max(len(frames) for frames in page_table.values()) if page_table else 0
    df_data = {pid: frames + [None] * (max_pages - len(frames)) for pid, frames in page_table.items()}
    return memory, df_data, page_faults, timeline

# Function to simulate Segmentation
def simulate_segmentation(processes, total_memory):
    memory = [None] * total_memory
    segment_table = {}
    current_pos = 0

    for pid, size in processes.items():
        if current_pos + size <= total_memory:
            segment_table[pid] = (current_pos, current_pos + size - 1)
            for i in range(current_pos, current_pos + size):
                memory[i] = pid
            current_pos += size
        else:
            st.warning(f"Insufficient memory for process {pid}")
            break

    return memory, segment_table

# Function to plot Memory Usage in Canvas
def plot_memory_usage(timeline):
    fig, ax = plt.subplots(figsize=(10, 4))
    for pid, start, end in timeline:
        color = 'lightblue' if "replaces" not in pid else 'lightcoral'
        ax.barh(y=0, width=end - start, left=start, color=color, edgecolor='black')
        ax.text(start + (end - start) / 2, 0, pid, va='center', ha='center', fontsize=10)
    ax.set_yticks([])
    ax.set_xticks(range(max(t[2] for t in timeline) + 1))
    ax.set_xlabel("Time")
    ax.set_title("Memory Allocation Timeline")
    return fig

# Canvas Panel for Visualization and Code Execution
def open_canvas_panel(timeline, memory, page_table, page_faults):
    st.sidebar.button("Open Canvas Panel", key="canvas_open")
    if st.session_state.get("canvas_open", False):
        st.sidebar.subheader("Canvas Panel")
        
        # Display Memory Visualization
        st.subheader("Memory Allocation Chart")
        fig = plot_memory_usage(timeline)
        st.pyplot(fig)

        # Allow Simple Code Execution
        st.subheader("Execute Simple Code")
        code = st.text_area("Enter Python Code (e.g., print memory stats)", 
                            value=f"print('Total Page Faults: {page_faults}')\n"
                                  f"print('Memory State: {memory}')\n"
                                  f"print('Page Table: {page_table}')")
        if st.button("Run Code"):
            try:
                exec(code, {"page_faults": page_faults, "memory": memory, "page_table": page_table})
            except Exception as e:
                st.error(f"Error: {e}")

# Streamlit App UI
st.title("🔹 Dynamic Memory Management Visualizer")

st.write("Simulate and visualize memory management techniques (Paging, Segmentation, Virtual Memory).")

# User Inputs
technique = st.selectbox("Select Memory Management Technique", ["Paging", "Segmentation", "Virtual Memory"])
total_memory = st.number_input("Total Memory Size (KB)", min_value=100, value=1024, step=100)
if technique == "Paging":
    page_size = st.number_input("Page Size (KB)", min_value=1, value=3, step=1)
    replacement_algo = st.selectbox("Replacement Algorithm", ["FIFO", "LRU"])

# Process Inputs
num_processes = st.number_input("Number of Processes", min_value=1, max_value=10, value=10, step=1)
processes = {}
for i in range(num_processes):
    pid = st.text_input(f"Process {i+1} ID", f"P{i+1}")
    size = st.number_input(f"Memory Size for {pid} (KB)", min_value=1, value=2 if i < 5 else 3 if i < 7 else 4 if i < 8 else 5, step=1)
    processes[pid] = size

# Simulation Button
if st.button("Simulate Memory Management"):
    if technique == "Paging":
        memory, page_table, page_faults, timeline = simulate_paging(processes, page_size, total_memory, replacement_algo)
        st.subheader("📊 Memory State")
        st.write(pd.DataFrame({"Frame": range(len(memory)), "Process": memory}))
        st.subheader("📋 Page Table")
        st.write(pd.DataFrame(page_table))  # Now works with padded data
        st.write(f"**🔹 Number of Page Faults:** {page_faults}")
        open_canvas_panel(timeline, memory, page_table, page_faults)
    elif technique == "Segmentation":
        memory, segment_table = simulate_segmentation(processes, total_memory)
        st.subheader("📊 Memory State")
        st.write(pd.DataFrame({"Address": range(len(memory)), "Process": memory}))
        st.subheader("📋 Segment Table")
        st.write(pd.DataFrame(segment_table.items(), columns=["Process", "Segment"]))
    else:  # Virtual Memory (simplified as paging with demand paging)
        memory, page_table, page_faults, timeline = simulate_paging(processes, page_size, total_memory, replacement_algo)
        st.subheader("📊 Memory State")
        st.write(pd.DataFrame({"Frame": range(len(memory)), "Process": memory}))
        st.subheader("📋 Page Table")
        st.write(pd.DataFrame(page_table))
        st.write(f"**🔹 Number of Page Faults:** {page_faults}")
        open_canvas_panel(timeline, memory, page_table, page_faults)

# Initialize session state for canvas
if "canvas_open" not in st.session_state:
    st.session_state.canvas_open = False