import requests
import time
from datetime import datetime, timedelta

def create_url(start_dt, end_dt, site="04119070", parameter="00065"):
    """Create formatted URL for data request."""
    base_url = "https://waterservices.usgs.gov/nwis/iv/"
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
    return (f"{base_url}?sites={site}&agencyCd=USGS&parameterCd={parameter}"
            f"&startDT={start_str}&endDT={end_str}&format=rdb")


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


def download_data():
    """Download data in 7-day blocks."""
    output_file = "river_level_data.rdb"
    current_time = datetime.now()
    header_written = False

    # Clear existing file
    with open(output_file, 'w') as f:
        f.write("# USGS River Level Data\n")

    # Download blocks of 7 days each
    for block in range(15):
        end_time = current_time - (timedelta(days=7) * block)
        start_time = end_time - timedelta(days=7)

        url = create_url(start_time, end_time)

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

            print(f"Successfully downloaded data for {start_time.date()} to {end_time.date()}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for block {block + 1}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred for block {block + 1}: {req_err}")
        except Exception as e:
            print(f"Unexpected error occurred for block {block + 1}: {e}")

        time.sleep(.5)

    # Sort the data by date after all downloads are complete
    print("Sorting data by date...")
    sort_data_by_date(output_file)
    print("Data sorting complete")


if __name__ == "__main__":
    download_data()