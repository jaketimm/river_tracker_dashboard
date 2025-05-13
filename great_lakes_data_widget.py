# great_lakes_data_widget.py
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import pandas as pd
import io
import logging

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
            # Download the data from the URL
            response = requests.get(self.data_url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Read the data into a pandas DataFrame
            # The data has a header row starting with '#', and actual data follows
            lines = response.text.splitlines()
            # Skip the first two lines (header and units)
            data_lines = lines[2:]
            data_text = "\n".join(data_lines)

            # Parse the data into a DataFrame (space-separated)
            df = pd.read_csv(io.StringIO(data_text), sep=r'\s+', header=None)

            # According to the header, WTMP is the 15th column (index 14)
            if len(df.columns) > 9:
                self.latest_wtmp = df.iloc[0, 14]  # Most recent value (first row)
                self.wtmp_label.setText(f"Latest Holland Water Temperature: {self.latest_wtmp} °C")
                logger.info(f"Fetched latest WTMP: {self.latest_wtmp} °C")
            else:
                self.wtmp_label.setText("Latest Holland Water Temperature: Data format error")
                logger.error("Data format error: WTMP column not found")

        except Exception as e:
            self.wtmp_label.setText("Latest Holland Water Temperature: Failed to load data")
            logger.error(f"Error fetching data: {str(e)}")