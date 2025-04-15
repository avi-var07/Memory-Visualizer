from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer
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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer

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