import streamlit as st
import pandas as pd
import plotly.express as px
from process_simulator import ProcessSimulator
from cpu_scheduler import CPUScheduler
from memory_simulator import MemorySimulator, SegmentationSimulator

def main():
    st.set_page_config(
        page_title="OS Simulator",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
        text-align: center;
    }
    .module-header {
        font-size: 28px;
        font-weight: bold;
        color: #3498db;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .feature-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">Operating System Simulator</div>', unsafe_allow_html=True)
    
    st.sidebar.header("OS Modules")
    module = st.sidebar.radio("", ["Dashboard", "Process Management", "CPU Scheduling", "Memory Management"])
    
    if 'process_sim' not in st.session_state:
        st.session_state.process_sim = ProcessSimulator()
    if 'cpu_scheduler' not in st.session_state:
        st.session_state.cpu_scheduler = CPUScheduler()
    
    if module == "Dashboard":
        display_dashboard()
    elif module == "Process Management":
        display_process_management()
    elif module == "CPU Scheduling":
        display_cpu_scheduling()
    elif module == "Memory Management":
        display_memory_management()

def display_dashboard():
    st.markdown('<div class="module-header">OS Simulator Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("👥 Process Management")
        st.write("Simulate process creation, states, and transitions.")
        st.markdown("- Process state visualization\n- PCB management\n- Process transitions")
        if st.button("Go to Process Management"):
            st.session_state.module = "Process Management"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("⏱️ CPU Scheduling")
        st.write("Simulate different CPU scheduling algorithms.")
        st.markdown("- FCFS, SJF, Round Robin\n- Priority Scheduling\n- Gantt chart visualization")
        if st.button("Go to CPU Scheduling"):
            st.session_state.module = "CPU Scheduling"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("🧠 Memory Management")
        st.write("Simulate memory allocation techniques.")
        st.markdown("- Paging & Segmentation\n- Page replacement algorithms\n- Virtual memory simulation")
        if st.button("Go to Memory Management"):
            st.session_state.module = "Memory Management"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="module-header">System Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("System Stats")
        stats = {
            "CPU Usage": "32%",
            "Memory Usage": "512 MB / 1024 MB",
            "Processes": f"{len(st.session_state.process_sim.get_processes())} active",
            "Average Wait Time": "12.5 ms",
            "Page Faults": "5"
        }
        for key, value in stats.items():
            st.metric(key, value)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Resource Usage")
        fig = px.pie(
            names=['Used', 'Free'],
            values=[512, 512],
            title="Memory Allocation"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_process_management():
    st.markdown('<div class="module-header">Process Management Module</div>', unsafe_allow_html=True)
    process_sim = st.session_state.process_sim
    
    with st.form("process_form"):
        st.subheader("Process Creation")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Process Name", f"Process_{process_sim.next_pid}")
            priority = st.slider("Priority", 1, 10, 5)
        with col2:
            memory = st.number_input("Memory Required (MB)", 1, 1000, 64)
            burst_time = st.number_input("CPU Burst Time (ms)", 1, 1000, 50)
        submitted = st.form_submit_button("Create Process")
        
        if submitted:
            pid = process_sim.create_process(name, priority, memory, burst_time)
            st.success(f"Process {name} (PID: {pid}) created!")
    
    with st.form("state_form"):
        st.subheader("Update Process State")
        processes = process_sim.get_processes()
        if processes:
            pid = st.selectbox("Select Process", options=list(processes.keys()))
            state = st.selectbox("New State", options=['New', 'Ready', 'Running', 'Waiting', 'Terminated'])
            update = st.form_submit_button("Update State")
            
            if update:
                if state == 'Terminated':
                    process_sim.terminate_process(pid)
                    st.success(f"Process {pid} terminated!")
                else:
                    process_sim.update_state(pid, state)
                    st.success(f"Process {pid} state updated to {state}!")
    
    processes = process_sim.get_processes()
    if processes:
        st.subheader("Active Processes")
        df = pd.DataFrame.from_dict(processes, orient='index')
        st.dataframe(df, use_container_width=True)
    
    history = process_sim.get_history()
    if history:
        st.subheader("Process History")
        df_history = pd.DataFrame(history)
        st.dataframe(df_history, use_container_width=True)

def display_cpu_scheduling():
    st.markdown('<div class="module-header">CPU Scheduling Module</div>', unsafe_allow_html=True)
    scheduler = st.session_state.cpu_scheduler
    
    with st.form("add_process_form"):
        st.subheader("Add Process")
        pid = st.number_input("Process ID", min_value=1, step=1)
        burst_time = st.number_input("Burst Time (ms)", min_value=1, value=50)
        priority = st.number_input("Priority", min_value=0, value=0)
        add = st.form_submit_button("Add Process")
        
        if add:
            scheduler.add_process(pid, burst_time, priority)
            st.success(f"Process {pid} added!")
    
    st.subheader("Run Scheduling Algorithm")
    algo = st.selectbox("Algorithm", ["FCFS", "SJF", "Round Robin"])
    quantum = None
    if algo == "Round Robin":
        quantum = st.number_input("Time Quantum", min_value=1, value=10)
    
    if st.button("Run Simulation"):
        if algo == "FCFS":
            metrics = scheduler.fcfs()
        elif algo == "SJF":
            metrics = scheduler.sjf()
        else:
            metrics = scheduler.round_robin(quantum)
        
        st.subheader("Gantt Chart")
        st.plotly_chart(scheduler.plot_gantt(), use_container_width=True)
        
        st.subheader("Performance Metrics")
        df_metrics = pd.DataFrame(metrics)
        st.dataframe(df_metrics, use_container_width=True)

def display_memory_management():
    st.markdown('<div class="module-header">Memory Management Module</div>', unsafe_allow_html=True)
    
    technique = st.sidebar.selectbox("Technique", ["Paging", "Segmentation"])
    total_memory = st.sidebar.number_input("Total Memory (KB)", min_value=100, value=1024, step=100)
    
    if technique == "Paging":
        page_size = st.sidebar.number_input("Page Size (KB)", min_value=1, value=16, step=1)
        algo = st.sidebar.selectbox("Replacement Algorithm", ["FIFO", "LRU", "LFU"])
        
        if 'paging_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
            st.session_state.paging_sim = MemorySimulator(total_memory, page_size)
            st.session_state.time_step = 0
            st.session_state.process_history = []
        
        sim = st.session_state.paging_sim
        with st.form("paging_form"):
            st.subheader("Process Management")
            col1, col2 = st.columns(2)
            with col1:
                pid = st.text_input("Process ID", f"P{len(st.session_state.process_history) + 1}")
                size = st.number_input("Size (KB)", min_value=1, value=32)
                add = st.form_submit_button("Add Process")
            with col2:
                active = [p['id'] for p in st.session_state.process_history if p['active']]
                if active:
                    remove_pid = st.selectbox("Remove Process", options=active)
                    remove = st.form_submit_button("Remove Process")
                else:
                    remove = False
            
            if add:
                success = sim.allocate_process(pid, size, algo, st.session_state.time_step)
                st.session_state.process_history.append({
                    'id': pid, 'size': size, 'time_added': st.session_state.time_step, 'active': True
                })
                st.session_state.time_step += 1
                if success:
                    st.success(f"Process {pid} allocated!")
                else:
                    st.error(f"Failed to allocate process {pid}")
            
            if remove and active:
                for p in st.session_state.process_history:
                    if p['id'] == remove_pid:
                        p['active'] = False
                sim.deallocate_process(remove_pid)
                st.session_state.time_step += 1
                st.success(f"Process {remove_pid} removed!")
        
        memory, page_faults = sim.get_state()
        st.subheader("Memory Map")
        st.plotly_chart(sim.plot_memory(), use_container_width=True)
        
        st.subheader("Page Table")
        active_processes = [p['id'] for p in st.session_state.process_history if p['active']]
        if active_processes:
            page_data = {pid: [i for i, x in enumerate(memory) if x == pid] for pid in active_processes}
            max_pages = max([len(pages) for pages in page_data.values()], default=0)
            for pid in page_data:
                page_data[pid] = page_data[pid] + [None] * (max_pages - len(page_data[pid]))
            df_pages = pd.DataFrame(page_data)
            st.dataframe(df_pages, use_container_width=True)
        
        st.subheader("Metrics")
        metrics = sim.get_metrics()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Page Faults", metrics["page_faults"])
        with col2:
            st.metric("Hit Ratio", f"{metrics['hit_ratio']:.2%}")
        with col3:
            st.metric("Internal Fragmentation", f"{metrics['internal_fragmentation']} KB")
    
    else:  # Segmentation
        if 'seg_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
            st.session_state.seg_sim = SegmentationSimulator(total_memory)
            st.session_state.seg_processes = {}
        
        sim = st.session_state.seg_sim
        algo = st.sidebar.selectbox("Allocation Algorithm", ["First-Fit", "Best-Fit", "Worst-Fit"])
        
        with st.form("segment_form"):
            st.subheader("Segment Management")
            col1, col2 = st.columns(2)
            with col1:
                pid = st.text_input("Process ID", "P1")
                seg_name = st.text_input("Segment Name", "code")
                size = st.number_input("Size (KB)", min_value=1, value=64)
                add = st.form_submit_button("Add Segment")
            with col2:
                if sim.segment_table:
                    processes = list(sim.segment_table.keys())
                    remove_pid = st.selectbox("Remove Process", options=processes)
                    remove = st.form_submit_button("Remove Process")
                else:
                    remove = False
            
            if add:
                success, addr = sim.allocate_segment(pid, seg_name, size, algo)
                if success:
                    st.success(f"Segment '{seg_name}' allocated at {addr}")
                    if pid not in st.session_state.seg_processes:
                        st.session_state.seg_processes[pid] = []
                    st.session_state.seg_processes[pid].append({'name': seg_name, 'size': size, 'address': addr})
                else:
                    st.error(f"Failed to allocate segment '{seg_name}'")
            
            if remove and sim.segment_table:
                sim.deallocate_segment(remove_pid)
                if remove_pid in st.session_state.seg_processes:
                    del st.session_state.seg_processes[remove_pid]
                st.success(f"Process {remove_pid} removed!")
        
        st.subheader("Memory Map")
        st.plotly_chart(sim.plot_memory(), use_container_width=True)
        
        st.subheader("Segment Table")
        memory, segment_table, seg_faults = sim.get_state()
        if segment_table:
            segments_data = []
            for pid, segments in segment_table.items():
                for name, start, size in segments:
                    segments_data.append({
                        'Process': pid,
                        'Segment': name,
                        'Base Address': start,
                        'Size': size
                    })
            st.dataframe(pd.DataFrame(segments_data), use_container_width=True)
            st.metric("Segmentation Faults", seg_faults)

if __name__ == "__main__":
    main()