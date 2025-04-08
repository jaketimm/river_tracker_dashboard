# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from data_processing import download_river_data
from data_visualization import display_river_data
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('river_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.time_period = 21  # default value of 21 days
        self.site_id = '04119070'  # default station choice
        self.sample_interval = 6  # default sampling interval

    def initUI(self):
        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle('River Data Downloader')

        self.site_id = ''

        self.combo_site = QComboBox(self)
        self.combo_site.addItem('Grand River - Wilson Ave Bridge')
        self.combo_site.addItem('Grand River - Downtown GR')
        self.combo_site.move(50, 50)
        self.combo_site.currentTextChanged.connect(self.updateSiteId)

        # Add sampling interval dropdown
        self.combo_sample = QComboBox(self)
        self.combo_sample.addItems(['1 hour', '2 hours', '3 hours'])
        self.combo_sample.move(130, 80)
        self.combo_sample.setCurrentText('3 hours')
        self.combo_sample.currentTextChanged.connect(self.updateSampleInterval)

        # Add slider for time period
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(5)
        self.slider.setMaximum(21)
        self.slider.setValue(21)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setFixedWidth(200)
        self.slider.move(50, 130)
        self.slider.valueChanged.connect(self.updateTimePeriod)

        # Add label to display selected days
        self.time_label = QLabel('21 days', self)
        self.time_label.move(265, 130)

        self.button = QPushButton('Download and Display Data', self)
        self.button.move(75, 180)
        self.button.clicked.connect(self.downloadAndDisplayData)

        self.show()

    def updateSiteId(self, text):
        if text == 'Grand River - Wilson Ave Bridge':
            self.site_id = '04119070'
        elif text == 'Grand River - Downtown GR':
            self.site_id = '04119000'

    def updateTimePeriod(self, value):
        self.time_period = value
        self.time_label.setText(f'{value} days')

    def updateSampleInterval(self, text):
        """Update the sampling interval based on dropdown selection."""
        self.sample_interval = int(text.split()[0])

    def downloadAndDisplayData(self):
        try:
            download_river_data(self.site_id, self.time_period)
            display_river_data(self.site_id, self.sample_interval)
            logger.info("Data processed successfully")
        except Exception as e:
            error_msg = f"Error occurred while processing data"
            logger.error(error_msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())