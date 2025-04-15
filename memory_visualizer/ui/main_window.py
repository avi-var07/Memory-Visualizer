from PyQt5.QtWidgets import QMainWindow, QTabWidget, QSplitter, QStatusBar, QMessageBox, QAction
from PyQt5.QtCore import Qt
from memory_management import MemoryManager
from control_panel import ControlPanel
from visualizers import MemoryBlockVisualizer, PageTableVisualizer, SegmentationVisualizer, MetricsVisualizer, EventLogWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.control_panel = ControlPanel()
        self.memory_manager = MemoryManager(
            total_memory_size=self.control_panel.get_memory_size(),
            page_size=self.control_panel.get_page_size()
        )
        self.setWindowTitle("Memory Management Visualizer")
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        central_widget = QSplitter(Qt.Horizontal)
        self.setCentralWidget(central_widget)

        central_widget.addWidget(self.control_panel)

        self.tabs = QTabWidget()
        self.memory_block_vis = MemoryBlockVisualizer(self.memory_manager)
        self.page_table_vis = PageTableVisualizer(self.memory_manager)
        self.segmentation_vis = SegmentationVisualizer(self.memory_manager)
        self.metrics_vis = MetricsVisualizer(self.memory_manager)
        self.event_log = EventLogWidget(self.memory_manager)

        self.tabs.addTab(self.memory_block_vis, "Contiguous Allocation")
        self.tabs.addTab(self.page_table_vis, "Paging")
        self.tabs.addTab(self.segmentation_vis, "Segmentation")
        self.tabs.addTab(self.metrics_vis, "Metrics")
        self.tabs.addTab(self.event_log, "Event Log")

        central_widget.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 5000)

        help_menu = self.menuBar().addMenu("Help")
        concepts_action = QAction("Memory Concepts", self)
        concepts_action.triggered.connect(self.show_help)
        help_menu.addAction(concepts_action)

    def connect_signals(self):
        self.control_panel.memory_reset.connect(self.memory_manager.reset)
        self.control_panel.memory_reset.connect(lambda: self.status_bar.showMessage("Memory reset", 5000))
        self.control_panel.memory_allocate.connect(self.memory_manager.allocate_memory)
        self.control_panel.memory_allocate.connect(self.on_allocation_triggered)
        self.control_panel.memory_deallocate.connect(self.memory_manager.deallocate_memory)
        self.control_panel.memory_deallocate.connect(self.on_deallocation_triggered)
        self.control_panel.algorithm_changed.connect(self.memory_manager.set_algorithm)
        self.control_panel.algorithm_changed.connect(lambda algo: self.status_bar.showMessage(f"Algorithm changed to {algo}", 5000))
        self.control_panel.allocate_pages.connect(self.memory_manager.allocate_pages)
        self.control_panel.allocate_pages.connect(self.on_pages_allocated)
        self.control_panel.access_page.connect(self.memory_manager.access_page)
        self.control_panel.access_page.connect(self.on_page_accessed)
        self.control_panel.create_segment.connect(self.memory_manager.create_segment)
        self.control_panel.create_segment.connect(self.on_segment_created)
        self.control_panel.access_segment.connect(self.memory_manager.access_segment)
        self.control_panel.access_segment.connect(self.on_segment_accessed)
        self.control_panel.simulate_thrashing.connect(self.simulate_thrashing)

    def on_allocation_triggered(self, process_id, size):
        self.status_bar.showMessage(f"Allocated {size} KB for Process {process_id}", 5000)
        self.check_for_errors()

    def on_deallocation_triggered(self, process_id):
        self.status_bar.showMessage(f"Deallocated memory for Process {process_id}", 5000)
        self.check_for_errors()

    def on_pages_allocated(self, process_id, num_pages):
        self.status_bar.showMessage(f"Allocated {num_pages} pages for Process {process_id}", 5000)
        self.check_for_errors()

    def on_page_accessed(self, process_id, page_id, algo):
        self.status_bar.showMessage(f"Accessed Page {page_id} for Process {process_id} using {algo}", 5000)
        self.check_for_errors()

    def on_segment_created(self, process_id, segment_id, size):
        self.status_bar.showMessage(f"Created Segment {segment_id} for Process {process_id} with {size} KB", 5000)
        self.check_for_errors()

    def on_segment_accessed(self, process_id, segment_id, offset):
        self.status_bar.showMessage(f"Accessed Segment {segment_id} at offset {offset} for Process {process_id}", 5000)
        self.check_for_errors()

    def simulate_thrashing(self, process_id, num_accesses):
        import random
        for _ in range(num_accesses):
            page_id = random.randint(0, 9)
            self.memory_manager.access_page(process_id, page_id, "LRU")
        self.status_bar.showMessage(f"Simulated thrashing for Process {process_id}", 5000)
        self.check_for_errors()

    def check_for_errors(self):
        if self.memory_manager.history:
            last_action = self.memory_manager.history[-1]
            if last_action.get("type") in ["error", "page_fault", "segmentation_fault", "allocation_failure"]:
                QMessageBox.critical(self, "Memory Event", last_action.get("message", "An error occurred"))

    def show_help(self):
        QMessageBox.information(self, "Memory Concepts",
            "Page Fault: Occurs when a requested page is not in memory and must be loaded.\n"
            "Fragmentation: Scattered free memory that cannot be allocated efficiently.\n"
            "Segmentation Fault: Occurs when accessing an invalid memory address in a segment.\n"
            "First-Fit: Allocates the first free block that is large enough.\n"
            "Best-Fit: Allocates the smallest free block that is large enough.\n"
            "Worst-Fit: Allocates the largest free block available.")