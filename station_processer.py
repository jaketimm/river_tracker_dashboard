import csv
import os


# This scipt is used to update the station_list_mi.csv file with the latest station data from 
# the real_mi.txt file. The real_mi.txt file is a list of stations that are currently in the 
# USGS database, and can be downloaed here: https://waterwatch.usgs.gov/index.php?id=wwds_map. 
# Select Michigan, currrent streamflow, site, Water-Resources Regions, and CSV.

try:
    # Check if input file exists
    if not os.path.exists('real_mi.txt'):
        raise FileNotFoundError("Input file 'real_mi.txt' not found")
    
    # Check if input file is empty
    if os.path.getsize('real_mi.txt') == 0:
        raise ValueError("Input file 'real_mi.txt' is empty")
    
    # Open input and output files
    with open('real_mi.txt', 'r') as infile, open('station_list_mi.csv', 'w', newline='') as outfile:
        # Read the input file contents
        lines = infile.readlines()
        
        # Set up CSV reader and writer
        reader = csv.DictReader(lines)
        
        # Verify required columns exist
        if 'name' not in reader.fieldnames or 'id' not in reader.fieldnames:
            raise ValueError("Required columns 'name' and 'id' not found in the input file")
        
        # Set up CSV writer with headers
        writer = csv.writer(outfile)
        writer.writerow(['name', 'id'])
        
        # Process each row
        row_count = 0
        for row_num, row in enumerate(reader, 1):
            try:
                # Extract name and ID from columns
                name = row.get('name', '').strip()
                station_id = row.get('id', '').strip()
                
                # Error checking: verify ID is numeric
                if not station_id.isdigit():
                    print(f"Error at row {row_num}: Station ID '{station_id}' is not numeric")
                    continue
                
                # Check if station name contains 'MI'
                if 'MI' not in name:
                    print(f"Warning at row {row_num}: Station name '{name}' does not contain 'MI' and will be excluded")
                    continue
                
                # Write to CSV
                writer.writerow([name, station_id])
                row_count += 1
                
            except Exception as e:
                print(f"Error processing row {row_num}: {str(e)}")
        
        # Verify that data was written
        if row_count == 0:
            print("Warning: No valid data was written to the output file")
        else:
            print(f"Processing complete. {row_count} stations written to 'station_list_mi.csv'.")

except FileNotFoundError as e:
    print(f"File error: {str(e)}")
except ValueError as e:
    print(f"Data error: {str(e)}")
except csv.Error as e:
    print(f"CSV error: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")