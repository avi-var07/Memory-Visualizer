![image](https://github.com/user-attachments/assets/fdffef65-e3f5-441b-9ed6-9e9295fda694)# Dynamic Memory Management Simulator

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)

A comprehensive educational tool for visualizing and understanding memory management techniques in operating systems, including paging, segmentation, and virtual memory.

## 📸 Project Screenshots

<details>
<summary>See Images</summary>

![Screenshot 1](https://github.com/user-attachments/assets/798c93b7-a15a-4e81-9318-dc83369a73ab)
![Screenshot 2 - Paging](https://github.com/user-attachments/assets/0c5d8e9b-6b1e-4e14-b5b3-5e6e9c7b8f0e)
![Screenshot 3 - Virtual Memory](https://github.com/user-attachments/assets/3f8b7c2a-5f9f-4b2d-8e1d-8a8f6c9d0e1f)
![Screenshot 4 - Segmentation Allocation](https://github.com/user-attachments/assets/6e2d9f3b-7c0f-4e24-9e2d-9b9f7d0e1f2g)
![Screenshot 5 - Segmentation with Fragmentation](https://github.com/user-attachments/assets/9f3e0g4c-8d1g-4f34-ae3e-ac0g8e1f2g3h)
![Screenshot 6 - Virtual Memory Allocation](https://github.com/user-attachments/assets/cg4h1i5d-9e2h-4g45-bf4f-bd1h9f2g3i4i)
![Screenshot 7 - Paging Allocation](https://github.com/user-attachments/assets/i5j2k6e-fg3i-4h56-cg5g-ce2i0g3h4j5j)

</details>



## 🔍 Overview

This project is an interactive visualization tool designed to simulate three core memory management techniques used in operating systems:

1. **Paging**: Demonstrates how physical memory is divided into fixed-size frames and logical memory into pages
2. **Segmentation**: Shows memory allocation with variable-sized segments based on logical divisions of programs
3. **Virtual Memory**: Illustrates the mapping between virtual and physical address spaces with on-demand loading

The simulator provides real-time visual feedback and performance metrics, making it an excellent educational resource for understanding these complex memory management concepts.

## ✨ Features

### Common Features
- Interactive web-based interface built with Streamlit
- Real-time memory visualization using Plotly
- Performance metrics tracking
- Process allocation and deallocation

### Paging Simulator
- Support for multiple page replacement algorithms (FIFO, LRU, LFU)
- Page table visualization
- Page fault tracking and hit ratio calculation
- Internal fragmentation analysis

### Segmentation Simulator
- Multiple allocation algorithms (First-Fit, Best-Fit, Worst-Fit)
- Segment table display
- External fragmentation analysis
- Free memory block distribution visualization 

### Virtual Memory Simulator
- Combined paging with demand loading
- Simulated page faults and disk operations
- Physical and virtual memory maps
- Memory access simulation with address translation

## 🛠️ Technology Stack

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Pandas**: Data processing and management
- **Plotly**: Interactive data visualization
- **NumPy**: Numerical operations

## 🚀 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/memory-management-simulator.git
   cd memory-management-simulator
   ```

2. Create and activate virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

5. The application should automatically open in your default browser at `http://localhost:8501`.

## 💻 Usage Guide

### Paging Simulation
1. Select "Paging" from the sidebar
2. Configure total memory size and page size
3. Select a page replacement algorithm (FIFO, LRU, LFU)
4. Allocate memory to processes using the form
5. Deallocate when finished
6. Observe the memory map and page table

### Segmentation Simulation
1. Select "Segmentation" from the sidebar
2. Configure total memory size
3. Choose an allocation algorithm (First-Fit, Best-Fit, Worst-Fit)
4. Allocate segments for different processes
5. Analyze fragmentation metrics
6. Deallocate segments or entire processes

### Virtual Memory Simulation
1. Select "Virtual Memory" from the sidebar
2. Set physical and virtual memory sizes
3. Configure page size and replacement algorithm
4. Allocate memory to processes
5. Simulate memory access operations
6. View the physical and virtual memory maps
7. Track page faults and disk operations

## 📚 Educational Value

This simulator is designed to help students and professionals understand:

- The trade-offs between different memory management techniques
- How page replacement algorithms affect system performance
- The causes and effects of memory fragmentation
- The benefits of virtual memory systems
- Address translation and memory mapping concepts

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

[Aviral Varshney]

- GitHub: [@avi-var07](https://github.com/avi-var07)
- LinkedIn: [Aviral Ved Varshney](https://www.linkedin.com/in/avi7/)
- Email: aviralvarshney07@gmail.com

---

![Screenshot 2025-04-29 235011](https://github.com/user-attachments/assets/798c93b7-a15a-4e81-9318-dc83369a73ab)


Built with ❤️ for Operating Systems enthusiasts and students.
