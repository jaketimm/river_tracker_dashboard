# data_processing.py
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
import logging

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