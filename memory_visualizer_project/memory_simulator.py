import numpy as np
import plotly.graph_objects as go
import pandas as pd
from collections import deque

class MemorySimulator:
    def __init__(self, total_memory, page_size):
        if total_memory <= 0 or page_size <= 0:
            raise ValueError("Memory and page size must be positive integers.")
        if total_memory < page_size:
            raise ValueError("Total memory must be greater than page size.")
        
        self.total_memory = int(total_memory)
        self.page_size = int(page_size)
        self.num_pages = self.total_memory // self.page_size
        self.memory = [None] * self.num_pages
        self.page_faults = 0
        self.hits = 0
        self.fifo_queue = deque()
        self.lru_tracker = {}
        self.lfu_counter = {}
        self.history = []
        self.internal_fragmentation = 0
        self.external_fragmentation = 0

    def allocate_process(self, process_id, process_size, algorithm="FIFO", time_step=0):
        if not (0 < process_size <= self.total_memory):
            raise ValueError(f"Invalid process size: {process_size}")
        
        pages_needed = (process_size + self.page_size - 1) // self.page_size
        self.internal_fragmentation += (pages_needed * self.page_size) - process_size
        free_pages = self.memory.count(None)
        
        if free_pages >= pages_needed:  #agar memory khali hai ya enough space hai to directly insert the page
            self._allocate_free_pages(process_id, pages_needed, time_step) #actually puts the process into memory
            return True #Allocation is successfull
        else:   #enough space nahi hai
            self.page_faults += (pages_needed - free_pages)
            self._allocate_free_pages(process_id, free_pages, time_step) #jitne jaa skte utne daalo
            pages_to_replace = pages_needed - free_pages    
            for _ in range(pages_to_replace):
                if not self._replace_page(algorithm, process_id, time_step):
                    return False
            return True

    def _allocate_free_pages(self, process_id, num_pages, time_step):
        pages_allocated = 0
        for i in range(self.num_pages):
            if self.memory[i] is None and pages_allocated < num_pages:  #memory mei None hai yaani empty hai aur pages to allocate less than free pages
                self.memory[i] = process_id #assign the ith memory space to current process
                self.fifo_queue.append(i)   
                self.lru_tracker[i] = time_step #which page was used long ago
                self.lfu_counter[i] = self.lfu_counter.get(i, 0)    #If this slot isn’t in the LFU counter yet, set its count to 0. LFU uses this to know how many times a page has been accessed.
                pages_allocated += 1
        self.history.append(self.memory.copy()) #visualization k liye

    def _replace_page(self, algorithm, process_id, time_step):
        if algorithm == "FIFO" and self.fifo_queue: #algo is FIFO and fifo queue not empty
            old_page = self.fifo_queue.popleft() #oldest page
            self.memory[old_page] = process_id #oldest page ki index pr process id
            self.fifo_queue.append(old_page) # Add this page back to the end of the queue (since it now contains a new process).
            self.lru_tracker[old_page] = time_step #Update its last used time (needed even for LFU or future LRU).
            self.lfu_counter[old_page] = 0  # Reset frequency count for the new page (for LFU use later).
            self.history.append(self.memory.copy())
            return True
        elif algorithm == "LRU" and self.lru_tracker:
            oldest = min(self.lru_tracker, key=self.lru_tracker.get)
            self.memory[oldest] = process_id
            self.lru_tracker[oldest] = time_step
            self.lfu_counter[oldest] = 0
            self.history.append(self.memory.copy())
            return True
        elif algorithm == "LFU" and self.lfu_counter:
            least_freq = min(self.lfu_counter.values())
            candidates = [p for p, c in self.lfu_counter.items() if c == least_freq]
            old_page = min(candidates, key=lambda x: self.lru_tracker.get(x, float('inf')))
            self.memory[old_page] = process_id
            self.lru_tracker[old_page] = time_step
            self.lfu_counter[old_page] = 0
            self.history.append(self.memory.copy())
            return True
        return False

    def deallocate_process(self, process_id):
        for i in range(self.num_pages):
            if self.memory[i] == process_id:
                self.memory[i] = None
                if i in self.fifo_queue:
                    self.fifo_queue.remove(i)
                if i in self.lru_tracker:
                    del self.lru_tracker[i]
                if i in self.lfu_counter:
                    del self.lfu_counter[i]
        self.history.append(self.memory.copy())

    def access_page(self, page_number, time_step):
        if 0 <= page_number < self.num_pages and self.memory[page_number] is not None:
            self.lru_tracker[page_number] = time_step
            self.lfu_counter[page_number] = self.lfu_counter.get(page_number, 0) + 1
            self.hits += 1
            return True
        else:
            self.page_faults += 1
            return False

    def get_state(self):
        return self.memory.copy(), self.page_faults

    def get_history(self):
        return self.history

    def get_metrics(self):
        total_accesses = self.hits + self.page_faults
        hit_ratio = self.hits / total_accesses if total_accesses > 0 else 0
        return {
            "page_faults": self.page_faults,
            "hits": self.hits,
            "hit_ratio": hit_ratio,
            "internal_fragmentation": self.internal_fragmentation,
            "external_fragmentation": self.external_fragmentation
        }

    def plot_memory(self):
        memory = self.memory
        unique_processes = set(p for p in memory if p is not None)
        colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
        color_map = {p: colors[i % len(colors)] for i, p in enumerate(unique_processes)}
        color_map[None] = 'lightgray'

        fig = go.Figure(data=[
            go.Bar(
                x=list(range(len(memory))),
                y=[1] * len(memory),
                marker_color=[color_map[p] for p in memory],
                text=[str(p) if p is not None else '' for p in memory],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Memory Map",
            xaxis_title="Page Number",
            showlegend=False,
            height=300
        )
        return fig

class SegmentationSimulator:
    def __init__(self, total_memory):
        if total_memory <= 0:
            raise ValueError("Memory size must be a positive integer.")
        self.total_memory = int(total_memory)
        self.memory = [None] * self.total_memory
        self.segment_table = {}
        self.free_blocks = [(0, self.total_memory)]
        self.history = []
        self.segmentation_faults = 0

    def allocate_segment(self, process_id, segment_name, segment_size, algorithm="First-Fit"):
        if not (0 < segment_size <= self.total_memory):
            raise ValueError(f"Invalid segment size: {segment_size}")
        
        block_index = None
        if algorithm == "First-Fit":
            block_index = self._first_fit(segment_size)
        elif algorithm == "Best-Fit":
            block_index = self._best_fit(segment_size)
        elif algorithm == "Worst-Fit":
            block_index = self._worst_fit(segment_size)
        
        if block_index is None:
            self.segmentation_faults += 1
            return False, None
        
        start, size = self.free_blocks[block_index]
        if size == segment_size:
            self.free_blocks.pop(block_index)
        else:
            self.free_blocks[block_index] = (start + segment_size, size - segment_size)
        
        for i in range(start, start + segment_size):
            self.memory[i] = (process_id, segment_name)
        
        if process_id not in self.segment_table:
            self.segment_table[process_id] = []
        self.segment_table[process_id].append((segment_name, start, segment_size))
        self.history.append(self.memory.copy())
        return True, start

    def _first_fit(self, size):
        for i, (start, block_size) in enumerate(self.free_blocks):
            if block_size >= size:
                return i
        return None

    def _best_fit(self, size):
        best_idx = None
        best_fit = float('inf')
        for i, (start, block_size) in enumerate(self.free_blocks):
            if size <= block_size < best_fit:
                best_idx = i
                best_fit = block_size
        return best_idx

    def _worst_fit(self, size):
        worst_idx = None
        worst_fit = 0
        for i, (start, block_size) in enumerate(self.free_blocks):
            if block_size >= size and block_size > worst_fit:
                worst_idx = i
                worst_fit = block_size
        return worst_idx

    def deallocate_segment(self, process_id, segment_name=None):
        if process_id not in self.segment_table:
            return False
        
        segments_to_remove = []
        for seg in self.segment_table[process_id]:
            name, start, size = seg
            if segment_name is None or name == segment_name:
                segments_to_remove.append(seg)
                for i in range(start, start + size):
                    self.memory[i] = None
                self.free_blocks.append((start, size))
        
        for seg in segments_to_remove:
            self.segment_table[process_id].remove(seg)
        
        if not self.segment_table[process_id]:
            del self.segment_table[process_id]
        
        self._merge_free_blocks()
        self.history.append(self.memory.copy())
        return True

    def _merge_free_blocks(self):
        if not self.free_blocks:
            return
        self.free_blocks.sort(key=lambda x: x[0])
        merged = [self.free_blocks[0]]
        for start, size in self.free_blocks[1:]:
            prev_start, prev_size = merged[-1]
            if prev_start + prev_size == start:
                merged[-1] = (prev_start, prev_size + size)
            else:
                merged.append((start, size))
        self.free_blocks = merged

    def get_state(self):
        return self.memory.copy(), self.segment_table.copy(), self.segmentation_faults

    def plot_memory(self):
        memory = self.memory
        processes = set(pid for pid, _ in [m for m in memory if m is not None])
        colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
        color_map = {pid: colors[i % len(colors)] for i, pid in enumerate(processes)}
        
        segments = []
        colors_list = []
        starts = []
        for i in range(len(memory)):
            if memory[i] is None:
                if not segments or segments[-1] != "Free":
                    segments.append("Free")
                    colors_list.append("lightgray")
                    starts.append(i)
            else:
                pid, seg_name = memory[i]
                label = f"{pid}:{seg_name}"
                if not segments or segments[-1] != label:
                    segments.append(label)
                    colors_list.append(color_map[pid])
                    starts.append(i)
        
        starts.append(len(memory))
        fig = go.Figure()
        for i in range(len(segments)):
            start = starts[i]
            end = starts[i+1] if i+1 < len(starts) else len(memory)
            width = end - start
            fig.add_trace(go.Bar(
                x=[start + width/2],
                y=[1],
                width=width,
                marker_color=colors_list[i],
                name=segments[i],
                text=segments[i] if width > 10 else '',
                textposition='auto'
            ))
        
        fig.update_layout(
            title="Memory Map - Segmentation",
            xaxis_title="Memory Address",
            showlegend=True,
            height=300,
            barmode='stack'
        )
        return fig

    def calculate_fragmentation(self):
        if not self.free_blocks:
            return 0
        total_free = sum(size for _, size in self.free_blocks)
        largest_free = max(size for _, size in self.free_blocks)
        return (total_free - largest_free) / total_free * 100 if total_free > 0 else 0
    # Add this method to the SegmentationSimulator class in memory_simulator.py

    def analyze_fragmentation(self):
        """Performs detailed fragmentation analysis"""
        # Calculate total memory
        total_memory = self.total_memory
        
        # Calculate used memory
        used_memory = 0
        for process_id, segments in self.segment_table.items():
            for _, _, size in segments:
                used_memory += size
        
        # Calculate free memory
        free_memory = total_memory - used_memory
        
        # Calculate external fragmentation
        external_fragmentation = 0
        largest_free_block = 0
        
        if self.free_blocks:
            largest_free_block = max(size for _, size in self.free_blocks)
            # External fragmentation is free memory that cannot be allocated to the largest request
            external_fragmentation = free_memory - largest_free_block
        
        # Calculate number of free blocks
        num_free_blocks = len(self.free_blocks)
        
        # Average size of free blocks
        avg_free_block_size = free_memory / num_free_blocks if num_free_blocks > 0 else 0
        
        # Fragmentation index (higher means more fragmented)
        fragmentation_index = 1 - (largest_free_block / free_memory) if free_memory > 0 else 0
        
        return {
            "total_memory": total_memory,
            "used_memory": used_memory,
            "free_memory": free_memory,
            "external_fragmentation": external_fragmentation,
            "largest_free_block": largest_free_block,
            "num_free_blocks": num_free_blocks,
            "avg_free_block_size": avg_free_block_size,
            "fragmentation_index": fragmentation_index
        }

    def plot_fragmentation(self):
        """Creates a visualization of memory fragmentation"""
        frag_data = self.analyze_fragmentation()
        
        # Plot memory usage
        labels = ['Used Memory', 'Largest Free Block', 'External Fragmentation']
        values = [
            frag_data['used_memory'], 
            frag_data['largest_free_block'],
            frag_data['external_fragmentation']
        ]
        
        colors = ['#636EFA', '#00CC96', '#EF553B']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="Memory Fragmentation Analysis",
            height=300
        )
        
        # Plot free blocks distribution
        block_sizes = [size for _, size in self.free_blocks]
        
        if block_sizes:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[f"Block {i}" for i in range(len(block_sizes))],
                y=block_sizes,
                marker_color='#00CC96'
            ))
            
            fig2.update_layout(
                title="Free Memory Block Distribution",
                xaxis_title="Memory Blocks",
                yaxis_title="Size (KB)",
                height=300
            )
            
            return fig, fig2
        
        return fig, None
# Add this class to memory_simulator.py

class VirtualMemorySimulator:
    def __init__(self, physical_memory_size, virtual_memory_size, page_size):
        self.physical_memory_size = physical_memory_size
        self.virtual_memory_size = virtual_memory_size
        self.page_size = page_size
        
        self.physical_pages = physical_memory_size // page_size
        self.virtual_pages = virtual_memory_size // page_size
        
        # Initialize physical memory and page table
        self.physical_memory = [None] * self.physical_pages
        self.page_table = {}  # Maps virtual page -> physical frame
        self.reverse_mapping = {}  # Maps physical frame -> virtual page
        
        # For swap space simulation
        self.swap_space = {}  # Maps virtual page -> stored content
        
        # Metrics
        self.page_faults = 0
        self.disk_writes = 0
        self.disk_reads = 0
        
        # For page replacement
        self.fifo_queue = deque()
        self.lru_tracker = {}
        self.lfu_counter = {}
        self.access_time = 0
    
    def access_address(self, virtual_address, process_id, write=False, algorithm="LRU"):
        """Simulates memory access with demand paging"""
        virtual_page = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # Update access time
        self.access_time += 1
        
        # Check if page is in memory (page hit)
        if virtual_page in self.page_table:
            physical_frame = self.page_table[virtual_page]
            
            # Update replacement data
            if algorithm == "LRU":
                self.lru_tracker[physical_frame] = self.access_time
            elif algorithm == "LFU":
                self.lfu_counter[physical_frame] = self.lfu_counter.get(physical_frame, 0) + 1
                
            physical_address = physical_frame * self.page_size + offset
            return True, physical_address, False
        
        # Page fault handling
        self.page_faults += 1
        
        # Find free frame if available
        free_frame = None
        for i in range(self.physical_pages):
            if self.physical_memory[i] is None:
                free_frame = i
                break
        
        # If no free frame, use replacement algorithm
        if free_frame is None:
            free_frame = self._replace_page(algorithm)
            
            # Handle victim page (swap out)
            victim_virtual_page = self.reverse_mapping[free_frame]
            self.swap_space[victim_virtual_page] = f"Data for {process_id}:{victim_virtual_page}"
            del self.page_table[victim_virtual_page]
            self.disk_writes += 1
        
        # Load page into memory (swap in if needed)
        if virtual_page in self.swap_space:
            # Reading from swap space
            self.disk_reads += 1
        
        # Update mappings
        self.physical_memory[free_frame] = process_id
        self.page_table[virtual_page] = free_frame
        self.reverse_mapping[free_frame] = virtual_page
        
        # Update replacement data
        self.fifo_queue.append(free_frame)
        self.lru_tracker[free_frame] = self.access_time
        self.lfu_counter[free_frame] = 1
        
        physical_address = free_frame * self.page_size + offset
        return True, physical_address, True  # Success, physical address, was page fault
    
    def _replace_page(self, algorithm):
        """Choose a page to replace based on the selected algorithm"""
        if algorithm == "FIFO" and self.fifo_queue:
            return self.fifo_queue.popleft()
        elif algorithm == "LRU" and self.lru_tracker:
            victim = min(self.lru_tracker.items(), key=lambda x: x[1])[0]
            return victim
        elif algorithm == "LFU" and self.lfu_counter:
            # Get least frequently used frames
            min_usage = min(self.lfu_counter.values())
            candidates = [frame for frame, count in self.lfu_counter.items() if count == min_usage]
            # If multiple candidates, use LRU as tie-breaker
            return min(candidates, key=lambda frame: self.lru_tracker.get(frame, 0))
        else:
            # Default to first frame if no algorithm can be applied
            return 0
    
    def allocate_process(self, process_id, size):
        """Pre-allocates virtual memory for a process"""
        pages_needed = (size + self.page_size - 1) // self.page_size
        virtual_pages = []
        
        # Find available virtual pages
        for i in range(self.virtual_pages):
            if len(virtual_pages) < pages_needed and i not in self.page_table and i not in self.swap_space:
                virtual_pages.append(i)
        
        if len(virtual_pages) < pages_needed:
            return False, "Not enough virtual memory"
        
        return True, virtual_pages
    
    def get_metrics(self):
        """Return performance metrics"""
        return {
            "page_faults": self.page_faults,
            "disk_reads": self.disk_reads,
            "disk_writes": self.disk_writes,
            "physical_utilization": len([p for p in self.physical_memory if p is not None]) / self.physical_pages,
            "swap_utilization": len(self.swap_space) / self.virtual_pages if self.virtual_pages > 0 else 0
        }
    
    def plot_memory_maps(self):
        """Create visualizations for physical and virtual memory"""
        # Physical memory visualization
        phys_colors = []
        phys_text = []
        unique_processes = set(p for p in self.physical_memory if p is not None)
        color_map = {p: f'rgba({(hash(str(p)) % 255)}, {(hash(str(p)) * 123) % 255}, {(hash(str(p)) * 77) % 255}, 0.7)' 
                     for p in unique_processes}
        color_map[None] = 'rgba(220, 220, 220, 0.7)'
        
        for i, proc in enumerate(self.physical_memory):
            phys_colors.append(color_map[proc])
            virtual_page = self.reverse_mapping.get(i, "")
            phys_text.append(f"F{i}: {proc or 'Free'}<br>VP: {virtual_page}")
        
        # Virtual memory visualization (both in memory and in swap)
        v_colors = []
        v_text = []
        
        for i in range(self.virtual_pages):
            if i in self.page_table:
                physical_frame = self.page_table[i]
                proc = self.physical_memory[physical_frame]
                v_colors.append(color_map[proc])
                v_text.append(f"VP{i}: In Memory (F{physical_frame})")
            elif i in self.swap_space:
                v_colors.append('rgba(255, 165, 0, 0.7)')  # Orange for swap
                v_text.append(f"VP{i}: In Swap")
            else:
                v_colors.append('rgba(220, 220, 220, 0.7)')  # Gray for unallocated
                v_text.append(f"VP{i}: Unallocated")
        
        # Create plots
        physical_fig = go.Figure(data=[
            go.Bar(
                x=list(range(self.physical_pages)),
                y=[1] * self.physical_pages,
                marker_color=phys_colors,
                text=phys_text,
                hoverinfo="text"
            )
        ])
        
        physical_fig.update_layout(
            title="Physical Memory",
            xaxis_title="Frame Number",
            showlegend=False,
            height=200
        )
        
        virtual_fig = go.Figure(data=[
            go.Bar(
                x=list(range(self.virtual_pages)),
                y=[1] * self.virtual_pages,
                marker_color=v_colors,
                text=v_text,
                hoverinfo="text"
            )
        ])
        
        virtual_fig.update_layout(
            title="Virtual Memory",
            xaxis_title="Page Number",
            showlegend=False,
            height=200
        )
        
        return physical_fig, virtual_fig