import pytest
from memory_management import MemoryManager

@pytest.fixture
def mm():
    return MemoryManager(total_memory_size=1024)

def test_first_fit(mm):
    mm.set_algorithm("first_fit")
    mm.allocate_memory(1, 100)
    mm.allocate_memory(2, 200)
    assert mm.memory_blocks[0].process_id == 1
    assert mm.memory_blocks[1].process_id == 2

def test_best_fit(mm):
    mm.set_algorithm("best_fit")
    mm.allocate_memory(1, 100)
    mm.deallocate_memory(1)
    mm.allocate_memory(2, 50)
    mm.allocate_memory(3, 50)
    assert any(block.size == 50 and block.process_id == 2 for block in mm.memory_blocks)

def test_fifo_replacement(mm):
    mm.allocate_pages(1, 5)
    mm.frames = [1] * mm.num_frames  # Fill frames
    mm.access_page(1, 4, "FIFO")
    assert any(action["type"] == "page_replacement" and action["algorithm"] == "FIFO" for action in mm.history)

def test_lru_replacement(mm):
    mm.allocate_pages(1, 5)
    mm.frames = [1] * mm.num_frames
    mm.access_page(1, 0, "LRU")
    mm.access_page(1, 1, "LRU")
    mm.access_page(1, 4, "LRU")
    assert any(action["type"] == "page_replacement" and action["algorithm"] == "LRU" for action in mm.history)