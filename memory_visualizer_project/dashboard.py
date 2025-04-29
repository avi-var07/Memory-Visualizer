import streamlit as st
import pandas as pd
from memory_simulator import MemorySimulator, SegmentationSimulator, VirtualMemorySimulator

def main():
    st.set_page_config(
        page_title="Memory Management Simulator",
        page_icon="🧠",
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
    
    st.markdown('<div class="main-header">Dynamic Memory Management Simulator</div>', unsafe_allow_html=True)
    
    if 'technique' not in st.session_state:
        st.session_state.technique = "Paging"
    
    st.sidebar.header("Memory Management Technique")
    technique = st.sidebar.radio("Select Technique", ["Paging", "Segmentation", "Virtual Memory"])
    st.session_state.technique = technique
    
    display_memory_management()

def display_memory_management():
    st.markdown('<div class="module-header">Memory Management Visualization</div>', unsafe_allow_html=True)
    
    technique = st.session_state.technique
    
    # Common parameters for all techniques
    total_memory = st.sidebar.number_input("Total Physical Memory (KB)", min_value=100, value=1024, step=100)
    
    if technique == "Paging":
        display_paging_simulation(total_memory)
    elif technique == "Segmentation":
        display_segmentation_simulation(total_memory)
    else:  # Virtual Memory
        display_virtual_memory_simulation(total_memory)

def display_paging_simulation(total_memory):
    page_size = st.sidebar.number_input("Page Size (KB)", min_value=1, value=16, step=1)
    algo = st.sidebar.selectbox("Page Replacement Algorithm", ["FIFO", "LRU", "LFU"])
    
    if 'paging_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
        st.session_state.paging_sim = MemorySimulator(total_memory, page_size)
        st.session_state.time_step = 0
        st.session_state.process_history = []
    
    sim = st.session_state.paging_sim
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Allocate Memory")
        with st.form("paging_allocate_form"):
            pid = st.text_input("Process ID", f"P{len(st.session_state.process_history) + 1}")
            size = st.number_input("Size (KB)", min_value=1, value=32)
            allocate = st.form_submit_button("Allocate Memory")
            
            if allocate:
                success = sim.allocate_process(pid, size, algo, st.session_state.time_step)
                st.session_state.process_history.append({
                    'id': pid, 'size': size, 'time_added': st.session_state.time_step, 'active': True
                })
                st.session_state.time_step += 1
                if success:
                    st.success(f"Process {pid} allocated successfully!")
                else:
                    st.error(f"Failed to allocate process {pid}. Not enough memory!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Deallocate Memory")
        with st.form("paging_deallocate_form"):
            # Get active processes
            active = [p['id'] for p in st.session_state.process_history if p['active']]
            if active:
                remove_pid = st.selectbox("Select Process to Remove", options=active)
                deallocate = st.form_submit_button("Deallocate Memory")
                
                if deallocate:
                    for p in st.session_state.process_history:
                        if p['id'] == remove_pid:
                            p['active'] = False
                    sim.deallocate_process(remove_pid)
                    st.session_state.time_step += 1
                    st.success(f"Process {remove_pid} removed from memory!")
            else:
                st.write("No active processes to deallocate.")
                st.form_submit_button("Deallocate Memory", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Memory Map Visualization
    st.subheader("Memory Map Visualization")
    memory_fig = sim.plot_memory()
    st.plotly_chart(memory_fig, use_container_width=True)
    
    # Page Table
    st.subheader("Page Table")
    memory, page_faults = sim.get_state()
    active_processes = [p['id'] for p in st.session_state.process_history if p['active']]
    if active_processes:
        page_data = {pid: [i for i, x in enumerate(memory) if x == pid] for pid in active_processes}
        max_pages = max([len(pages) for pages in page_data.values()], default=0)
        for pid in page_data:
            page_data[pid] = page_data[pid] + [None] * (max_pages - len(page_data[pid]))
        df_pages = pd.DataFrame(page_data)
        st.dataframe(df_pages, use_container_width=True)
    else:
        st.info("No active processes in memory.")
    
    # Performance Metrics
    st.subheader("Memory Performance Metrics")
    metrics = sim.get_metrics()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Page Faults", metrics["page_faults"])
    with col2:
        st.metric("Hit Ratio", f"{metrics['hit_ratio']:.2%}")
    with col3:
        st.metric("Internal Fragmentation", f"{metrics['internal_fragmentation']} KB")

def display_segmentation_simulation(total_memory):
    algo = st.sidebar.selectbox("Allocation Algorithm", ["First-Fit", "Best-Fit", "Worst-Fit"])
    
    if 'seg_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
        st.session_state.seg_sim = SegmentationSimulator(total_memory)
        st.session_state.seg_processes = {}
    
    sim = st.session_state.seg_sim
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Allocate Segment")
        with st.form("segment_allocate_form"):
            pid = st.text_input("Process ID", "P1")
            seg_name = st.text_input("Segment Name", "code")
            size = st.number_input("Size (KB)", min_value=1, value=64)
            allocate = st.form_submit_button("Allocate Segment")
            
            if allocate:
                success, addr = sim.allocate_segment(pid, seg_name, size, algo)
                if success:
                    st.success(f"Segment '{seg_name}' allocated at address {addr}")
                    if pid not in st.session_state.seg_processes:
                        st.session_state.seg_processes[pid] = []
                    st.session_state.seg_processes[pid].append({'name': seg_name, 'size': size, 'address': addr})
                else:
                    st.error(f"Failed to allocate segment '{seg_name}'. Not enough contiguous memory!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Deallocate Segment")
        with st.form("segment_deallocate_form"):
            if sim.segment_table:
                deallocate_option = st.radio("Deallocate option", ["Process", "Single Segment"])
                
                if deallocate_option == "Process":
                    processes = list(sim.segment_table.keys())
                    remove_pid = st.selectbox("Select Process to Remove", options=processes)
                    deallocate = st.form_submit_button("Deallocate Process")
                    
                    if deallocate:
                        sim.deallocate_segment(remove_pid)
                        if remove_pid in st.session_state.seg_processes:
                            del st.session_state.seg_processes[remove_pid]
                        st.success(f"Process {remove_pid} removed from memory!")
                else:
                    # Get all processes and their segments
                    all_segments = []
                    for pid in sim.segment_table:
                        for seg_name, _, _ in sim.segment_table[pid]:
                            all_segments.append((pid, seg_name))
                    
                    if all_segments:
                        segment_labels = [f"{pid}:{seg}" for pid, seg in all_segments]
                        selection = st.selectbox("Select Segment to Remove", options=segment_labels)
                        pid, seg_name = selection.split(":")
                        
                        deallocate = st.form_submit_button("Deallocate Segment")
                        
                        if deallocate:
                            sim.deallocate_segment(pid, seg_name)
                            st.success(f"Segment {seg_name} of process {pid} removed from memory!")
                    else:
                        st.write("No segments to deallocate.")
                        st.form_submit_button("Deallocate Segment", disabled=True)
            else:
                st.write("No active segments to deallocate.")
                st.form_submit_button("Deallocate", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Memory Map Visualization
    st.subheader("Memory Map Visualization")
    memory_fig = sim.plot_memory()
    st.plotly_chart(memory_fig, use_container_width=True)
    
    # Fragmentation Analysis
    st.subheader("Fragmentation Analysis")
    frag_fig, block_fig = sim.plot_fragmentation()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(frag_fig, use_container_width=True)
    with col2:
        if block_fig:
            st.plotly_chart(block_fig, use_container_width=True)
    
    # Segment Table
    st.subheader("Segment Table")
    _, segment_table, seg_faults = sim.get_state()
    if segment_table:
        segments_data = []
        for pid, segments in segment_table.items():
            for name, start, size in segments:
                segments_data.append({
                    'Process': pid,
                    'Segment': name,
                    'Base Address': start,
                    'Size': size,
                    'End Address': start + size - 1
                })
        st.dataframe(pd.DataFrame(segments_data), use_container_width=True)
        st.metric("Segmentation Faults", seg_faults)
    else:
        st.info("No segments allocated in memory.")

def display_virtual_memory_simulation(physical_memory):
    virtual_memory = st.sidebar.number_input("Total Virtual Memory (KB)", min_value=physical_memory, value=4096, step=512)
    page_size = st.sidebar.number_input("Page Size (KB)", min_value=1, value=16, step=1)
    algo = st.sidebar.selectbox("Page Replacement Algorithm", ["FIFO", "LRU", "LFU"])
    
    if 'vm_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
        st.session_state.vm_sim = VirtualMemorySimulator(physical_memory, virtual_memory, page_size)
        st.session_state.vm_processes = {}
        st.session_state.access_history = []
    
    sim = st.session_state.vm_sim
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Allocate Virtual Memory")
        with st.form("vm_allocate_form"):
            pid = st.text_input("Process ID", "P1")
            size = st.number_input("Size (KB)", min_value=1, value=128)
            allocate = st.form_submit_button("Allocate Memory")
            
            if allocate:
                success, result = sim.allocate_process(pid, size)
                if success:
                    st.session_state.vm_processes[pid] = {'size': size, 'pages': result}
                    st.success(f"Allocated {size} KB of virtual memory for process {pid}")
                else:
                    st.error(f"Failed to allocate memory: {result}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.subheader("Memory Access Simulation")
        with st.form("memory_access_form"):
            if st.session_state.vm_processes:
                process_options = list(st.session_state.vm_processes.keys())
                access_pid = st.selectbox("Select Process", options=process_options)
                
                if access_pid in st.session_state.vm_processes:
                    process_size = st.session_state.vm_processes[access_pid]['size']
                    max_address = process_size * 1024  # Convert KB to bytes
                    
                    virtual_address = st.number_input(
                        "Virtual Address to Access (bytes)", 
                        min_value=0, 
                        max_value=max_address-1, 
                        value=0
                    )
                    
                    is_write = st.checkbox("Write Operation", value=False)
                    access = st.form_submit_button("Access Memory")
                    
                    if access:
                        success, physical_addr, page_fault = sim.access_address(
                            virtual_address, access_pid, is_write, algo
                        )
                        
                        st.session_state.access_history.append({
                            'process': access_pid,
                            'virtual_addr': virtual_address,
                            'physical_addr': physical_addr if success else None,
                            'page_fault': page_fault,
                            'operation': 'Write' if is_write else 'Read'
                        })
                        
                        if success:
                            fault_text = " (Page Fault)" if page_fault else " (Page Hit)"
                            st.success(f"Memory access successful. Mapped to physical address {physical_addr}{fault_text}")
                        else:
                            st.error("Memory access failed!")
            else:
                st.write("No processes allocated. Please allocate memory first.")
                st.form_submit_button("Access Memory", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Memory Visualization
    st.subheader("Memory Visualization")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Physical Memory")
    with col2:
        st.markdown("#### Virtual Memory")
    
    # Get memory visualizations
    phys_fig, virt_fig = sim.plot_memory_maps()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(phys_fig, use_container_width=True)
    with col2:
        st.plotly_chart(virt_fig, use_container_width=True)
    
    # Access History
    if st.session_state.access_history:
        st.subheader("Memory Access History")
        df_access = pd.DataFrame(st.session_state.access_history)
        st.dataframe(df_access, use_container_width=True)
    
    # Performance Metrics
    st.subheader("Performance Metrics")
    metrics = sim.get_metrics()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Page Faults", metrics["page_faults"])
    with col2:
        st.metric("Disk Reads", metrics["disk_reads"])
    with col3:
        st.metric("Disk Writes", metrics["disk_writes"])

if __name__ == "__main__":
    main()