# Memory-Visualizer
# Dynamic Memory Management Visualizer
Simulates paging with FIFO and LRU algorithms, visualizing memory states.

## Setup
1. Install Python 3.x.
2. Install dependencies: `pip install matplotlib tk`
3. Run: `python memory_visualizer.py`

## Usage
- Enter total memory (e.g., 32 KB) and page size (e.g., 4 KB).
- Add processes with sizes (e.g., 10 KB).
- Select FIFO or LRU.
- Click "Simulate" to see memory map and page faults.

## Features
- Paging simulation with FIFO/LRU replacement.
- Visual memory map (gray = free, green = occupied).
- Page fault tracking.