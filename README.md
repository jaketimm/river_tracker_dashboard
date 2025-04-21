# River Level Tracking System

## Overview
A Python-based system for tracking and visualizing river level data from USGS stations. The system provides a GUI interface for selecting river locations and viewing historical river level data with customizable time ranges.

## Features
- Interactive GUI for station selection and data visualization
- Modular architecture with separate components for data processing and visualization
- Comprehensive logging system for debugging and monitoring
- Flexible data sampling and display options (5-21 days)
- Persistent data storage using RDB format

## Prerequisites

- **Python 3.8+**
- Required packages:
  - `PyQt5`: GUI framework
  - `requests`: HTTP requests for data download
  - `pandas`: Data manipulation
  - `matplotlib`: Data visualization
  - `logging`: Built-in logging functionality

Install dependencies via pip:
```bash
pip install PyQt5 requests pandas matplotlib
```

## Project Structure

```
.
├── main.py                   # Main application entry point
├── data_processing.py        # Data processing and manipulation logic
├── data_visualization.py     # Data visualization components
├── river_level_data.rdb      # Persistent data storage
├── station_processer.py      # Compile CSV station list
├── station_list_mi.csv       # List of Michigan stations
├── real_mi.txt               # Michigan station data
├── river_data.log            # Application logs
└── .venv/                    # Python virtual environment
```

## Components

### Main Application (`main.py`)
- Handles GUI initialization and user interactions
- Coordinates between data processing and visualization modules
- Manages application logging

### Data Processing (`data_processing.py`)
- Handles USGS data retrieval and processing
- Implements data sampling and filtering
- Manages data persistence

### Data Visualization (`data_visualization.py`)
- Creates and manages data plots
- Handles graph customization and updates
- Implements visualization utilities

### Station Processing (`station_processer.py`)
- Processes and compiles station lists
- Manages station data in CSV format

## Logging
The application maintains detailed logs in `river_data.log`, including:
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


