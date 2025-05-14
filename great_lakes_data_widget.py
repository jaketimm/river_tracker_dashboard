# great_lakes_data_widget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import logging
from data_processing import download_buoy_current_temp

logger = logging.getLogger(__name__)


class GreatLakesDataWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data_url = "https://www.ndbc.noaa.gov/data/realtime2/45029.txt"
        self.latest_wtmp = "Not loaded"
        self.initUI()

    def initUI(self):
        # Main layout for the widget
        layout = QVBoxLayout()

        # Label to display the latest water temperature
        self.wtmp_label = QLabel("Latest Holland Water Temperature: Not loaded", self)
        self.wtmp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.wtmp_label)

        # Button to refresh data
        self.refresh_button = QPushButton("Refresh Data", self)
        self.refresh_button.clicked.connect(self.fetchData)
        self.refresh_button.setFixedWidth(200)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignCenter)

        # Add stretch to center content vertically
        layout.addStretch()

        self.setLayout(layout)

        # Fetch data on initialization
        self.fetchData()

    def fetchData(self):
        """Fetch data from the URL and update the WTMP label with the most recent value."""
        try:
            # Call the download function from data_processing.py
            self.latest_wtmp = download_buoy_current_temp(self.data_url)
            
            if self.latest_wtmp is not None:
                # Convert Celsius to Fahrenheit
                fahrenheit = (self.latest_wtmp * 9/5) + 32
                self.wtmp_label.setText(f"Latest Holland Water Temperature: {fahrenheit:.1f} °F")
            else:
                self.wtmp_label.setText("Latest Holland Water Temperature: N/A")
                logger.error("Failed to retrieve water temperature data")

        except Exception as e:
            self.wtmp_label.setText("Latest Holland Water Temperature: Failed to load data")
            logger.error(f"Error fetching data: {str(e)}")