import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from memory_simulator import MemorySimulator, SegmentationSimulator, VirtualMemorySimulator

def main():
    st.set_page_config(
        page_title="Memory Management Visualizer",
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
    
    st.markdown('<div class="main-header">Dynamic Memory Management Visualizer</div>', unsafe_allow_html=True)
    
    st.sidebar.header("Memory Management")
    technique = st.sidebar.radio("Technique", ["Paging", "Segmentation", "Virtual Memory"])
    
    if technique == "Paging":
        display_paging()
    elif technique == "Segmentation":
        display_segmentation()
    else:  # Virtual Memory
        display_virtual_memory()

def display_paging():
    st.markdown('<div class="module-header">Paging Simulation</div>', unsafe_allow_html=True)
    
    total_memory = st.sidebar.number_input("Total Memory (KB)", min_value=100, value=1024, step=100)
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
                remove = st.form_submit_button("Remove Process (No active processes)")
        
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

def display_segmentation():
    st.markdown('<div class="module-header">Segmentation Simulation</div>', unsafe_allow_html=True)
    
    total_memory = st.sidebar.number_input("Total Memory (KB)", min_value=100, value=1024, step=100)
    algo = st.sidebar.selectbox("Allocation Algorithm", ["First-Fit", "Best-Fit", "Worst-Fit"])
    
    if 'seg_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
        st.session_state.seg_sim = SegmentationSimulator(total_memory)
        st.session_state.seg_processes = {}
    
    sim = st.session_state.seg_sim
    
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
                remove = st.form_submit_button("Remove Process (No processes)")
        
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
    
    st.subheader("Fragmentation Analysis")
    frag_data = sim.analyze_fragmentation()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Memory Usage", f"{frag_data['used_memory']}/{frag_data['total_memory']} KB")
    with col2:
        st.metric("External Fragmentation", f"{frag_data['external_fragmentation']} KB")
    with col3:
        st.metric("Free Memory Blocks", frag_data['num_free_blocks'])
    with col4:
        frag_percent = f"{frag_data['fragmentation_index'] * 100:.1f}%"
        st.metric("Fragmentation Index", frag_percent)
    
    frag_fig, blocks_fig = sim.plot_fragmentation()
    st.plotly_chart(frag_fig, use_container_width=True)
    if blocks_fig:
        st.plotly_chart(blocks_fig, use_container_width=True)

def display_virtual_memory():
    st.markdown('<div class="module-header">Virtual Memory Simulation</div>', unsafe_allow_html=True)
    
    physical_memory = st.sidebar.number_input("Physical Memory (KB)", min_value=100, value=512, step=100)
    virtual_memory = st.sidebar.number_input("Virtual Memory (KB)", min_value=physical_memory, value=1024, step=100)
    page_size = st.sidebar.number_input("Page Size (KB)", min_value=1, value=16, step=1)
    algo = st.sidebar.selectbox("Replacement Algorithm", ["FIFO", "LRU", "LFU"])
    
    if 'virtual_sim' not in st.session_state or st.sidebar.button("Reset Simulator"):
        st.session_state.virtual_sim = VirtualMemorySimulator(physical_memory, virtual_memory, page_size)
        st.session_state.vm_process_counter = 1
        st.session_state.vm_access_history = []
    
    sim = st.session_state.virtual_sim
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Allocate Memory")
        with st.form("vm_allocate_form"):
            process_id = st.text_input("Process ID", f"P{st.session_state.vm_process_counter}")
            size = st.number_input("Process Size (KB)", min_value=1, value=64, step=1)
            allocate = st.form_submit_button("Allocate Virtual Memory")
            
            if allocate:
                success, result = sim.allocate_process(process_id, size)
                if success:
                    st.success(f"Virtual memory allocated for process {process_id}")
                    st.session_state.vm_process_counter += 1
                else:
                    st.error(f"Failed to allocate memory: {result}")
    
    with col2:
        st.subheader("Access Memory")
        with st.form("vm_access_form"):
            address = st.number_input("Virtual Address", min_value=0, value=0, step=page_size)
            process = st.text_input("Process ID for Access", "P1")
            is_write = st.checkbox("Write Access")
            access = st.form_submit_button("Access Memory")
            
            if access:
                success, physical_addr, was_fault = sim.access_address(address, process, is_write, algo)
                if success:
                    page_num = address // page_size
                    offset = address % page_size
                    phys_page = physical_addr // page_size
                    
                    result_msg = f"Virtual Address: {address} (Page {page_num}, Offset {offset})\n"
                    result_msg += f"Physical Address: {physical_addr} (Frame {phys_page}, Offset {offset})"
                    
                    if was_fault:
                        result_msg += "\nPage Fault Occurred! Page loaded from disk."
                    
                    st.session_state.vm_access_history.append({
                        'address': address,
                        'process': process,
                        'physical': physical_addr,
                        'fault': was_fault,
                        'time': len(st.session_state.vm_access_history) + 1
                    })
                    
                    st.success(result_msg)
                else:
                    st.error("Memory access failed!")
    
    st.subheader("Memory Maps")
    phys_fig, virt_fig = sim.plot_memory_maps()
    st.plotly_chart(phys_fig, use_container_width=True)
    st.plotly_chart(virt_fig, use_container_width=True)
    
    st.subheader("Performance Metrics")
    metrics = sim.get_metrics()
    cols = st.columns(len(metrics))
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i]:
            formatted_value = f"{value:.2%}" if "utilization" in key else value
            st.metric(key.replace("_", " ").title(), formatted_value)
    
    if st.session_state.vm_access_history:
        st.subheader("Access History")
        access_df = pd.DataFrame(st.session_state.vm_access_history)
        st.dataframe(access_df, use_container_width=True)
        
        # Access pattern visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=access_df['time'],
            y=access_df['address'],
            mode='markers+lines',
            marker=dict(
                size=10,
                color=['red' if fault else 'green' for fault in access_df['fault']],
                symbol=['x' if fault else 'circle' for fault in access_df['fault']]
            ),
            name='Memory Access'
        ))
        fig.update_layout(
            title="Memory Access Pattern",
            xaxis_title="Access Sequence",
            yaxis_title="Virtual Address",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()