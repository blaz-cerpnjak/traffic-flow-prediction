import sys
sys.path.append("../../../")
import pandas as pd
import numpy as np
import onnxruntime as rt
from src.data.scrapers import travel_time_scraper
from src.data.weather import fetch_weather_data as weather_service

def get_last_window(location_name, window_size=24):
    # TODO: load from mongodb
    df = pd.read_csv(f'../../data/travel_times/processed/{location_name}/data.csv')
    df = df.tail(window_size)
    return df

def predict_travel_time(model_path, scalers, location_name):
    temperature_scaler = scalers['apparent_temperature_scaler']
    minutes_scaler = scalers['minutes_scaler']

    df = get_last_window(location_name)
    df['apparent_temperature'] = temperature_scaler.transform(df['apparent_temperature'].values.reshape(-1, 1))
    df['minutes'] = minutes_scaler.transform(df['minutes'].values.reshape(-1, 1))

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