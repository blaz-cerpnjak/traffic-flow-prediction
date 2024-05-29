import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd
import src.serve.utils.db_service as db_service

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
                    
                    processed_subfolder_path = os.path.join(processed_data_dir, folder, subfolder)
                    os.makedirs(processed_subfolder_path, exist_ok=True)
                    
                    # Merge the two datasets
                    merged_df = pd.concat([travel_times_df, weather_data_df], axis=1)
                    merged_output_path = os.path.join(processed_subfolder_path, 'data.csv')
                    merged_df.to_csv(merged_output_path, index=False)

                    # Save new row to MongoDB
                    last_row = merged_df.iloc[-1].copy()
                    last_row['direction'] = subfolder
                    db_service.save_to_collection('vehicle_counter_history', last_row)

                    # Determine the split index for an 80-20 train-test split
                    split_index = int(len(merged_df) * 0.8)

                    # Create train and test sets using slicing to preserve order
                    train_df = merged_df[:split_index]
                    test_df = merged_df[split_index:]

                    # Save the train and test sets
                    train_output_path = os.path.join(processed_subfolder_path, 'train.csv')
                    test_output_path = os.path.join(processed_subfolder_path, 'test.csv')
                    train_df.to_csv(train_output_path, index=False)
                    test_df.to_csv(test_output_path, index=False)

print("All data processed.")