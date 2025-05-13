# main.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
import logging
from inland_lakes_rivers_widget import InlandLakesRiversWidget

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log_file.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Downloader Application')
        self.setGeometry(200, 200, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()

        # Tab 1: Inland Lakes and Rivers (original MyApp widget)
        tab1 = InlandLakesRiversWidget()
        tabs.addTab(tab1, "Inland Lakes and Rivers")

        # Tab 2: Simple placeholder tab
        tab2 = QWidget()
        tab2_layout = QHBoxLayout()
        tab2_label = QLabel("Tab 2")
        tab2_label.setAlignment(Qt.AlignCenter)
        tab2_layout.addWidget(tab2_label)
        tab2.setLayout(tab2_layout)
        tabs.addTab(tab2, "Tab 2")

        # Add tabs to the main layout
        layout.addWidget(tabs)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    sys.exit(app.exec_())