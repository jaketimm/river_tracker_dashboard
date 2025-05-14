# data_processing.py
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd
import requests
import logging
import os
import time
import io
from PyQt5.QtWidgets import QMessageBox, QFileDialog

logger = logging.getLogger(__name__)

'''
Function: create_url
Inputs: start_dt, end_dt, site, parameter
Outputs: URL string
Description: Create formatted URL for data request.
'''
def create_url(start_dt, end_dt, site, parameter="00065"):
    """Create formatted URL for data request."""
    base_url = "https://waterservices.usgs.gov/nwis/iv/"
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
    return (f"{base_url}?sites={site}&agencyCd=USGS&parameterCd={parameter}"
            f"&startDT={start_str}&endDT={end_str}&format=rdb")

'''
Function: sort_data_by_date
Inputs: input_file path
Outputs: None
Description: Sort the data in the file by date in ascending order.
'''
def sort_data_by_date(input_file):
    """Sort the data in the file by date in ascending order."""
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Separate header and data
    header_lines = []
    data_lines = []

    for line in lines:
        if line.startswith('#') or line.startswith('agency_cd'):
            header_lines.append(line.strip())
        elif line.startswith('USGS'):
            data_lines.append(line.strip())

    # Sort data lines by date (column 3 in RDB format is datetime)
    if data_lines:
        # Parse datetime from third column and sort
        data_lines.sort(key=lambda x: datetime.strptime(x.split('\t')[2], '%Y-%m-%d %H:%M'))

    # Write sorted data back to file
    with open(input_file, 'w') as f:
        # Write headers first
        f.write('\n'.join(header_lines) + '\n')
        # Write sorted data
        if data_lines:
            f.write('\n'.join(data_lines) + '\n')

'''
Function: download_data_multiple_blocks
Inputs: river station ID, number of weeks of data to download
Outputs: None
Description: Downloads data for a selected river station from the USGS API in 7-day blocks.
The data is saved locally into a file named river_level_data.rdb
'''
def download_data_multiple_blocks(site_id, num_weeks, parent=None):
    """Download data in 7-day blocks."""
    output_file = "river_level_data.rdb"
    current_time = datetime.now()
    header_written = False
    failed_blocks = []

    # Clear existing file
    with open(output_file, 'w') as f:
        f.write("# USGS River Level Data\n")

    # Download blocks of 7 days each
    for block in range(num_weeks):
        end_time = current_time - (timedelta(days=7) * block)
        start_time = end_time - timedelta(days=7)

        url = create_url(start_time, end_time, site_id)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            lines = response.text.split('\n')
            data_to_write = []

            for line in lines:
                if not line.strip():
                    continue
                if line.startswith('agency_cd') and not header_written:
                    data_to_write.append(line)
                    header_written = True
                elif line.startswith('USGS'):
                    data_to_write.append(line)

            if data_to_write:
                with open(output_file, 'a') as f:
                    f.write('\n'.join(data_to_write) + '\n')

        except requests.exceptions.HTTPError as http_err:
            failed_blocks.append((start_time, end_time))
            logger.error(f"HTTP error occurred for time range {start_time} to {end_time}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            failed_blocks.append((start_time, end_time))
            logger.error(f"Request error occurred for time range {start_time} to {end_time}: {req_err}")
        except Exception as e:
            failed_blocks.append((start_time, end_time))
            logger.error(f"Unexpected error occurred for time range {start_time} to {end_time}: {e}")

        time.sleep(.5)  # half second delay between requests

    # Show warning popup if any blocks failed
    if failed_blocks and parent:
        failed_ranges = "\n".join([f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}" for start, end in failed_blocks])
        QMessageBox.warning(parent, "Download Warning", f"Failed to download data for the following time range(s):\n{failed_ranges}")

    logger.info("Data download complete")
    sort_data_by_date(output_file)
    logger.info("Data sorting by date complete")

'''
Function: download_data_single_block
Inputs: river station ID, number of days of data to download in weeks
Outputs: None
Description: Downloads data for a selected river station from the USGS API. The data is saved locally into 
a file named river_level_data.rdb
'''
def download_data_single_block(station_id, num_weeks):
    timestamp = datetime.now()

    # Calculate date `num_days` ago
    start_datetime = timestamp - timedelta(days=(num_weeks * 7))
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
        response.raise_for_status()

        output_file = "river_level_data.rdb"
        header_written = False
        data_to_write = []

        # Process the response text line by line
        lines = response.text.split('\n')
        for line in lines:
            if not line.strip():
                continue
            if line.startswith('agency_cd') and not header_written:
                data_to_write.append(line)
                header_written = True
            elif line.startswith('USGS'):
                data_to_write.append(line)

        # Write processed data to file
        with open(output_file, 'w') as f:
            f.write("# USGS River Level Data\n")
            if data_to_write:
                f.write('\n'.join(data_to_write) + '\n')

        logger.info(f"Download succeeded - URL: {url}")
        sort_data_by_date(output_file)
        logger.info("Data sorting by date complete")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise Exception(f"HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        raise Exception(f"Request Error: {req_err}")
    except Exception as e:
        logger.error(f"Download failed - URL: {url} - Error: {str(e)}")
        raise Exception(f"Download failed: {str(e)}")

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
Function: export_data
Inputs: site_id for filename generation, parent widget for dialogs
Outputs: None
Description: Exports the downloaded river data to a CSV file. Raises exceptions on failure.
'''
def export_data(site_id, parent=None):
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
                            f"Failed to export data")
        raise Exception(f"Failed to export data: {str(e)}")
    
'''
Function: download_buoy_current_temp
Inputs: buoy_url - URL for the buoy data
Outputs: latest_wtmp - the current water temperature value as a float, or None if error
Description: Downloads current temperature data from a NOAA buoy.
'''
def download_buoy_current_temp(buoy_url):
    """Fetch data from the URL and return the most recent WTMP value."""
    try:
        # Download the data from the URL
        logger.info(f"Fetching buoy data from {buoy_url}")
        response = requests.get(buoy_url)
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
        if len(df.columns) > 14:  # Ensure WTMP column exists (index 14)
            latest_wtmp = df.iloc[0, 14]  # Most recent value (first row)
            logger.info(f"Fetched latest WTMP: {latest_wtmp} °C")
            return latest_wtmp
        else:
            logger.error("Data format error: WTMP column not found")
            return None

    except Exception as e:
        logger.error(f"Error fetching buoy data: {str(e)}")
        return None

'''
Function: generate_summary_statistics
Inputs: parent widget for dialogs
Outputs: None
Description: Generates summary statistics for the downloaded data.
'''
def generate_summary_statistics(parent=None):
    """Generate summary statistics for the downloaded data."""
    try:
        # Read the downloaded RDB file, skipping comment lines
        data = pd.read_csv('river_level_data.rdb',
                            comment='#',
                            sep='\t',
                            skiprows=[0],  # Skip the first non-comment line (format spec)
                            dtype={'agency_cd': str, 'site_no': str})

        # Clean column names (remove any whitespace)
        data.columns = data.columns.str.strip()
        data.iloc[0, 4] = data.iloc[1, 4]  # overwrite '14n' string
        data = data.rename(columns={data.columns[4]: 'level'})
        data = data.astype({'level': float}, errors='ignore')

        # Calculate statistics
        stats = {
            'Mean': data['level'].mean(),
            'Median': data['level'].median(),
            'Std Dev': data['level'].std(),
            'Min': data['level'].min(),
            'Max': data['level'].max()
        }

        # Format statistics message with units
        stats_message = "\n".join([f"{key}: {value:.2f} feet" for key, value in stats.items()])
        
        # Display in message box
        QMessageBox.information(
            parent,
            "Summary Statistics",
            stats_message
        )
        logger.info("Summary statistics generated successfully")

    except Exception as e:
        logger.error(f"Error occurred while processing data: {str(e)}")
        QMessageBox.critical(
            parent,
            "Statistics Error",
            f"Failed to generate statistics"
        )
        raise Exception(f"Failed to generate statistics: {str(e)}")
