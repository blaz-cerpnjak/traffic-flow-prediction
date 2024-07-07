import os
import pandas as pd

raw_data_dir = 'data/vehicle_counters/raw'

def remove_duplicates(df):
    # Find duplicates based on datetime column
    duplicates = df[df.duplicated(subset=['datetime'], keep=False)]
    if len(duplicates) == 0:
        return df

    duplicate_count = len(duplicates) - len(duplicates.drop_duplicates(subset=['datetime']))
    print(f"Number of duplicate rows: {duplicate_count}")

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Drop duplicates based on datetime column, keeping the first occurrence
    df_unique = df.drop_duplicates(subset=['datetime'])

    print(f"Number of duplicate rows after dropping: {len(df) - len(df_unique)}")
    return df_unique

for folder in os.listdir(raw_data_dir):

    folder_path = os.path.join(raw_data_dir, folder)
    if not os.path.isdir(folder_path):
        continue

    for subfolder in os.listdir(folder_path):

        subfolder_path = os.path.join(folder_path, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        
        weather_data_path = os.path.join(subfolder_path, 'weather_data.csv')
        if not os.path.exists(weather_data_path):
            continue

        weather_df = pd.read_csv(weather_data_path)

        weather_df = remove_duplicates(weather_df)

        weather_df.to_csv(weather_data_path, index=False)