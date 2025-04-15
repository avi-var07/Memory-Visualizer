import pytest
from memory_management import MemoryManager
from control_panel import ControlPanel
from PyQt5.QtWidgets import QApplication
import sys

@pytest.fixture
def app():
    return QApplication(sys.argv)

@pytest.fixture
def memory_manager():
    return MemoryManager(total_memory_size=1024, page_size=16)

@pytest.fixture
def control_panel(app):
    return ControlPanel()

def test_allocation(memory_manager, control_panel):
    control_panel.process_id_input.setValue(1)
    control_panel.alloc_size_input.setValue(100)
    control_panel.on_allocate()
    assert any(block.process_id == 1 and block.size == 100 for block in memory_manager.memory_blocks)

def test_page_fault(memory_manager, control_panel):
    control_panel.page_process_id_input.setValue(2)
    control_panel.num_pages_input.setValue(4)
    control_panel.on_allocate_pages()
    control_panel.page_id_input.setValue(5)
    control_panel.on_access_page()
    assert any(action["type"] == "page_fault" for action in memory_manager.history)

def test_segmentation_fault(memory_manager, control_panel):
    control_panel.seg_process_id_input.setValue(3)
    control_panel.segment_id_input.setValue(0)
    control_panel.segment_size_input.setValue(64)
    control_panel.on_create_segment()
    control_panel.offset_input.setValue(100)
    control_panel.on_access_segment()
    assert any(action["type"] == "segmentation_fault" for action in memory_manager.history)