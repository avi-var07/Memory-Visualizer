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