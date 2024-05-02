import requests
import os
import csv
import pandas as pd
from datetime import datetime, timezone

def get_item_by_hour(json_data, date_formatted, name, target_hour):
    """
    From the hourly data of open-meteo weather api, get the value of a specific item at a specific hour
    """
    times = json_data['hourly']['time']
    target_hour_iso = f"{date_formatted}T{target_hour:02d}:00"
    index = times.index(target_hour_iso)
    return json_data['hourly'][name][index]

def save_weather_data_to_csv(datetime, latitude, longitude, location_name, weather_data):
    path = f"data/travel_times/raw/{location_name}"

    if not os.path.exists(path):
        os.makedirs(path)

    csv_file_path = path + "/weather_data.csv"
    csv_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not csv_exists:
            writer.writerow(["datetime", "location_name", "latitude", "longitude", "temperature",
                             "relative_humidity", "dew_point", "precipitation", "precipitation_probability", "rain",
                             "surface_pressure", "apparent_temperature"])
            
        writer.writerow([datetime, location_name, latitude, longitude, weather_data['temperature'],
                         weather_data['relative_humidity'], weather_data['dew_point'], weather_data['precipitation'],
                         weather_data['precipitation_probability'], weather_data['rain'],
                         weather_data['surface_pressure'], weather_data['apparent_temperature']])

def fetch_weather_data(datetime, latitude, longitude, location_name):
    """
    Fetches weather data for a specific datetime and location
    """
    date, time = datetime.date(), datetime.time()
    date_formatted = date.strftime("%Y-%m-%d")

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={date_formatted}&end_date={date_formatted}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,precipitation_probability,rain,surface_pressure,wind_speed_10m,apparent_temperature&timezone=GMT"
  
    json_data = requests.get(url).json()

    data = {}
    data["temperature"] = get_item_by_hour(json_data, date_formatted, 'temperature_2m', time.hour)
    data["relative_humidity"] = get_item_by_hour(json_data, date_formatted, 'relative_humidity_2m', time.hour)
    data["dew_point"] = get_item_by_hour(json_data, date_formatted, 'dew_point_2m', time.hour)
    data["precipitation"] = get_item_by_hour(json_data, date_formatted, 'precipitation', time.hour)
    data["precipitation_probability"] = get_item_by_hour(json_data, date_formatted, 'precipitation_probability', time.hour)
    data["rain"] = get_item_by_hour(json_data, date_formatted, 'rain', time.hour)
    data["surface_pressure"] = get_item_by_hour(json_data, date_formatted, 'surface_pressure', time.hour)
    data["apparent_temperature"] = get_item_by_hour(json_data, date_formatted, 'apparent_temperature', time.hour)
    
    save_weather_data_to_csv(datetime, latitude, longitude, location_name, data)
    return

if __name__ == "__main__":
    for subdir, _, files in os.walk('data/travel_times/raw/'):
        for _ in files:
            location_name = os.path.split(subdir)[-1]
            print(f"Fetching weather data for {location_name}...")
            df = pd.read_csv(f'data/travel_times/raw/{location_name}/travel_time_data.csv')
            last_row = df.iloc[-1]
            fetch_weather_data(pd.to_datetime(last_row['datetime']), last_row['latitude'], last_row['longitude'], location_name)