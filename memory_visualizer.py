"""
Memory Management Visualizer - Main Application
This is the entry point for the Memory Management Visualization Tool.
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
"""
Core Simulation Engine for Memory Management Visualization
"""

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
        """Record an action for history tracking and visualization"""
        self.history.append(action)
        
    def allocate_memory(self, process_id, size):
        """Allocate memory using the current algorithm"""
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
"""
Visualization module for the Memory Management Visualization Tool
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QGraphicsView, QGraphicsScene, 
                            QGraphicsRectItem)
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QTimer
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import math 


class MemoryBlockVisualizer(QWidget):
    """Visualizes the memory blocks for contiguous allocation"""
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.title_label = QLabel("Memory Block Visualization")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.view)
        
        self.info_label = QLabel("Memory Usage: 0%")
        self.layout.addWidget(self.info_label)
        
        # Set up a timer to update the visualization
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(100)  # Update every 100ms
        
    def update_visualization(self):
        """Update the memory block visualization"""
        self.scene.clear()
        
        total_memory = self.memory_manager.total_memory_size
        view_width = self.view.width() - 20
        
        # Calculate block heights and positions
        y_pos = 10
        height = 40
        
        # Process color map
        process_colors = {}
        
        # Draw memory blocks
        for block in self.memory_manager.memory_blocks:
            # Calculate the width proportional to the block size
            width = (block.size / total_memory) * view_width
            
            # Choose color based on block status
            if block.is_free:
                color = QColor(200, 200, 200)  # Gray for free blocks
                text = f"Free: {block.size}"
            else:
                # Create a consistent color for the process
                if block.process_id not in process_colors:
                    # Generate a random color for this process
                    hue = random.random()
                    saturation = 0.7 + random.random() * 0.3
                    value = 0.7 + random.random() * 0.3
                    r, g, b = self._hsv_to_rgb(hue, saturation, value)
                    process_colors[block.process_id] = QColor(int(r*255), int(g*255), int(b*255))
                
                color = process_colors[block.process_id]
                text = f"P{block.process_id}: {block.size}"
            
            # Create and add the block rectangle
            rect = QGraphicsRectItem(0, y_pos, width, height)
            rect.setBrush(QBrush(color))
            rect.setPen(QPen(Qt.black))
            self.scene.addItem(rect)
            
            # Add the text label
            text_item = self.scene.addText(text)
            text_item.setPos(width/2 - text_item.boundingRect().width()/2, 
                             y_pos + height/2 - text_item.boundingRect().height()/2)
            
            # Add the address label
            addr_text = f"{block.start}"
            addr_item = self.scene.addText(addr_text)
            addr_item.setPos(0, y_pos - 15)
            
            y_pos += height + 10
        
        # Add the end address
        end_addr_text = f"{total_memory}"
        end_addr_item = self.scene.addText(end_addr_text)
        end_addr_item.setPos(view_width - end_addr_item.boundingRect().width(), y_pos - 15)
        
        # Update the scene rect to fit all items
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        
        # Update memory usage info
        used_memory = sum(
            block.size for block in self.memory_manager.memory_blocks 
            if not block.is_free
        )
        usage_percentage = (used_memory / total_memory) * 100
        
        frag_info = self.memory_manager.calculate_fragmentation()
        self.info_label.setText(
            f"Memory Usage: {usage_percentage:.1f}% | "
            f"External Fragmentation: {frag_info['fragmentation_percentage']:.1f}%"
        )
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB"""
        if s == 0.0:
            return v, v, v
        
        h = h * 6.0
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q


class PageTableVisualizer(QWidget):
    """Visualizes the page tables and frames"""
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.title_label = QLabel("Page Table Visualization")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        self.main_layout = QHBoxLayout()
        
        # Page tables visualization
        self.page_tables_widget = QWidget()
        self.page_tables_layout = QVBoxLayout()
        self.page_tables_widget.setLayout(self.page_tables_layout)
        self.page_tables_label = QLabel("Page Tables")
        self.page_tables_label.setAlignment(Qt.AlignCenter)
        self.page_tables_layout.addWidget(self.page_tables_label)
        self.page_tables_view = QGraphicsView()
        self.page_tables_scene = QGraphicsScene()
        self.page_tables_view.setScene(self.page_tables_scene)
        self.page_tables_layout.addWidget(self.page_tables_view)
        
        # Physical memory frames visualization
        self.frames_widget = QWidget()
        self.frames_layout = QVBoxLayout()
        self.frames_widget.setLayout(self.frames_layout)
        self.frames_label = QLabel("Physical Memory Frames")
        self.frames_label.setAlignment(Qt.AlignCenter)
        self.frames_layout.addWidget(self.frames_label)
        self.frames_view = QGraphicsView()
        self.frames_scene = QGraphicsScene()
        self.frames_view.setScene(self.frames_scene)
        self.frames_layout.addWidget(self.frames_view)
        
        self.main_layout.addWidget(self.page_tables_widget)
        self.main_layout.addWidget(self.frames_widget)
        
        self.layout.addLayout(self.main_layout)
        
        self.info_label = QLabel("Page Faults: 0")
        self.layout.addWidget(self.info_label)
        
        # Set up timer to update visualization
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(100)  # Update every 100ms
        
    def update_visualization(self):
        """Update the page table and frames visualization"""
        self.page_tables_scene.clear()
        self.frames_scene.clear()
        
        # Process color map for consistent coloring
        process_colors = {}
        
        # Draw page tables
        x_offset = 10
        y_offset = 10
        table_width = 180
        row_height = 30
        
        for process_id, page_table in self.memory_manager.page_tables.items():
            # Create a consistent color for the process
            if process_id not in process_colors:
                # Generate a random color for this process
                hue = random.random()
                saturation = 0.7 + random.random() * 0.3
                value = 0.7 + random.random() * 0.3
                r, g, b = self._hsv_to_rgb(hue, saturation, value)
                process_colors[process_id] = QColor(int(r*255), int(g*255), int(b*255))
            
            # Add process label
            proc_text = self.page_tables_scene.addText(f"Process {process_id}")
            proc_text.setPos(x_offset, y_offset)
            y_offset += 20
            
            # Add table headers
            header_text = self.page_tables_scene.addText("Page ID | Frame | Valid")
            header_text.setPos(x_offset, y_offset)
            y_offset += 20
            
            # Draw the page table entries
            for page_id, page in page_table.items():
                # Create table row
                rect = QGraphicsRectItem(x_offset, y_offset, table_width, row_height)
                rect.setBrush(QBrush(process_colors[process_id].lighter(130)))
                rect.setPen(QPen(Qt.black))
                self.page_tables_scene.addItem(rect)
                
                # Add text
                frame_text = str(page.frame_id) if page.frame_id is not None else "None"
                valid_text = "Yes" if page.is_valid else "No"
                text = f"{page_id} | {frame_text} | {valid_text}"
                text_item = self.page_tables_scene.addText(text)
                text_item.setPos(x_offset + 5, y_offset + 5)
                
                y_offset += row_height
            
            y_offset += 20
            
        self.page_tables_scene.setSceneRect(self.page_tables_scene.itemsBoundingRect())
        
        # Draw frames
        # Draw frames
        frame_size = 50
        cols = 4  # Number of columns in the frame grid
        x_pos = 10
        y_pos = 10
        
        for i in range(self.memory_manager.num_frames):
            # Calculate position
            col = i % cols
            row = i // cols
            frame_x = x_pos + col * (frame_size + 10)
            frame_y = y_pos + row * (frame_size + 10)
            Journal
            # Draw frame rectangle
            rect = QGraphicsRectItem(frame_x, frame_y, frame_size, frame_size)
            
            process_id = self.memory_manager.frames[i]
            if process_id is not None:
                # Frame is allocated
                if process_id not in process_colors:
                    # Generate a color for this process
                    hue = random.random()
                    saturation = 0.7 + random.random() * 0.3
                    value = 0.7 + random.random() * 0.3
                    r, g, b = self._hsv_to_rgb(hue, saturation, value)
                    process_colors[process_id] = QColor(int(r*255), int(g*255), int(b*255))
                
                rect.setBrush(QBrush(process_colors[process_id]))
                
                # Find which page is using this frame
                page_id = "?"
                for pid, page_table in self.memory_manager.page_tables.items():
                    if pid == process_id:
                        for page_id, page in page_table.items():
                            if page.frame_id == i:
                                page_id = page_id
                                break
                
                text = f"F{i}:P{process_id}\nPage {page_id}"
            else:
                # Frame is free
                rect.setBrush(QBrush(QColor(200, 200, 200)))
                text = f"F{i}\nFree"
            
            rect.setPen(QPen(Qt.black))
            self.frames_scene.addItem(rect)
            
            # Add text
            text_item = self.frames_scene.addText(text)
            text_rect = text_item.boundingRect()
            text_x = frame_x + (frame_size - text_rect.width()) / 2
            text_y = frame_y + (frame_size - text_rect.height()) / 2
            text_item.setPos(text_x, text_y)
        
        self.frames_scene.setSceneRect(self.frames_scene.itemsBoundingRect())
        
        # Count page faults
        page_faults = sum(
            1 for action in self.memory_manager.history
            if action.get("type") == "page_fault"
        )
        
        # Update info label
        self.info_label.setText(f"Page Faults: {page_faults}")
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB"""
        if s == 0.0:
            return v, v, v
        
        h = h * 6.0
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q


class SegmentationVisualizer(QWidget):
    """Visualizes the segmentation system"""
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.title_label = QLabel("Segmentation Visualization")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        self.main_layout = QHBoxLayout()
        
        # Segment tables visualization
        self.segment_tables_widget = QWidget()
        self.segment_tables_layout = QVBoxLayout()
        self.segment_tables_widget.setLayout(self.segment_tables_layout)
        self.segment_tables_label = QLabel("Segment Tables")
        self.segment_tables_label.setAlignment(Qt.AlignCenter)
        self.segment_tables_layout.addWidget(self.segment_tables_label)
        self.segment_tables_view = QGraphicsView()
        self.segment_tables_scene = QGraphicsScene()
        self.segment_tables_view.setScene(self.segment_tables_scene)
        self.segment_tables_layout.addWidget(self.segment_tables_view)
        
        # Physical memory visualization
        self.memory_widget = QWidget()
        self.memory_layout = QVBoxLayout()
        self.memory_widget.setLayout(self.memory_layout)
        self.memory_label = QLabel("Physical Memory")
        self.memory_label.setAlignment(Qt.AlignCenter)
        self.memory_layout.addWidget(self.memory_label)
        self.memory_view = QGraphicsView()
        self.memory_scene = QGraphicsScene()
        self.memory_view.setScene(self.memory_scene)
        self.memory_layout.addWidget(self.memory_view)
        
        self.main_layout.addWidget(self.segment_tables_widget)
        self.main_layout.addWidget(self.memory_widget)
        
        self.layout.addLayout(self.main_layout)
        
        self.info_label = QLabel("Segmentation Faults: 0")
        self.layout.addWidget(self.info_label)
        
        # Set up timer to update visualization
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(100)  # Update every 100ms
        
    def update_visualization(self):
        """Update the segmentation visualization"""
        self.segment_tables_scene.clear()
        self.memory_scene.clear()
        
        # Process color map for consistent coloring
        process_colors = {}
        
        # Draw segment tables
        x_offset = 10
        y_offset = 10
        table_width = 180
        row_height = 30
        
        for process_id, segment_table in self.memory_manager.segment_tables.items():
            # Create a consistent color for the process
            if process_id not in process_colors:
                # Generate a random color for this process
                hue = random.random()
                saturation = 0.7 + random.random() * 0.3
                value = 0.7 + random.random() * 0.3
                r, g, b = self._hsv_to_rgb(hue, saturation, value)
                process_colors[process_id] = QColor(int(r*255), int(g*255), int(b*255))
            
            # Add process label
            proc_text = self.segment_tables_scene.addText(f"Process {process_id}")
            proc_text.setPos(x_offset, y_offset)
            y_offset += 20
            
            # Add table headers
            header_text = self.segment_tables_scene.addText("Segment ID | Base | Limit | Valid")
            header_text.setPos(x_offset, y_offset)
            y_offset += 20
            
            # Draw the segment table entries
            for segment_id, segment in segment_table.items():
                # Create table row
                rect = QGraphicsRectItem(x_offset, y_offset, table_width, row_height)
                rect.setBrush(QBrush(process_colors[process_id].lighter(130)))
                rect.setPen(QPen(Qt.black))
                self.segment_tables_scene.addItem(rect)
                
                # Add text
                base_text = str(segment.base) if segment.base is not None else "None"
                limit_text = str(segment.limit) if segment.limit is not None else "None"
                valid_text = "Yes" if segment.is_valid else "No"
                text = f"{segment_id} | {base_text} | {limit_text} | {valid_text}"
                text_item = self.segment_tables_scene.addText(text)
                text_item.setPos(x_offset + 5, y_offset + 5)
                
                y_offset += row_height
            
            y_offset += 20
            
        self.segment_tables_scene.setSceneRect(self.segment_tables_scene.itemsBoundingRect())
        
        # Draw physical memory for segmentation
        total_memory = self.memory_manager.total_memory_size
        view_width = self.memory_view.width() - 20
        memory_height = 300
        x_pos = 10
        y_pos = 10
        
        # Draw the full memory rectangle
        memory_rect = QGraphicsRectItem(x_pos, y_pos, view_width, memory_height)
        memory_rect.setBrush(QBrush(QColor(240, 240, 240)))
        memory_rect.setPen(QPen(Qt.black))
        self.memory_scene.addItem(memory_rect)
        
        # Draw segment allocations
        for process_id, segment_table in self.memory_manager.segment_tables.items():
            if process_id not in process_colors:
                continue
                
            for segment_id, segment in segment_table.items():
                if not segment.is_valid or segment.base is None:
                    continue
                
                # Calculate position and size
                segment_x = x_pos + (segment.base / total_memory) * view_width
                segment_width = (segment.limit / total_memory) * view_width
                
                # Draw segment rectangle
                segment_rect = QGraphicsRectItem(segment_x, y_pos, segment_width, memory_height)
                segment_rect.setBrush(QBrush(process_colors[process_id]))
                segment_rect.setPen(QPen(Qt.black))
                self.memory_scene.addItem(segment_rect)
                
                # Add label
                label_text = f"P{process_id}:S{segment_id}"
                label_item = self.memory_scene.addText(label_text)
                label_item.setPos(
                    segment_x + (segment_width - label_item.boundingRect().width()) / 2,
                    y_pos + memory_height / 2 - label_item.boundingRect().height() / 2
                )
        
        # Add memory address markers
        for i in range(0, total_memory + 1, total_memory // 10):
            x = x_pos + (i / total_memory) * view_width
            marker_line = self.memory_scene.addLine(x, y_pos + memory_height, x, y_pos + memory_height + 10)
            
            text_item = self.memory_scene.addText(str(i))
            text_item.setPos(x - text_item.boundingRect().width() / 2, y_pos + memory_height + 10)
        
        self.memory_scene.setSceneRect(self.memory_scene.itemsBoundingRect())
        
        # Count segmentation faults
        seg_faults = sum(
            1 for action in self.memory_manager.history
            if action.get("type") == "segmentation_fault"
        )
        
        # Update info label
        self.info_label.setText(f"Segmentation Faults: {seg_faults}")
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB"""
        if s == 0.0:
            return v, v, v
        
        h = h * 6.0
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q


class MetricsVisualizer(QWidget):
    """Visualizes performance metrics for memory management"""
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.history_data = {
            'time': [],
            'page_faults': [],
            'memory_usage': [],
            'fragmentation': []
        }
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.title_label = QLabel("Performance Metrics")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        # Create matplotlib figure for metrics
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Initialize subplots
        self.ax1 = self.figure.add_subplot(211)  # Page faults
        self.ax2 = self.figure.add_subplot(212)  # Memory usage and fragmentation
        
        # Set up timer to update visualization
        self.update_counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.timer.start(500)  # Update every 500ms
        
    def update_visualization(self):
        """Update the metrics visualization"""
        self.update_counter += 1
        
        # Count page faults
        page_faults = sum(
            1 for action in self.memory_manager.history
            if action.get("type") == "page_fault"
        )
        
        # Calculate memory usage
        used_memory = sum(
            block.size for block in self.memory_manager.memory_blocks 
            if not block.is_free
        )
        memory_usage = (used_memory / self.memory_manager.total_memory_size) * 100
        
        # Calculate fragmentation
        frag_info = self.memory_manager.calculate_fragmentation()
        
        # Update history data
        self.history_data['time'].append(self.update_counter)
        self.history_data['page_faults'].append(page_faults)
        self.history_data['memory_usage'].append(memory_usage)
        self.history_data['fragmentation'].append(frag_info['fragmentation_percentage'])
        
        # Keep a maximum of 50 data points
        if len(self.history_data['time']) > 50:
            for key in self.history_data:
                self.history_data[key] = self.history_data[key][-50:]
        
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot page faults
        self.ax1.plot(
            self.history_data['time'], 
            self.history_data['page_faults'], 
            'r-', 
            label='Page Faults'
        )
        self.ax1.set_ylabel('Page Faults')
        self.ax1.legend(loc='upper left')
        self.ax1.set_title('Page Fault Count')
        
        # Plot memory usage and fragmentation
        self.ax2.plot(
            self.history_data['time'], 
            self.history_data['memory_usage'], 
            'b-', 
            label='Memory Usage %'
        )
        self.ax2.plot(
            self.history_data['time'], 
            self.history_data['fragmentation'], 
            'g-', 
            label='Fragmentation %'
        )
        self.ax2.set_ylabel('Percentage')
        self.ax2.set_xlabel('Time')
        self.ax2.legend(loc='upper left')
        self.ax2.set_title('Memory Usage and Fragmentation')
        
        # Adjust layout and draw
        self.figure.tight_layout()
        self.canvas.draw()
"""
User Interface Components for Memory Management Visualization Tool
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QTabWidget, QSpinBox, 
                            QLineEdit, QGroupBox, QFormLayout, QRadioButton,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QSplitter, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ControlPanel(QWidget):
    """Control panel for memory management operations"""
    # Define signals
    memory_reset = pyqtSignal()
    memory_allocate = pyqtSignal(int, int)  # process_id, size
    memory_deallocate = pyqtSignal(int)  # process_id
    algorithm_changed = pyqtSignal(str)  # algorithm name
    allocate_pages = pyqtSignal(int, int)  # process_id, num_pages
    access_page = pyqtSignal(int, int, str)  # process_id, page_id, replacement_algo
    create_segment = pyqtSignal(int, int, int)  # process_id, segment_id, size
    access_segment = pyqtSignal(int, int, int)  # process_id, segment_id, offset
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Memory Configuration
        self.config_group = QGroupBox("Memory Configuration")
        self.config_layout = QFormLayout()
        self.config_group.setLayout(self.config_layout)
        
        # Memory size selector
        self.memory_size_label = QLabel("Total Memory Size:")
        self.memory_size_input = QSpinBox()
        self.memory_size_input.setRange(64, 4096)
        self.memory_size_input.setValue(1024)
        self.memory_size_input.setSingleStep(64)
        self.memory_size_input.setSuffix(" KB")
        self.config_layout.addRow(self.memory_size_label, self.memory_size_input)
        
        # Page size selector
        self.page_size_label = QLabel("Page Size:")
        self.page_size_input = QComboBox()
        self.page_size_input.addItems(["4 KB", "8 KB", "16 KB", "32 KB"])
        self.config_layout.addRow(self.page_size_label, self.page_size_input)
        
        # Reset button
        self.reset_button = QPushButton("Reset Memory")
        self.reset_button.clicked.connect(self.on_reset)
        self.config_layout.addRow("", self.reset_button)
        
        self.layout.addWidget(self.config_group)
        
        # Memory Allocation
        self.allocation_group = QGroupBox("Memory Allocation")
        self.allocation_layout = QFormLayout()
        self.allocation_group.setLayout(self.allocation_layout)
        
        # Algorithm selector
        self.algorithm_label = QLabel("Allocation Algorithm:")
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["First-Fit", "Best-Fit", "Worst-Fit"])
        self.algorithm_selector.currentTextChanged.connect(self.on_algorithm_changed)
        self.allocation_layout.addRow(self.algorithm_label, self.algorithm_selector)
        
        # Process ID input
        self.process_id_label = QLabel("Process ID:")
        self.process_id_input = QSpinBox()
        self.process_id_input.setRange(1, 100)
        self.allocation_layout.addRow(self.process_id_label, self.process_id_input)
        
        # Memory size input
        self.alloc_size_label = QLabel("Memory Size:")
        self.alloc_size_input = QSpinBox()
        self.alloc_size_input.setRange(1, 1024)
        self.alloc_size_input.setValue(64)
        self.alloc_size_input.setSuffix(" KB")
        self.allocation_layout.addRow(self.alloc_size_label, self.alloc_size_input)
        
        # Allocate button
        self.allocate_button = QPushButton("Allocate Memory")
        self.allocate_button.clicked.connect(self.on_allocate)
        self.allocation_layout.addRow("", self.allocate_button)
        
        # Deallocate button
        self.deallocate_button = QPushButton("Deallocate Memory")
        self.deallocate_button.clicked.connect(self.on_deallocate)
        self.allocation_layout.addRow("", self.deallocate_button)
        
        self.layout.addWidget(self.allocation_group)
        
        # Paging Control
        self.paging_group = QGroupBox("Paging Control")
        self.paging_layout = QFormLayout()
        self.paging_group.setLayout(self.paging_layout)
        
        # Process ID for paging
        self.page_process_id_label = QLabel("Process ID:")
        self.page_process_id_input = QSpinBox()
        self.page_process_id_input.setRange(1, 100)
        self.paging_layout.addRow(self.page_process_id_label, self.page_process_id_input)
        
        # Number of pages
        self.num_pages_label = QLabel("Number of Pages:")
        self.num_pages_input = QSpinBox()
        self.num_pages_input.setRange(1, 50)
        self.num_pages_input.setValue(4)
        self.paging_layout.addRow(self.num_pages_label, self.num_pages_input)
        
        # Allocate pages button
        self.allocate_pages_button = QPushButton("Allocate Pages")
        self.allocate_pages_button.clicked.connect(self.on_allocate_pages)
        self.paging_layout.addRow("", self.allocate_pages_button)
        
        # Page access
        self.page_id_label = QLabel("Page ID:")
        self.page_id_input = QSpinBox()
        self.page_id_input.setRange(0, 49)
        self.paging_layout.addRow(self.page_id_label, self.page_id_input)
        
        # Page replacement algorithm
        self.replacement_algo_label = QLabel("Replacement Algorithm:")
        self.replacement_algo_selector = QComboBox()
        self.replacement_algo_selector.addItems(["FIFO", "LRU"])
        self.paging_layout.addRow(self.replacement_algo_label, self.replacement_algo_selector)
        
        # Access page button
        self.access_page_button = QPushButton("Access Page")
        self.access_page_button.clicked.connect(self.on_access_page)
        self.paging_layout.addRow("", self.access_page_button)
        
        self.layout.addWidget(self.paging_group)
        
        # Segmentation Control
        self.segmentation_group = QGroupBox("Segmentation Control")
        self.segmentation_layout = QFormLayout()
        self.segmentation_group.setLayout(self.segmentation_layout)
        
        # Process ID for segmentation
        self.seg_process_id_label = QLabel("Process ID:")
        self.seg_process_id_input = QSpinBox()
        self.seg_process_id_input.setRange(1, 100)
        self.segmentation_layout.addRow(self.seg_process_id_label, self.seg_process_id_input)
        
        # Segment ID
        self.segment_id_label = QLabel("Segment ID:")
        self.segment_id_input = QSpinBox()
        self.segment_id_input.setRange(0, 9)
        self.segmentation_layout.addRow(self.segment_id_label, self.segment_id_input)
        
        # Segment size
        self.segment_size_label = QLabel("Segment Size:")
        self.segment_size_input = QSpinBox()
        self.segment_size_input.setRange(1, 512)
        self.segment_size_input.setValue(64)
        self.segment_size_input.setSuffix(" KB")
        self.segmentation_layout.addRow(self.segment_size_label, self.segment_size_input)
        
        # Create segment button
        self.create_segment_button = QPushButton("Create Segment")
        self.create_segment_button.clicked.connect(self.on_create_segment)
        self.segmentation_layout.addRow("", self.create_segment_button)
        
        # Segment access
        self.offset_label = QLabel("Offset:")
        self.offset_input = QSpinBox()
        self.offset_input.setRange(0, 511)
        self.segmentation_layout.addRow(self.offset_label, self.offset_input)
        
        # Access segment button
        self.access_segment_button = QPushButton("Access Segment")
        self.access_segment_button.clicked.connect(self.on_access_segment)
        self.segmentation_layout.addRow("", self.access_segment_button)
        
        self.layout.addWidget(self.segmentation_group)
        
        # Event log
        self.log_group = QGroupBox("Event Log")
        self.log_layout = QVBoxLayout()
        self.log_group.setLayout(self.log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_layout.addWidget(self.log_text)
        
        self.layout.addWidget(self.log_group)
    
    def on_reset(self):
        """Handle reset button click"""
        self.memory_reset.emit()
        self.log_message("Memory reset")
    
    def on_algorithm_changed(self, algorithm):
        """Handle algorithm selection change"""
        algo_map = {
            "First-Fit": "first_fit",
            "Best-Fit": "best_fit",
            "Worst-Fit": "worst_fit"
        }
        self.algorithm_changed.emit(algo_map[algorithm])
        self.log_message(f"Allocation algorithm changed to {algorithm}")
    
    def on_allocate(self):
        """Handle memory allocation"""
        process_id = self.process_id_input.value()
        size = self.alloc_size_input.value()
        self.memory_allocate.emit(process_id, size)
        self.log_message(f"Requesting memory allocation for Process {process_id}, Size {size} KB")
    
    def on_deallocate(self):
        """Handle memory deallocation"""
        process_id = self.process_id_input.value()
        self.memory_deallocate.emit(process_id)
        self.log_message(f"Requesting memory deallocation for Process {process_id}")
    
    def on_allocate_pages(self):
        """Handle page allocation"""
        process_id = self.page_process_id_input.value()
        num_pages = self.num_pages_input.value()
        self.allocate_pages.emit(process_id, num_pages)
        self.log_message(f"Requesting page allocation for Process {process_id}, {num_pages} pages")
    
    def on_access_page(self):
        """Handle page access"""
        process_id = self.page_process_id_input.value()
        page_id = self.page_id_input.value()
        replacement_algo = self.replacement_algo_selector.currentText()
        self.access_page.emit(process_id, page_id, replacement_algo)
        self.log_message(f"Accessing Page {page_id} for Process {process_id} using {replacement_algo}")
    
    def on_create_segment(self):
        """Handle segment creation"""
        process_id = self.seg_process_id_input.value()
        segment_id = self.segment_id_input.value()
        size = self.segment_size_input.value()
        self.create_segment.emit(process_id, segment_id, size)
        self.log_message(f"Creating Segment {segment_id} for Process {process_id}, Size {size} KB")
    
    def on_access_segment(self):
        """Handle segment access"""
        process_id = self.seg_process_id_input.value()
        segment_id = self.segment_id_input.value()
        offset = self.offset_input.value()
        self.access_segment.emit(process_id, segment_id, offset)
        self.log_message(f"Accessing Segment {segment_id} at offset {offset} for Process {process_id}")
    
    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.append(message)
    
    def get_memory_size(self):
        """Get the configured memory size"""
        return self.memory_size_input.value()
    
    def get_page_size(self):
        """Get the configured page size"""
        text = self.page_size_input.currentText()
        return int(text.split()[0])  # Extract the number from "X KB"


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer

class EventLogWidget(QWidget):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Memory Management Events")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)

        self.event_table = QTableWidget(0, 4)
        self.event_table.setHorizontalHeaderLabels(["Time", "Type", "Process ID", "Details"])
        self.event_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.event_table.setAlternatingRowColors(True)
        self.event_table.setToolTip("History of memory management events")
        self.layout.addWidget(self.event_table)

        # Timer for updating the table
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_event_table)
        self.timer.start(100)

    def update_event_table(self):
        if not self.isVisible():
            return
        self.event_table.setRowCount(0)
        for idx, action in enumerate(self.memory_manager.history):
            row = self.event_table.rowCount()
            self.event_table.insertRow(row)
            self.event_table.setItem(row, 0, QTableWidgetItem(str(idx)))
            self.event_table.setItem(row, 1, QTableWidgetItem(action.get("type", "")))
            self.event_table.setItem(row, 2, QTableWidgetItem(str(action.get("process_id", ""))))
            details = action.get("message", "")
            if action.get("type") == "allocation":
                details = f"Size: {action.get('size')} KB, Start: {action.get('block_start')}"
            elif action.get("type") == "page_fault":
                details = f"Page {action.get('page_id')} not in memory"
            elif action.get("type") == "segmentation_fault":
                details = f"Offset {action.get('offset')} exceeds limit {action.get('limit')}"
            self.event_table.setItem(row, 3, QTableWidgetItem(details))
        self.event_table.resizeColumnsToContents()