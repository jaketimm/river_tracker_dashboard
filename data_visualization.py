# data_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import logging

logger = logging.getLogger(__name__)

'''
Function: display_river_data
Inputs: river station ID, sampling interval
Outputs: None
Description: Loads, samples data based on the sampling interval, 
and displays the river data for a selected river station.
'''


def display_river_data(sample_interval, site_name):
    
    try:
        # Read the RDB file into a DataFrame
        df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')

        # Verify that the DataFrame is not empty
        if df.empty:
            logger.error("Loaded data is empty")
            raise ValueError("Loaded data is empty. Please check the data source.")

        # Verify required columns exist
        if 'datetime' not in df.columns or len(df.columns) < 5:
            logger.error("Required columns missing from data file")
            raise ValueError("Required columns missing from data file.")

        df = df.rename(columns={df.columns[4]: 'level'})

        # Extract the time from the 'datetime' column as a string
        time = df['datetime'].str[11:]

        # Generate sampling times based on selected interval
        sample_hours = [f'{hour:02d}:00' for hour in range(0, 24, sample_interval)]
        df_sampled = df[time.isin(sample_hours)]

        # Verify sampled data is not empty
        if df_sampled.empty:
            logger.error(f"No data available for {sample_interval}-hour sampling interval")
            raise ValueError(f"No data available for {sample_interval}-hour sampling interval.")

        # Convert level values from string to numeric
        df_sampled = df_sampled.astype({'level': float}, errors='ignore')
        df_sampled.iloc[0, 4] = df_sampled.iloc[1, 4]  # overwrite '14n' string
        
        # Convert datetime column to proper datetime objects to avoid matplotlib warning
        df_sampled['datetime'] = pd.to_datetime(df_sampled['datetime'])

        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.plot(df_sampled['datetime'], df_sampled['level'])
        ax1.set_xlabel(f'Date ({sample_interval} hr Increments)')
        ax1.set_ylabel('Water Level (feet)')
        plt.title(site_name)

        # Add background highlights for station 04119070
        if '04119070' in site_name:
            # existing y-axis minimum limit
            ymin = ax1.get_ylim()[0]
            # Set y-axis limits manually based on maxiumum level value plus a .5 foot offset to prevent chart from adding extra white space
            ax1.set_ylim(ymin, (df_sampled['level'].max() +.5))  
            # Yellow background between 7.5 and 10 feet
            ax1.axhspan(7.5, 10, facecolor='yellow', alpha=0.3)
            # Red background above 10 feet to the top of the y-axis
            ax1.axhspan(10, ax1.get_ylim()[1], facecolor='red', alpha=0.3)

        ax1.tick_params(rotation=45)
        # Adjust x-tick frequency based on sampling interval
        tick_step = max(24 // sample_interval, 1)  # Show at least one label per day
        # Set x-ticks directly from the sampled data
        ax1.set_xticks(df_sampled['datetime'][::tick_step])
        ax1.set_xticklabels([dt.strftime('%Y-%m-%d %H:%M') for dt in df_sampled['datetime'][::tick_step]], rotation=45)
        plt.tight_layout()
        plt.show()

    except pd.errors.EmptyDataError:
        logger.error("Data file is empty or corrupt")
        raise ValueError("Data file is empty or corrupt. Please download data again.")
    except pd.errors.ParserError:
        logger.error("Error parsing data file")
        raise ValueError("Error parsing data file. File format may be incorrect.")
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise RuntimeError(f"Error processing data: {str(e)}")