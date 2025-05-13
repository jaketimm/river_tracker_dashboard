# main.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QLabel)
import logging
from inland_lakes_rivers_widget import InlandLakesRiversWidget
from great_lakes_data_widget import GreatLakesDataWidget

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
        self.setWindowTitle('Water Data Downloader Application')
        self.setGeometry(200, 200, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()

        # Tab 1: Inland Lakes and Rivers
        tab1 = InlandLakesRiversWidget()
        tabs.addTab(tab1, "Inland Lakes and Rivers")
        tabs.addTab(tab1, "Inland Lakes and Rivers")

        # Tab 2: Great Lakes Data
        tab2 = GreatLakesDataWidget()
        tabs.addTab(tab2, "Great Lakes Data")

        # Add tabs to the main layout
        layout.addWidget(tabs)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    sys.exit(app.exec_())