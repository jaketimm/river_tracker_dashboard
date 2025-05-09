# main.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QSlider, QLabel,
                            QLineEdit, QListWidget, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from data_processing import validate_API_data, export_data, generate_summary_statistics, download_data_single_block, download_data_multiple_blocks
from data_visualization import display_data, display_monthly_averages
import logging

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

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Load station data from CSV
        self.stations_df = pd.read_csv('station_list_mi.csv', dtype={'id': str})
        self.stations = self.stations_df.to_dict('records')  # List of dicts with 'name' and 'id'

        self.initUI()
        self.time_period = 1  # default value of 21 days
        self.site_id = ''  # will be set when user selects a station
        self.site_name = ''
        self.sample_interval = 3  # default sampling interval

    def initUI(self):
        self.setGeometry(300, 300, 400, 550)  # Increased height for new button
        self.setWindowTitle('River & Lake Data Downloader')

        # Main layout
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

        # Create horizontal layout for controls
        controls_layout = QHBoxLayout()

        # Left side controls
        left_layout = QVBoxLayout()

        # Sampling Interval label
        self.sample_label = QLabel('Graph Sampling Interval', self)
        left_layout.addWidget(self.sample_label)

        # Add sampling interval dropdown, set width to 250
        self.combo_sample = QComboBox(self)
        self.combo_sample.addItems(['1 hour', '2 hours', '3 hours'])
        self.combo_sample.setCurrentText('3 hours')
        self.combo_sample.setFixedWidth(250)  # Set width to 250 units
        self.combo_sample.currentTextChanged.connect(self.updateSampleInterval)
        left_layout.addWidget(self.combo_sample)

        # Download Mode label
        self.download_mode_label = QLabel('Download Mode', self)
        left_layout.addWidget(self.download_mode_label)

        # Add download mode dropdown, set width to 250
        self.combo_download_mode = QComboBox(self)
        self.combo_download_mode.addItems(['Single Block', 'Multiple Blocks'])
        self.combo_download_mode.setCurrentText('Multiple Blocks')
        self.combo_download_mode.setFixedWidth(250)  # Set width to 250 units
        self.combo_download_mode.currentTextChanged.connect(self.updateDownloadMode)
        left_layout.addWidget(self.combo_download_mode)

        # Number of Weeks label
        self.days_label = QLabel('Number of Weeks', self)
        left_layout.addWidget(self.days_label)

        # Add slider for number of weeks
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(52)
        self.slider.setValue(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(4)  # 4 week intervals
        self.slider.setFixedWidth(250)  # Match width with combo box
        self.slider.valueChanged.connect(self.updateTimePeriod)
        left_layout.addWidget(self.slider)

        # Add label to display selected days
        self.time_label = QLabel('1 week', self)
        left_layout.addWidget(self.time_label)

        # Add left layout to controls layout
        controls_layout.addLayout(left_layout)

       # Right side controls
        right_layout = QVBoxLayout()

        # Download button, set width to 250
        self.download_button = QPushButton('Download Data', self)
        self.download_button.setFixedWidth(250)  # Set width to 250 units
        self.download_button.clicked.connect(self.downloadData)
        right_layout.addWidget(self.download_button)

        # Display button, set width to 250
        self.display_button = QPushButton('Display Data', self)
        self.display_button.setFixedWidth(250)  # Set width to 250 units
        self.display_button.clicked.connect(self.displayData)
        self.display_button.setEnabled(False)  # Initially disabled
        right_layout.addWidget(self.display_button)
        
        # Monthly averages button, set width to 250
        self.monthly_avg_button = QPushButton('Monthly Averages', self)
        self.monthly_avg_button.setFixedWidth(250)  # Set width to 250 units
        self.monthly_avg_button.clicked.connect(self.displayMonthlyAverages)
        self.monthly_avg_button.setEnabled(False)  # Initially disabled
        right_layout.addWidget(self.monthly_avg_button)

        # Export button, set width to 250
        self.export_button = QPushButton('Export to CSV', self)
        self.export_button.setFixedWidth(250)  # Set width to 250 units
        self.export_button.clicked.connect(self.exportData)
        self.export_button.setEnabled(False)  # Initially disabled
        right_layout.addWidget(self.export_button)

        # Export button, set width to 250
        self.generate_stats_button = QPushButton('Summary Statistics', self)
        self.generate_stats_button.setFixedWidth(250)  # Set width to 250 units
        self.generate_stats_button.clicked.connect(self.generateStatistics)
        self.generate_stats_button.setEnabled(False)  # Initially disabled
        right_layout.addWidget(self.generate_stats_button)

        # Add status label to show download status
        self.status_label = QLabel('', self)
        self.status_label.setFixedWidth(350)
        right_layout.addWidget(self.status_label)

        # Add right layout to controls layout
        controls_layout.addLayout(right_layout)
        controls_layout.addStretch()

        # Add the controls layout to the main layout
        layout.addLayout(controls_layout)

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
        self.status_label.setText(f"Selected: {self.site_id}")
        logger.info(f"Selected station ID: {self.site_id}")


    def updateTimePeriod(self, value):
        self.time_period = value
        self.time_label.setText(f'{value} week(s)')
        # Reset data availability when changing time period
        self.display_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.generate_stats_button.setEnabled(False)
        self.monthly_avg_button.setEnabled(False)  # Disable monthly averages button

    def updateSampleInterval(self, text):
        """Update the sampling interval based on dropdown selection."""
        self.sample_interval = int(text.split()[0])

    def updateDownloadMode(self, text):
        """Update the download mode based on dropdown selection."""
        self.download_mode = text

    def downloadData(self):
        """Download and validate river data."""
        if not self.site_id:
            QMessageBox.warning(self, "No Station Selected", "Please select a station before downloading data.")
            return
        try:
            self.status_label.setText("Downloading...")
            QApplication.processEvents()  # Force UI to update immediately
            if hasattr(self, 'download_mode') and self.download_mode == 'Single Block':
                download_data_single_block(self.site_id, self.time_period)
            else:
                download_data_multiple_blocks(self.site_id, self.time_period, parent=self)
            data_is_valid = validate_API_data()  # validate the data downloaded from the USGS API
            if data_is_valid:
                self.status_label.setText("Download Finished")
                self.display_button.setEnabled(True)
                self.export_button.setEnabled(True)
                self.generate_stats_button.setEnabled(True)
                self.monthly_avg_button.setEnabled(True)  # Enable monthly averages button
                logger.info("Data downloaded and validated successfully")
            else:
                self.status_label.setText("Download failed")
                self.display_button.setEnabled(False)
                self.export_button.setEnabled(False)
                self.generate_stats_button.setEnabled(False)
                self.monthly_avg_button.setEnabled(False)  # Disable monthly averages button
                logger.error("Downloaded data is not valid")
        except Exception as e:
            self.status_label.setText("Download failed")
            self.display_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.generate_stats_button.setEnabled(False)
            self.monthly_avg_button.setEnabled(False)  # Disable monthly averages button
            logger.error(f"Error occurred while downloading data: {str(e)}")
            
    def displayData(self):
        """Display the downloaded river data."""
        try:
            display_data(self.sample_interval, self.site_name)
            logger.info("Data displayed successfully")
        except Exception as e:
            logger.error(f"Error occurred while displaying data: {str(e)}")
    
    def displayMonthlyAverages(self):
        """Display monthly average water levels as a bar chart."""
        try:
            display_monthly_averages(self.site_name)
            logger.info("Monthly average data displayed successfully")
        except Exception as e:
            logger.error(f"Error occurred while displaying monthly averages: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to display monthly averages: {str(e)}")

    def exportData(self):
        """Export downloaded data to CSV."""
        try:
            export_data(self.site_id, parent=self)

        except Exception as e:
            logger.error(f"Error occurred while exporting data: {str(e)}")

    def generateStatistics(self):
        """Generate summary statistics for the downloaded data."""
        try:
            generate_summary_statistics(parent=self)
            logger.info("Summary statistics displayed successfully")
        except Exception as e:
            logger.error(f"Error occurred while generating statistics: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
