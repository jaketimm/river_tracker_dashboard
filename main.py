# main.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QSlider, QLabel,
                            QLineEdit, QListWidget, QVBoxLayout, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from data_processing import download_river_data, validate_API_data
from data_visualization import display_river_data
import logging

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

        # Load station data from CSV
        self.stations_df = pd.read_csv('station_list_mi.csv', dtype={'id': str})
        self.stations = self.stations_df.to_dict('records')  # List of dicts with 'name' and 'id'

        self.initUI()
        self.time_period = 21  # default value of 21 days
        self.site_id = ''  # will be set when user selects a station
        self.site_name = ''
        self.sample_interval = 3  # default sampling interval

    def initUI(self):
        self.setGeometry(300, 300, 400, 500)  # Increased height to accommodate layout
        self.setWindowTitle('River Data Downloader')

        # Layout
        layout = QVBoxLayout()

        # Search bar for station filtering
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search for a station...")
        self.search_bar.textChanged.connect(self.filterStations)
        layout.addWidget(self.search_bar)

        # List widget to display stations, set height to 300
        self.station_list = QListWidget(self)
        self.station_list.setFixedHeight(300)  # Set height to 300 units
        self.updateStationList(self.stations)  # Populate with all stations initially
        self.station_list.itemClicked.connect(self.selectStation)
        layout.addWidget(self.station_list)

        # Sampling Interval label
        self.sample_label = QLabel('Sampling Interval', self)
        layout.addWidget(self.sample_label)

        # Add sampling interval dropdown, set width to 250
        self.combo_sample = QComboBox(self)
        self.combo_sample.addItems(['1 hour', '2 hours', '3 hours'])
        self.combo_sample.setCurrentText('3 hours')
        self.combo_sample.setFixedWidth(250)  # Set width to 250 units
        self.combo_sample.currentTextChanged.connect(self.updateSampleInterval)
        layout.addWidget(self.combo_sample)

        # Number of Days label
        self.days_label = QLabel('Number of Days', self)
        layout.addWidget(self.days_label)

        # Add slider for time period
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(5)
        self.slider.setMaximum(21)
        self.slider.setValue(21)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setFixedWidth(250)  # Match width with combo box
        self.slider.valueChanged.connect(self.updateTimePeriod)
        layout.addWidget(self.slider)

        # Add label to display selected days
        self.time_label = QLabel('21 days', self)
        layout.addWidget(self.time_label)

        # Download button, set width to 250
        self.button = QPushButton('Download and Display Data', self)
        self.button.setFixedWidth(250)  # Set width to 250 units
        self.button.clicked.connect(self.downloadAndDisplayData)
        layout.addWidget(self.button)

        # Add status label to show download status
        self.status_label = QLabel('', self)
        self.status_label.setFixedWidth(350)  
        layout.addWidget(self.status_label)

        # Add stretch to push content up and maintain spacing
        layout.addStretch()

        self.setLayout(layout)
        self.show()

    def updateStationList(self, stations):
        """Update the QListWidget with the given list of stations."""
        self.station_list.clear()
        for station in stations:
            self.station_list.addItem(f"{station['name']} ({station['id']})")

    def filterStations(self, text):
        """Filter stations based on search bar input."""
        if not text:
            self.updateStationList(self.stations)  # Show all if search is empty
        else:
            filtered_stations = [
                station for station in self.stations
                if text.lower() in station['name'].lower() or text in str(station['id'])
            ]
            self.updateStationList(filtered_stations)

    def selectStation(self, item):
        """Update site_id when a station is selected."""
        selected_text = item.text()
        # Extract the ID from the text (assumes ID is in parentheses at the end)
        station_id = selected_text.split('(')[-1].strip(')')
        # set name and ID
        self.site_name = selected_text
        self.site_id = station_id
        logger.info(f"Selected station ID: {self.site_id}")

    def updateTimePeriod(self, value):
        self.time_period = value
        self.time_label.setText(f'{value} days')

    def updateSampleInterval(self, text):
        """Update the sampling interval based on dropdown selection."""
        self.sample_interval = int(text.split()[0])

    def downloadAndDisplayData(self):
        if not self.site_id:
            # Show dialog box if no station is selected
            QMessageBox.warning(self, "No Station Selected", "Please select a station before downloading data.")
            return
        try:
            download_river_data(self.site_id, self.time_period)
            data_is_valid = validate_API_data()  # validate the data downloaded from the USGS API
            # if the data is valid, allow the data to be displayed 
            if data_is_valid:
                display_river_data(self.sample_interval, self.site_name)
                self.status_label.setText("Download succeeded")
                logger.info("Data processed successfully")
            else:
                self.status_label.setText("Download failed: API Data is not valid")
                logger.error("Data is not valid")
        except Exception as e:
            error_msg = f"Error occurred while processing data: {str(e)}"
            self.status_label.setText("Error Occurred: See log for details")
            logger.error(error_msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())