from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, 
                             QSpinBox, QComboBox, QPushButton, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class ControlPanel(QWidget):
    memory_reset = pyqtSignal()
    memory_allocate = pyqtSignal(int, int)
    memory_deallocate = pyqtSignal(int)
    algorithm_changed = pyqtSignal(str)
    allocate_pages = pyqtSignal(int, int)
    access_page = pyqtSignal(int, int, str)
    create_segment = pyqtSignal(int, int, int)
    access_segment = pyqtSignal(int, int, int)
    simulate_thrashing = pyqtSignal(int, int)

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

        self.memory_size_label = QLabel("Total Memory Size:")
        self.memory_size_input = QSpinBox()
        self.memory_size_input.setRange(64, 4096)
        self.memory_size_input.setValue(1024)
        self.memory_size_input.setSingleStep(64)
        self.memory_size_input.setSuffix(" KB")
        self.memory_size_input.setToolTip("Total memory available for allocation (64-4096 KB)")
        self.config_layout.addRow(self.memory_size_label, self.memory_size_input)

        self.page_size_label = QLabel("Page Size:")
        self.page_size_input = QComboBox()
        self.page_size_input.addItems(["4 KB", "8 KB", "16 KB", "32 KB"])
        self.page_size_input.setToolTip("Size of each page in the paging system")
        self.config_layout.addRow(self.page_size_label, self.page_size_input)

        self.reset_button = QPushButton("Reset Memory")
        self.reset_button.setToolTip("Reset all memory to initial state")
        self.reset_button.clicked.connect(self.on_reset)
        self.config_layout.addRow("", self.reset_button)

        self.layout.addWidget(self.config_group)

        # Memory Allocation
        self.allocation_group = QGroupBox("Memory Allocation")
        self.allocation_layout = QFormLayout()
        self.allocation_group.setLayout(self.allocation_layout)

        self.algorithm_label = QLabel("Allocation Algorithm:")
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["First-Fit", "Best-Fit", "Worst-Fit"])
        self.algorithm_selector.setToolTip("Choose the memory allocation strategy")
        self.algorithm_selector.currentTextChanged.connect(self.on_algorithm_changed)
        self.allocation_layout.addRow(self.algorithm_label, self.algorithm_selector)

        self.process_id_label = QLabel("Process ID:")
        self.process_id_input = QSpinBox()
        self.process_id_input.setRange(1, 100)
        self.process_id_input.setToolTip("Unique ID for the process (1-100)")
        self.allocation_layout.addRow(self.process_id_label, self.process_id_input)

        self.alloc_size_label = QLabel("Memory Size:")
        self.alloc_size_input = QSpinBox()
        self.alloc_size_input.setRange(1, 1024)
        self.alloc_size_input.setValue(64)
        self.alloc_size_input.setSuffix(" KB")
        self.alloc_size_input.setToolTip("Size of memory to allocate (1-1024 KB)")
        self.allocation_layout.addRow(self.alloc_size_label, self.alloc_size_input)

        self.allocate_button = QPushButton("Allocate Memory")
        self.allocate_button.setToolTip("Allocate memory for the specified process")
        self.allocate_button.clicked.connect(self.on_allocate)
        self.allocation_layout.addRow("", self.allocate_button)

        self.deallocate_button = QPushButton("Deallocate Memory")
        self.deallocate_button.setToolTip("Free memory allocated to the specified process")
        self.deallocate_button.clicked.connect(self.on_deallocate)
        self.allocation_layout.addRow("", self.deallocate_button)

        self.layout.addWidget(self.allocation_group)

        # Paging Control
        self.paging_group = QGroupBox("Paging Control")
        self.paging_layout = QFormLayout()
        self.paging_group.setLayout(self.paging_layout)

        self.page_process_id_label = QLabel("Process ID:")
        self.page_process_id_input = QSpinBox()
        self.page_process_id_input.setRange(1, 100)
        self.page_process_id_input.setToolTip("Process ID for page allocation")
        self.paging_layout.addRow(self.page_process_id_label, self.page_process_id_input)

        self.num_pages_label = QLabel("Number of Pages:")
        self.num_pages_input = QSpinBox()
        self.num_pages_input.setRange(1, 50)
        self.num_pages_input.setValue(4)
        self.num_pages_input.setToolTip("Number of pages to allocate")
        self.paging_layout.addRow(self.num_pages_label, self.num_pages_input)

        self.allocate_pages_button = QPushButton("Allocate Pages")
        self.allocate_pages_button.setToolTip("Allocate pages to the specified process")
        self.allocate_pages_button.clicked.connect(self.on_allocate_pages)
        self.paging_layout.addRow("", self.allocate_pages_button)

        self.page_id_label = QLabel("Page ID:")
        self.page_id_input = QSpinBox()
        self.page_id_input.setRange(0, 49)
        self.page_id_input.setToolTip("ID of the page to access")
        self.paging_layout.addRow(self.page_id_label, self.page_id_input)

        self.replacement_algo_label = QLabel("Replacement Algorithm:")
        self.replacement_algo_selector = QComboBox()
        self.replacement_algo_selector.addItems(["FIFO", "LRU"])
        self.replacement_algo_selector.setToolTip("Page replacement strategy")
        self.paging_layout.addRow(self.replacement_algo_label, self.replacement_algo_selector)

        self.access_page_button = QPushButton("Access Page")
        self.access_page_button.setToolTip("Access the specified page")
        self.access_page_button.clicked.connect(self.on_access_page)
        self.paging_layout.addRow("", self.access_page_button)

        self.thrashing_button = QPushButton("Simulate Thrashing")
        self.thrashing_button.setToolTip("Simulate rapid page accesses to trigger page faults")
        self.thrashing_button.clicked.connect(self.on_simulate_thrashing)
        self.paging_layout.addRow("", self.thrashing_button)

        self.layout.addWidget(self.paging_group)

        # Segmentation Control
        self.segmentation_group = QGroupBox("Segmentation Control")
        self.segmentation_layout = QFormLayout()
        self.segmentation_group.setLayout(self.segmentation_layout)

        self.seg_process_id_label = QLabel("Process ID:")
        self.seg_process_id_input = QSpinBox()
        self.seg_process_id_input.setRange(1, 100)
        self.seg_process_id_input.setToolTip("Process ID for segment creation")
        self.segmentation_layout.addRow(self.seg_process_id_label, self.seg_process_id_input)

        self.segment_id_label = QLabel("Segment ID:")
        self.segment_id_input = QSpinBox()
        self.segment_id_input.setRange(0, 9)
        self.segment_id_input.setToolTip("ID of the segment to create or access")
        self.segmentation_layout.addRow(self.segment_id_label, self.segment_id_input)

        self.segment_size_label = QLabel("Segment Size:")
        self.segment_size_input = QSpinBox()
        self.segment_size_input.setRange(1, 512)
        self.segment_size_input.setValue(64)
        self.segment_size_input.setSuffix(" KB")
        self.segment_size_input.setToolTip("Size of the segment")
        self.segmentation_layout.addRow(self.segment_size_label, self.segment_size_input)

        self.create_segment_button = QPushButton("Create Segment")
        self.create_segment_button.setToolTip("Create a new segment")
        self.create_segment_button.clicked.connect(self.on_create_segment)
        self.segmentation_layout.addRow("", self.create_segment_button)

        self.offset_label = QLabel("Offset:")
        self.offset_input = QSpinBox()
        self.offset_input.setRange(0, 511)
        self.offset_input.setToolTip("Offset within the segment to access")
        self.segmentation_layout.addRow(self.offset_label, self.offset_input)

        self.access_segment_button = QPushButton("Access Segment")
        self.access_segment_button.setToolTip("Access memory at the specified offset")
        self.access_segment_button.clicked.connect(self.on_access_segment)
        self.segmentation_layout.addRow("", self.access_segment_button)

        self.layout.addWidget(self.segmentation_group)

        # Event Log
        self.log_group = QGroupBox("Event Log")
        self.log_layout = QVBoxLayout()
        self.log_group.setLayout(self.log_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setToolTip("Log of memory management events")
        self.log_layout.addWidget(self.log_text)

        self.layout.addWidget(self.log_group)

        # Connect config changes (after all widgets are defined)
        self.memory_size_input.valueChanged.connect(self.on_config_changed)
        self.page_size_input.currentIndexChanged.connect(self.on_config_changed)

    def on_reset(self):
        if QMessageBox.question(self, "Confirm Reset", "Reset all memory?") == QMessageBox.Yes:
            self.memory_reset.emit()
            self.log_message("Memory reset")

    def on_algorithm_changed(self, algorithm):
        algo_map = {"First-Fit": "first_fit", "Best-Fit": "best_fit", "Worst-Fit": "worst_fit"}
        self.algorithm_changed.emit(algo_map[algorithm])
        self.log_message(f"Allocation algorithm changed to {algorithm}")

    def on_allocate(self):
        process_id = self.process_id_input.value()
        size = self.alloc_size_input.value()
        if size > self.memory_size_input.value():
            QMessageBox.warning(self, "Invalid Input", "Allocation size exceeds total memory!")
            return
        self.memory_allocate.emit(process_id, size)
        self.log_message(f"Requesting memory allocation for Process {process_id}, Size {size} KB")

    def on_deallocate(self):
        process_id = self.process_id_input.value()
        self.memory_deallocate.emit(process_id)
        self.log_message(f"Requesting memory deallocation for Process {process_id}")

    def on_allocate_pages(self):
        process_id = self.page_process_id_input.value()
        num_pages = self.num_pages_input.value()
        self.allocate_pages.emit(process_id, num_pages)
        self.log_message(f"Requesting page allocation for Process {process_id}, {num_pages} pages")

    def on_access_page(self):
        process_id = self.page_process_id_input.value()
        page_id = self.page_id_input.value()
        replacement_algo = self.replacement_algo_selector.currentText()
        self.access_page.emit(process_id, page_id, replacement_algo)
        self.log_message(f"Accessing Page {page_id} for Process {process_id} using {replacement_algo}")

    def on_create_segment(self):
        process_id = self.seg_process_id_input.value()
        segment_id = self.segment_id_input.value()
        size = self.segment_size_input.value()
        if size > self.memory_size_input.value():
            QMessageBox.warning(self, "Invalid Input", "Segment size exceeds total memory!")
            return
        self.create_segment.emit(process_id, segment_id, size)
        self.log_message(f"Creating Segment {segment_id} for Process {process_id}, Size {size} KB")

    def on_access_segment(self):
        process_id = self.seg_process_id_input.value()
        segment_id = self.segment_id_input.value()
        offset = self.offset_input.value()
        self.access_segment.emit(process_id, segment_id, offset)
        self.log_message(f"Accessing Segment {segment_id} at offset {offset} for Process {process_id}")

    def on_simulate_thrashing(self):
        process_id = self.page_process_id_input.value()
        self.simulate_thrashing.emit(process_id, 10)
        self.log_message(f"Simulating thrashing for Process {process_id}")

    def on_config_changed(self):
        self.memory_reset.emit()

    def log_message(self, message):
        self.log_text.append(message)

    def get_memory_size(self):
        return self.memory_size_input.value()

    def get_page_size(self):
        text = self.page_size_input.currentText()
        return int(text.split()[0])