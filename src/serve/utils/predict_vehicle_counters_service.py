import sys
sys.path.append("../../../")
import pandas as pd
import numpy as np
import onnxruntime as rt
from src.data.weather import fetch_weather_data as weather_service
from src.utils.locations import LOCATION_NAMES, HIGHWAY_LOCATIONS
import math
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import threading
import src.serve.utils.db_service as db_service

def save_prediction_to_mongodb(datetime_utc, location_name, destination, input_data, prediction):
    """
    Saves the given prediction with input data to MongoDB.
    """
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["traffic_flow_predictions"]
    collection = db["vehicle_counter_predictions"]

    item = {
        "datetime": datetime_utc,
        "location_name": location_name,
        "destination": destination, 
        "input_data": input_data,
        "prediction": prediction
    }

    collection.insert_one(item)
    return

def get_last_window(location_name, direction, window_size=24):
    # TODO: load from mongodb
    df = pd.read_csv(f'../../data/vehicle_counters/processed/{location_name}/{direction}/data.csv')
    df = df.tail(window_size)
    return df

def predict_vehicle_count(model_path, scalers, datetime_utc, location_name, direction, df):
    """
    Returns number of vehicles prediction for next hour at the given `location_name` location and `destination` destination.
    """
    number_of_vehicle_right_lane_scaler = scalers['number_of_vehicles_right_lane_scaler']

    features = ['apparent_temperature', 'number_of_vehicles_right_lane']
    X = df[features]
    X_reshaped = np.reshape(X, (1, len(features), 24))

    sess = rt.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name
    onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
    onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
    onnx_predictions = onnx_predictions.reshape(1, -1)
    inverse_transformed = number_of_vehicle_right_lane_scaler.inverse_transform(onnx_predictions)
    prediction = inverse_transformed[0][0]
    
    threading.Thread(target=save_vehicle_counter_prediction, args=(location_name, datetime_utc, direction, df, prediction)).start()

    return prediction

def save_vehicle_counter_prediction(location_name, datetime_utc, direction, df, prediction):
    db_service.save_vehicle_counter_prediction(datetime_utc, location_name, direction, df, int(prediction))

# Cached weather predictions
weather_predictions = {}

def predict_vehicle_count_for_next_hours(model_path, scalers, location_name, direction, hours):
    """
    Returns predictions for the next `hours` hours at the given location and direction.
    """
    predictions_by_hour = {}

    number_of_vehicle_right_lane_scaler = scalers['number_of_vehicles_right_lane_scaler']
    apparent_temperature_scaler = scalers['apparent_temperature_scaler']

    df = get_last_window(location_name, direction)
    df['number_of_vehicles_right_lane'] = number_of_vehicle_right_lane_scaler.transform(df['number_of_vehicles_right_lane'].values.reshape(-1, 1))
    df['apparent_temperature'] = apparent_temperature_scaler.transform(df['apparent_temperature'].values.reshape(-1, 1))

    latitude = df.iloc[-1]['latitude']
    longitude = df.iloc[-1]['longitude']
    datetime_utc = pd.to_datetime(df.iloc[-1]['datetime'])

    prediction = predict_vehicle_count(model_path, scalers, datetime_utc, location_name, direction, df)
    if math.isnan(prediction):
        return None

    predictions_by_hour = []

    prediction_item = {}
    prediction_item['location'] = location_name
    prediction_item['route'] = HIGHWAY_LOCATIONS[location_name][direction]
    prediction_item['datetime'] = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    prediction_item['number_of_vehicles_right_lane'] = int(prediction)

    predictions_by_hour.append(prediction_item)

    if hours > 0:
        for _ in range(hours):
            datetime_utc = datetime_utc + pd.Timedelta(hours=1)

            if location_name not in weather_predictions:
                weather_data = weather_service.fetch_weather_data(datetime_utc, latitude, longitude)
                weather_predictions[location_name] = { datetime_utc.day : weather_data }
                print("location_name not in weather_predictions")
            elif datetime_utc.day not in weather_predictions[location_name]:
                weather_data = weather_service.fetch_weather_data(datetime_utc, latitude, longitude)
                weather_predictions[location_name][datetime_utc.day] = weather_data
                print("datetime_utc not in weather_predictions")
            else:
                weather_data = weather_predictions[location_name][datetime_utc.day]
                print("weather_data from cache")

            apparent_temperature = weather_data['apparent_temperature']

            new_row = {
                'datetime': datetime_utc,
                'latitude': latitude,
                'longitude': longitude,
                'number_of_vehicles_right_lane': int(prediction),
                'apparent_temperature': apparent_temperature,
            }

            new_row = pd.DataFrame([new_row])
            new_row['number_of_vehicles_right_lane'] = number_of_vehicle_right_lane_scaler.transform(new_row['number_of_vehicles_right_lane'].values.reshape(-1, 1))
            new_row['apparent_temperature'] = apparent_temperature_scaler.transform(new_row['apparent_temperature'].values.reshape(-1, 1))

            df = df.iloc[1:]
            df = pd.concat([df, new_row], ignore_index=True)

            prediction = predict_vehicle_count(model_path, scalers, datetime_utc, location_name, direction, df)

            prediction_item = {}
            prediction_item['location_name'] = location_name
            prediction_item['route'] = HIGHWAY_LOCATIONS[location_name][direction]
            prediction_item['datetime'] = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
            prediction_item['number_of_vehicles_right_lane'] = int(prediction)

            predictions_by_hour.append(prediction_item)

    return predictions_by_hour