import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd

# Define the main data directory and the processed directory
raw_data_dir = 'data/travel_times/raw'
processed_data_dir = 'data/travel_times/processed'

# Create the processed directory if it doesn't exist
os.makedirs(processed_data_dir, exist_ok=True)

# Iterate through each subfolder in the raw data directory
for subfolder in os.listdir(raw_data_dir):
    raw_subfolder_path = os.path.join(raw_data_dir, subfolder)
    processed_subfolder_path = os.path.join(processed_data_dir, subfolder)
    
    if os.path.isdir(raw_subfolder_path):
        travel_times_path = os.path.join(raw_subfolder_path, 'travel_time_data.csv')
        weather_data_path = os.path.join(raw_subfolder_path, 'weather_data.csv')
        
        if os.path.exists(travel_times_path) and os.path.exists(weather_data_path):
            travel_times_df = pd.read_csv(travel_times_path)
            weather_data_df = pd.read_csv(weather_data_path)
            weather_data_df.drop(columns=['datetime'], inplace=True)
            
            merged_df = pd.concat([travel_times_df, weather_data_df], axis=1)
            
            os.makedirs(processed_subfolder_path, exist_ok=True)
            
            merged_output_path = os.path.join(processed_subfolder_path, 'data.csv')
            merged_df.to_csv(merged_output_path, index=False)
        
print("All data processed.")