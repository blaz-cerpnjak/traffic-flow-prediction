import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd

raw_data_dir = 'data/vehicle_counters/raw'
processed_data_dir = 'data/vehicle_counters/processed'

os.makedirs(processed_data_dir, exist_ok=True)

for folder in os.listdir(raw_data_dir):
    folder_path = os.path.join(raw_data_dir, folder)
    
    if os.path.isdir(folder_path):
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            
            if os.path.isdir(subfolder_path):
                travel_times_path = os.path.join(subfolder_path, 'counters_data.csv')
                weather_data_path = os.path.join(subfolder_path, 'weather_data.csv')
                
                if os.path.exists(travel_times_path) and os.path.exists(weather_data_path):
                    travel_times_df = pd.read_csv(travel_times_path)
                    weather_data_df = pd.read_csv(weather_data_path)
                
                    merged_df = pd.concat([travel_times_df, weather_data_df], axis=1)
                    
                    processed_subfolder_path = os.path.join(processed_data_dir, folder, subfolder)
                    os.makedirs(processed_subfolder_path, exist_ok=True)
                    
                    merged_output_path = os.path.join(processed_subfolder_path, 'data.csv')
                    merged_df.to_csv(merged_output_path, index=False)
                    
                    print(f"Merged data saved to {merged_output_path}")

print("All data processed.")