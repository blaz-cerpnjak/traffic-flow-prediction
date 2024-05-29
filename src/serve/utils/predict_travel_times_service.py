import sys
sys.path.append("../../../")
import pandas as pd
import numpy as np
import onnxruntime as rt
from src.data.weather import fetch_weather_data as weather_service
from src.utils.locations import LOCATIONS, LOCATION_NAMES
import math
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import src.serve.utils.db_service as db_service


def save_prediction_to_mongodb(datetime_utc, location_name, destination, df_input, prediction):
    """
    Saves the given prediction with input data to MongoDB.
    """
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))    
    db = client["traffic_flow_predictions"]
    collection = db["travel_time_predictions"]

    item = {
        "datetime": datetime_utc,
        "location_name": location_name,
        "destination": destination, 
        "input_data": df_input.to_dict(orient='records'),
        "prediction": prediction
    }

    collection.insert_one(item)
    return

def predict_travel_time(model_path, scalers, location_name, df):
    """
    Returns travel time (minutes) prediction for next hour at the given `location_name` location.
    """
    #temperature_scaler = scalers['apparent_temperature_scaler']
    minutes_scaler = scalers['minutes_scaler']

    #df = get_last_window(location_name)
    #df['apparent_temperature'] = temperature_scaler.transform(df['apparent_temperature'].values.reshape(-1, 1))
    #df['minutes'] = minutes_scaler.transform(df['minutes'].values.reshape(-1, 1))

    features = ['apparent_temperature', 'minutes']
    X = df[features]
    X_reshaped = np.reshape(X, (1, len(features), 24))

    sess = rt.InferenceSession(model_path)
    input_name = sess.get_inputs()[0].name
    onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
    onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
    onnx_predictions = onnx_predictions.reshape(1, -1)
    inverse_transformed = minutes_scaler.inverse_transform(onnx_predictions)
    
    return inverse_transformed

def predict_travel_times_for_next_hours(model_path, scalers, location_name, hours):
    """
    Returns predictions for the next `hours` hours at the given location.
    """
    predictions_by_hour = {}
    temperature_scaler = scalers['apparent_temperature_scaler']
    minutes_scaler = scalers['minutes_scaler']

    df = db_service.get_last_travel_times_window(location_name, window_size=24)
    df['apparent_temperature'] = temperature_scaler.transform(df['apparent_temperature'].values.reshape(-1, 1))
    df['minutes'] = minutes_scaler.transform(df['minutes'].values.reshape(-1, 1))

    prediction = predict_travel_time(model_path, scalers, location_name, df)
    if math.isnan(prediction[0][0]):
        return None
    
    destination = LOCATION_NAMES[location_name]
    if destination is None:
        destination = "Unknown"

    latitude = df.iloc[-1]['latitude']
    longitude = df.iloc[-1]['longitude']
    datetime_utc = pd.to_datetime(df.iloc[-1]['datetime'])

    predictions_by_hour = []
    prediction_item = {}
    prediction_item['location'] = location_name
    prediction_item['destination'] = destination
    prediction_item['datetime'] = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    prediction_item['minutes'] = int(prediction[0][0])
    prediction_item['traffic_status'] = 'HIGH TRAFFIC' if prediction > 150 else 'MEDIUM TRAFFIC' if prediction > 100 else 'LOW TRAFFIC'
    predictions_by_hour.append(prediction_item)

    # save_prediction_to_mongodb(datetime_utc, location_name, destination, df, int(prediction[0][0]))

    if hours > 0:
        for _ in range(hours):
            datetime_utc = datetime_utc + pd.Timedelta(hours=1)
            weather_data = weather_service.fetch_weather_data(datetime_utc, latitude, longitude)
            apparent_temperature = weather_data['apparent_temperature']

            new_row = {
                'datetime': datetime_utc,
                'latitude': latitude,
                'longitude': longitude,
                'apparent_temperature': apparent_temperature,
                'minutes': prediction[0][0]
            }

            new_row = pd.DataFrame([new_row])
            new_row['apparent_temperature'] = temperature_scaler.transform(new_row['apparent_temperature'].values.reshape(-1, 1))
            new_row['minutes'] = minutes_scaler.transform(new_row['minutes'].values.reshape(-1, 1))

            df = df.iloc[1:]
            df = pd.concat([df, new_row], ignore_index=True)

            prediction = predict_travel_time(model_path, scalers, location_name, df)
            prediction_item = {}
            prediction_item['location'] = location_name
            prediction_item['destination'] = destination
            prediction_item['datetime'] = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
            prediction_item['minutes'] = int(prediction[0][0])
            prediction_item['traffic_status'] = 'HIGH TRAFFIC' if prediction > 150 else 'MEDIUM TRAFFIC' if prediction > 100 else 'LOW TRAFFIC'
            predictions_by_hour.append(prediction_item)

    return predictions_by_hour