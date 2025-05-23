# data_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter
import logging

logger = logging.getLogger(__name__)

'''
Function: display_river_data
Inputs: river station ID, sampling interval
Outputs: None
Description: Loads, samples data based on the sampling interval, 
and displays the river data for a selected river station using a compressed timescale.
'''
def display_data(sample_interval, site_name):
    try:
        # Read the RDB file into a DataFrame
        df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')
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
        
        # Convert datetime column to proper datetime objects
        df_sampled['datetime'] = pd.to_datetime(df_sampled['datetime'])

        # Calculate the number of days in the dataset
        time_range = (df_sampled['datetime'].max() - df_sampled['datetime'].min()).days + 1

        # Create a compressed x-axis using index values
        x_compressed = np.arange(len(df_sampled))

        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.plot(x_compressed, df_sampled['level'])
        ax1.set_xlabel(f'Date ({sample_interval} hr Increments)')
        ax1.set_ylabel('Water Level (feet)')
        plt.title(site_name)

        # Add background highlights for station 04119070
        if '04119070' in site_name:
            ymin = ax1.get_ylim()[0]
            ax1.set_ylim(ymin, (df_sampled['level'].max() + 0.5))
            ax1.axhspan(7.5, 10, facecolor='yellow', alpha=0.3)
            ax1.axhspan(10, ax1.get_ylim()[1], facecolor='red', alpha=0.3)

        # Set x-axis ticks based on number of days
        if time_range <= 45:
            # 1 label per day
            tick_step = max(24 // sample_interval, 1)
        else:
            # 1 label every 5 days
            tick_step = max((24 // sample_interval) * 5, 1)

        # Create tick positions and labels
        tick_positions = np.arange(0, len(df_sampled), tick_step)
        tick_labels = [df_sampled['datetime'].iloc[i].strftime('%Y-%m-%d %H:%M') 
                      for i in tick_positions if i < len(df_sampled)]

        # Set ticks and labels
        ax1.xaxis.set_major_locator(FixedLocator(tick_positions))
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: 
            tick_labels[int(x/tick_step)] if 0 <= int(x/tick_step) < len(tick_labels) else ''))
        
        ax1.tick_params(axis='x', rotation=45)
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

'''
Function: display_monthly_statistics_barchart
Inputs: river station ID
Outputs: None
Description: Loads the river data and displays a bar chart of the monthly water level min, max, and mean.
'''
def display_monthly_statistics_barchart(site_name):
    try:
        # Read the RDB file into a DataFrame
        df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')
        df = df.rename(columns={df.columns[4]: 'level'})
        
        # Convert level values from string to numeric, handling any non-numeric values
        df['level'] = pd.to_numeric(df['level'], errors='coerce')
        
        # Convert datetime column to proper datetime objects
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Extract month from datetime and create a new column
        df['month'] = df['datetime'].dt.month
        
        # Group by month and calculate mean, min, and max levels
        monthly_stats = df.groupby('month')['level'].agg(['mean', 'min', 'max']).reset_index()
        
        # Create month names for x-axis labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create the bar chart with grouped bars
        plt.figure(figsize=(12, 6))
        bar_width = 0.25
        x = np.arange(len(monthly_stats['month']))
        
        # Plot bars for mean, min, and max
        plt.bar(x - bar_width, monthly_stats['mean'], bar_width, label='Mean', color='skyblue')
        plt.bar(x, monthly_stats['min'], bar_width, label='Min', color='lightcoral')
        plt.bar(x + bar_width, monthly_stats['max'], bar_width, label='Max', color='lightgreen')
        
        # Add data labels on top of each bar
        for i in range(len(monthly_stats)):
            # Mean
            plt.text(x[i] - bar_width, monthly_stats['mean'][i] + 0.05, 
                     f'{monthly_stats["mean"][i]:.2f}', ha='center', va='bottom')
            # Min
            plt.text(x[i], monthly_stats['min'][i] + 0.05, 
                     f'{monthly_stats["min"][i]:.2f}', ha='center', va='bottom')
            # Max
            plt.text(x[i] + bar_width, monthly_stats['max'][i] + 0.05, 
                     f'{monthly_stats["max"][i]:.2f}', ha='center', va='bottom')
        
        # Set x-axis ticks and labels
        plt.xticks(x, [month_names[i-1] for i in monthly_stats['month']])
        
        plt.xlabel('Month')
        plt.ylabel('Water Level (feet)')
        plt.title(site_name + ': Monthly Water Level Statistics')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
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