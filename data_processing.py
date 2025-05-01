# data_processing.py
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd
import requests
import logging
import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog

logger = logging.getLogger(__name__)

'''
Function: download_river_data
Inputs: river station ID, number of days of data to download
Outputs: None
Description: Downloads data for a selected river station from the USGS API. The data is saved locally into 
a file named river_level_data.rdb
'''
def download_river_data(station_id, num_days):
    timestamp = datetime.now()

    # Calculate date `num_days` ago
    start_datetime = timestamp - timedelta(days=num_days)

    # Format dates as required by the USGS API
    start_dt = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'
    end_dt = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'

    # Construct query parameters dictionary
    params = {
        'sites': station_id,
        'agencyCd': 'USGS',
        'parameterCd': '00065',
        'startDT': start_dt,
        'endDT': end_dt,
        'format': 'rdb'
    }

    # Build the URL
    base_url = 'https://waterservices.usgs.gov/nwis/iv/'
    url = base_url + '?' + urlencode(params)

    try:
        # Download the data
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the data to a file
            with open('river_level_data.rdb', 'wb') as f:
                f.write(response.content)
            logger.info(f"Download succeeded - URL: {url}")
        else:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Download failed - URL: {url} - Error: {str(e)}")
        raise  # Re-raise the exception to be handled by the caller


'''
Function: validate_API_data
Inputs: None
Outputs: flag indicating if the data is valid
Description: Validates the data downloaded from the USGS API. 
'''
def validate_API_data():
    try:
        if not os.path.exists('river_level_data.rdb'):
            logger.error("Data file 'river_level_data.rdb' not found")
            return False

        # Read the RDB file into a DataFrame
        df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')

        # Verify that the DataFrame is not empty
        if df.empty:
            logger.error("Loaded data is empty")
            return False

        # Verify required columns exist
        if 'datetime' not in df.columns or len(df.columns) < 5:
            logger.error("Required columns missing from data file")
            return False

        return True  # data is valid, allow data display and export

    except pd.errors.EmptyDataError:
        logger.error("Data file is empty or corrupt")
        return False
    except pd.errors.ParserError:
        logger.error("Error parsing data file")
        return False
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return False

'''
Function: export_river_data
Inputs: site_id for filename generation, parent widget for dialogs
Outputs: None
Description: Exports the downloaded river data to a CSV file. Raises exceptions on failure.
'''
def export_river_data(site_id, parent=None):
    """Export downloaded data to CSV."""
    try:
        # Read the downloaded RDB file, skipping comment lines
        data = pd.read_csv('river_level_data.rdb',
                            comment='#',
                            sep='\t',
                            skiprows=[0],  # Skip the first non-comment line (format spec)
                            dtype={'agency_cd': str, 'site_no': str})

        # Clean column names (remove any whitespace)
        data.columns = data.columns.str.strip()

        # Generate default filename using site ID and current timestamp
        default_filename = f"river_data_{site_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Open file dialog for user to choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save CSV File",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            # Export to CSV
            data.to_csv(file_path, index=False)
            logger.info(f"Data exported successfully to {file_path}")
            QMessageBox.information(parent, "Export Successful",
                                    f"Data exported to {file_path}")
        else:
            logger.info("Export cancelled by user")
            return

    except Exception as e:
        logger.error(f"Error occurred while exporting data: {str(e)}")
        QMessageBox.critical(parent, "Export Failed",
                            f"Failed to export data: {str(e)}")
        raise Exception(f"Failed to export data: {str(e)}")
    
def generate_summary_statistics():
    """Generate summary statistics for the downloaded data."""
    print("Generating summary statistics...")


