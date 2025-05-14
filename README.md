# Water Level & Temperature Tracking System

## Overview
A Python-based system for tracking and visualizing data from USGS and NOAA stations. 
The system provides a GUI interface with two tabs. The first tab contains an interface for 
downloading, visualizing, and performing statistical calculations on data from USGS river and lake 
stations. The second tab contains an interface for downloading and visualizing data from NOAA 
buoy and lake stations.

## Features
- Interactive GUI for data downloading, statistics, and data visualization
- Modular architecture with separate components for data processing and visualization
- Comprehensive logging system for debugging and monitoring
- Flexible data sampling and display options 
- Persistent data storage using RDB format

## Prerequisites

- **Python 3.8+**
- Required packages:
  - `PyQt5`: GUI framework
  - `requests`: HTTP requests for data download
  - `pandas`: Data manipulation
  - `matplotlib`: Data visualization
  - `numpy`: Data manipulation

Install dependencies via pip:
```bash
pip install PyQt5 requests pandas matplotlib numpy
```

## Project Structure

```
.
├── main.py                       # Main application entry point
├── inland_lakes_rivers_widget.py # Inland Lake and River Tools GUI
├── great_lakes_data_widget.py    # Great Lakes Tools GUI
├── data_processing.py            # Data processing and manipulation logic
├── data_visualization.py         # Data visualization components
├── river_level_data.rdb          # Persistent data storage
├── station_processer.py          # Compile USGS CSV station list
├── station_list_mi.csv           # List of Michigan stations
├── real_mi.txt                   # Michigan station data
├── log_file.log                  # Application logs
└── .venv/                        # Python virtual environment
```

## Components

### Main Application (`main.py`)
- Handles GUI initialization and user interactions
- Manages application logging


### Inland Lakes & Rivers Widget (`inland_lakes_rivers_widget.py`)
- Contains interface for USGS data download and visualization tools
- Coordinates between data processing and visualization modules


### Great Lakes Widget (`great_lakes_data_widget.py`)
- Contains interface for NOAA data download and visualization tools
- Coordinates between data processing and visualization modules


### Data Processing (`data_processing.py`)
- Handles USGS data retrieval and processing
- Implements data sampling, filtering, and validation
- Manages data persistence


### Data Visualization (`data_visualization.py`)
- Creates and manages data plots
- Handles graph customization and updates
- Implements visualization utilities


### Station Processing (`station_processer.py`)
- Processes and compiles station lists
- Manages station data in CSV format


## Logging
The application maintains detailed logs in `log_file.log`, including:
- Data retrieval operations
- Processing steps
- Error conditions
- Application state changes

## How to Run

1. **Clone or Download**: Ensure all project files are in your working directory
2. **Install Dependencies**: Run the pip command above to install required packages
3. **Execute the Program**:
   ```bash
   python "main.py"
   ```


