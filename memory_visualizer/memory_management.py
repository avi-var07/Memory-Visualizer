"""
Memory Management Visualizer - Memory Management Module
Handles memory allocation, paging, and segmentation for the visualization tool.
"""
from PyQt5.QtCore import pyqtSignal
import logging

logging.basicConfig(filename="memory_visualizer.log", level=logging.ERROR)

class MemoryBlock:
    """Represents a block of memory in the system"""
    def __init__(self, start, size, is_free=True, process_id=None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id
    
    def __str__(self):
        status = "Free" if self.is_free else f"Allocated (Process {self.process_id})"
        return f"Block [start={self.start}, size={self.size}, {status}]"

class Page:
    """Represents a page in the paging system"""
    def __init__(self, page_id, frame_id=None, is_valid=False):
        self.page_id = page_id
        self.frame_id = frame_id
        self.is_valid = is_valid
        self.last_access_time = 0
        self.load_time = 0

class Segment:
    """Represents a segment in the segmentation system"""
    def __init__(self, segment_id, base=None, limit=None, is_valid=False):
        self.segment_id = segment_id
        self.base = base
        self.limit = limit
        self.is_valid = is_valid

class MemoryManager:
    """Main memory manager class that handles memory allocation and visualization"""
    history_changed = pyqtSignal()  # Moved to class level

    def __init__(self, total_memory_size=1024, page_size=16):
        self.total_memory_size = total_memory_size
        self.page_size = page_size
        self.num_frames = total_memory_size // page_size
        
        # For contiguous allocation
        self.memory_blocks = [MemoryBlock(0, total_memory_size)]
        
        # For paging
        self.frames = [None] * self.num_frames
        self.page_tables = {}  # Process ID -> Page Table mapping
        self.access_time = 0
        
        # For segmentation
        self.segment_tables = {}  # Process ID -> Segment Table mapping
        
        self.history = []
        self.current_algorithm = "first_fit"
        
    def record_action(self, action):
        action["time"] = len(self.history)
        self.history.append(action)
        if action.get("type") in ["error", "page_fault", "segmentation_fault"]:
            logging.error(str(action))
        try:
            self.history_changed.emit()
        except Exception as e:
            logging.error(f"Signal emit failed: {e}")

    def set_algorithm(self, algorithm):
        self.current_algorithm = algorithm
        self.record_action({"type": "algorithm_change", "algorithm": algorithm})
    
    def allocate_memory(self, process_id, size):
        """Allocate memory using the current algorithm"""
        if size <= 0:
            self.record_action({"type": "error", "message": "Invalid allocation size"})
            return False
        if self.current_algorithm == "first_fit":
            return self.first_fit_allocation(process_id, size)
        elif self.current_algorithm == "best_fit":
            return self.best_fit_allocation(process_id, size)
        elif self.current_algorithm == "worst_fit":
            return self.worst_fit_allocation(process_id, size)
        
    def first_fit_allocation(self, process_id, size):
        """First-fit memory allocation algorithm"""
        for i, block in enumerate(self.memory_blocks):
            if block.is_free and block.size >= size:
                # Found a suitable block
                if block.size > size:
                    # Split the block
                    remaining_size = block.size - size
                    self.memory_blocks[i] = MemoryBlock(block.start, size, False, process_id)
                    self.memory_blocks.insert(i+1, MemoryBlock(block.start + size, remaining_size))
                else:
                    # Use the entire block
                    self.memory_blocks[i].is_free = False
                    self.memory_blocks[i].process_id = process_id
                
                self.record_action({
                    "type": "allocation",
                    "algorithm": "first_fit",
                    "process_id": process_id,
                    "size": size,
                    "block_start": block.start
                })
                return True
        
        self.record_action({
            "type": "allocation_failure",
            "algorithm": "first_fit",
            "process_id": process_id,
            "size": size,
            "reason": "No suitable block found"
        })
        return False
    
    def best_fit_allocation(self, process_id, size):
        """Best-fit memory allocation algorithm"""
        best_fit_index = -1
        best_fit_size = float('inf')
        
        for i, block in enumerate(self.memory_blocks):
            if block.is_free and block.size >= size:
                if block.size < best_fit_size:
                    best_fit_index = i
                    best_fit_size = block.size
        
        if best_fit_index != -1:
            block = self.memory_blocks[best_fit_index]
            if block.size > size:
                # Split the block
                remaining_size = block.size - size
                self.memory_blocks[best_fit_index] = MemoryBlock(block.start, size, False, process_id)
                self.memory_blocks.insert(best_fit_index+1, MemoryBlock(block.start + size, remaining_size))
            else:
                # Use the entire block
                self.memory_blocks[best_fit_index].is_free = False
                self.memory_blocks[best_fit_index].process_id = process_id
            
            self.record_action({
                "type": "allocation",
                "algorithm": "best_fit",
                "process_id": process_id,
                "size": size,
                "block_start": block.start
            })
            return True
        
        self.record_action({
            "type": "allocation_failure",
            "algorithm": "best_fit",
            "process_id": process_id,
            "size": size,
            "reason": "No suitable block found"
        })
        return False
    
    def worst_fit_allocation(self, process_id, size):
        """Worst-fit memory allocation algorithm"""
        worst_fit_index = -1
        worst_fit_size = 0
        
        for i, block in enumerate(self.memory_blocks):
            if block.is_free and block.size >= size:
                if block.size > worst_fit_size:
                    worst_fit_index = i
                    worst_fit_size = block.size
        
        if worst_fit_index != -1:
            block = self.memory_blocks[worst_fit_index]
            if block.size > size:
                # Split the block
                remaining_size = block.size - size
                self.memory_blocks[worst_fit_index] = MemoryBlock(block.start, size, False, process_id)
                self.memory_blocks.insert(worst_fit_index+1, MemoryBlock(block.start + size, remaining_size))
            else:
                # Use the entire block
                self.memory_blocks[worst_fit_index].is_free = False
                self.memory_blocks[worst_fit_index].process_id = process_id
            
            self.record_action({
                "type": "allocation",
                "algorithm": "worst_fit",
                "process_id": process_id,
                "size": size,
                "block_start": block.start
            })
            return True
        
        self.record_action({
            "type": "allocation_failure",
            "algorithm": "worst_fit",
            "process_id": process_id,
            "size": size,
            "reason": "No suitable block found"
        })
        return False
    
    def deallocate_memory(self, process_id):
        """Deallocate memory allocated to a specific process"""
        deallocated = False
        for i, block in enumerate(self.memory_blocks):
            if not block.is_free and block.process_id == process_id:
                block.is_free = True
                block.process_id = None
                deallocated = True
                
                # Merge adjacent free blocks
                self.merge_free_blocks()
                
                self.record_action({
                    "type": "deallocation",
                    "process_id": process_id
                })
        
        return deallocated
    
    def merge_free_blocks(self):
        """Merge adjacent free memory blocks to reduce fragmentation"""
        i = 0
        while i < len(self.memory_blocks) - 1:
            if self.memory_blocks[i].is_free and self.memory_blocks[i+1].is_free:
                # Merge blocks
                self.memory_blocks[i].size += self.memory_blocks[i+1].size
                self.memory_blocks.pop(i+1)
            else:
                i += 1
    
    def calculate_fragmentation(self):
        """Calculate external fragmentation in the memory"""
        total_free = 0
        largest_free = 0
        fragmented_free = 0
        
        for block in self.memory_blocks:
            if block.is_free:
                total_free += block.size
                largest_free = max(largest_free, block.size)
        
        if total_free > 0:
            fragmented_free = total_free - largest_free
            fragmentation_percentage = (fragmented_free / total_free) * 100
        else:
            fragmentation_percentage = 0
            
        return {
            "total_free": total_free,
            "largest_free": largest_free,
            "fragmented_free": fragmented_free,
            "fragmentation_percentage": fragmentation_percentage
        }
    
    def allocate_pages(self, process_id, num_pages):
        """Allocate pages to a process"""
        if process_id not in self.page_tables:
            self.page_tables[process_id] = {}
        
        allocated_pages = 0
        for i in range(self.num_frames):
            if allocated_pages >= num_pages:
                break
                
            if self.frames[i] is None:
                page_id = len(self.page_tables[process_id])
                self.frames[i] = process_id
                self.page_tables[process_id][page_id] = Page(page_id, i, True)
                self.page_tables[process_id][page_id].load_time = self.access_time
                allocated_pages += 1
                
                self.record_action({
                    "type": "page_allocation",
                    "process_id": process_id,
                    "page_id": page_id,
                    "frame_id": i
                })
        
        if allocated_pages < num_pages:
            remaining = num_pages - allocated_pages
            for i in range(remaining):
                page_id = len(self.page_tables[process_id])
                self.page_tables[process_id][page_id] = Page(page_id, None, False)
                
                self.record_action({
                    "type": "page_creation",
                    "process_id": process_id,
                    "page_id": page_id,
                    "status": "swapped_out"
                })
        
        return allocated_pages
    
    def access_page(self, process_id, page_id, replacement_algo="FIFO"):
        """Access a page, handling page faults with the specified replacement algorithm"""
        self.access_time += 1
        
        if process_id not in self.page_tables or page_id not in self.page_tables[process_id]:
            self.record_action({
                "type": "error",
                "message": f"Invalid page access: Process {process_id}, Page {page_id}"
            })
            return False
        
        page = self.page_tables[process_id][page_id]
        
        if page.is_valid:
            # Page is in memory, update access time
            page.last_access_time = self.access_time
            
            self.record_action({
                "type": "page_access",
                "process_id": process_id,
                "page_id": page_id,
                "status": "hit"
            })
            return True
        else:
            # Page fault
            self.record_action({
                "type": "page_fault",
                "process_id": process_id,
                "page_id": page_id
            })
            
            # Find free frame
            for i in range(self.num_frames):
                if self.frames[i] is None:
                    self._load_page_into_frame(process_id, page_id, i)
                    return True
            
            # No free frames, need to replace
            if replacement_algo == "FIFO":
                return self._fifo_page_replacement(process_id, page_id)
            elif replacement_algo == "LRU":
                return self._lru_page_replacement(process_id, page_id)
            else:
                return False
    
    def _load_page_into_frame(self, process_id, page_id, frame_id):
        """Load a page into a specific frame"""
        page = self.page_tables[process_id][page_id]
        page.frame_id = frame_id
        page.is_valid = True
        page.load_time = self.access_time
        page.last_access_time = self.access_time
        self.frames[frame_id] = process_id
        
        self.record_action({
            "type": "page_loaded",
            "process_id": process_id,
            "page_id": page_id,
            "frame_id": frame_id
        })
    
    def _fifo_page_replacement(self, process_id, page_id):
        """First-In-First-Out page replacement algorithm"""
        oldest_load_time = float('inf')
        oldest_frame = -1
        oldest_process = None
        oldest_page = None
        
        # Find the oldest loaded page
        for proc_id, page_table in self.page_tables.items():
            for pid, p in page_table.items():
                if p.is_valid and p.load_time < oldest_load_time:
                    oldest_load_time = p.load_time
                    oldest_frame = p.frame_id
                    oldest_process = proc_id
                    oldest_page = pid
        
        if oldest_frame != -1:
            # Invalidate the oldest page
            self.page_tables[oldest_process][oldest_page].is_valid = False
            self.page_tables[oldest_process][oldest_page].frame_id = None
            
            self.record_action({
                "type": "page_replacement",
                "algorithm": "FIFO",
                "evicted_process": oldest_process,
                "evicted_page": oldest_page,
                "frame_id": oldest_frame
            })
            
            # Load the new page
            self._load_page_into_frame(process_id, page_id, oldest_frame)
            return True
        
        return False
    
    def _lru_page_replacement(self, process_id, page_id):
        """Least Recently Used page replacement algorithm"""
        least_recent_time = float('inf')
        lru_frame = -1
        lru_process = None
        lru_page = None
        
        # Find the least recently used page
        for proc_id, page_table in self.page_tables.items():
            for pid, p in page_table.items():
                if p.is_valid and p.last_access_time < least_recent_time:
                    least_recent_time = p.last_access_time
                    lru_frame = p.frame_id
                    lru_process = proc_id
                    lru_page = pid
        
        if lru_frame != -1:
            # Invalidate the LRU page
            self.page_tables[lru_process][lru_page].is_valid = False
            self.page_tables[lru_process][lru_page].frame_id = None
            
            self.record_action({
                "type": "page_replacement",
                "algorithm": "LRU",
                "evicted_process": lru_process,
                "evicted_page": lru_page,
                "frame_id": lru_frame
            })
            
            # Load the new page
            self._load_page_into_frame(process_id, page_id, lru_frame)
            return True
        
        return False
    
    def create_segment(self, process_id, segment_id, size):
        """Create a segment for a process"""
        if process_id not in self.segment_tables:
            self.segment_tables[process_id] = {}
        
        # Allocate memory for the segment
        allocated = self.allocate_memory(f"{process_id}_seg_{segment_id}", size)
        
        if allocated:
            # Find the allocated block
            for block in self.memory_blocks:
                if not block.is_free and block.process_id == f"{process_id}_seg_{segment_id}":
                    self.segment_tables[process_id][segment_id] = Segment(
                        segment_id, block.start, size, True
                    )
                    
                    self.record_action({
                        "type": "segment_creation",
                        "process_id": process_id,
                        "segment_id": segment_id,
                        "base": block.start,
                        "limit": size
                    })
                    return True
        
        self.record_action({
            "type": "segment_creation_failure",
            "process_id": process_id,
            "segment_id": segment_id,
            "size": size
        })
        return False
    
    def access_segment(self, process_id, segment_id, offset):
        """Access a memory location using segmentation"""
        if offset < 0:
            self.record_action({
                "type": "error",
                "message": f"Negative offset: Process {process_id}, Segment {segment_id}"
            })
            return False
        
        if process_id not in self.segment_tables or segment_id not in self.segment_tables[process_id]:
            self.record_action({
                "type": "error",
                "message": f"Invalid segment access: Process {process_id}, Segment {segment_id}"
            })
            return False
        
        segment = self.segment_tables[process_id][segment_id]
        
        if not segment.is_valid:
            self.record_action({
                "type": "error",
                "message": f"Segment not in memory: Process {process_id}, Segment {segment_id}"
            })
            return False
        
        if offset >= segment.limit:
            self.record_action({
                "type": "segmentation_fault",
                "process_id": process_id,
                "segment_id": segment_id,
                "offset": offset,
                "limit": segment.limit
            })
            return False
        
        physical_address = segment.base + offset
        
        self.record_action({
            "type": "segment_access",
            "process_id": process_id,
            "segment_id": segment_id,
            "offset": offset,
            "physical_address": physical_address
        })
        
        return physical_address
    
    def reset(self):
        """Reset the memory manager to initial state"""
        self.memory_blocks = [MemoryBlock(0, self.total_memory_size)]
        self.frames = [None] * self.num_frames
        self.page_tables = {}
        self.segment_tables = {}
        self.access_time = 0
        self.history = []
        
        self.record_action({
            "type": "reset"
        })