import onnxruntime as rt
from keras.models import load_model
import numpy as np
import pandas as pd
import joblib
import os

# Get last 25 rows from df. 24 are used for input, 1 for target
df = pd.read_csv("data/vehicle_counters/processed/malecnik_ac/direction_mb/data.csv")
df = df.tail(25)
last_row = df.tail(1)
print(f'To predict: {last_row["number_of_vehicles_right_lane"]}')
df = df.head(24)

# Scale the input
left_lane_scaler = joblib.load("models/vehicle_counters/malecnik_ac/direction_mb/scalers/number_of_vehicles_left_lane_scaler.joblib")
right_lane_scaler = joblib.load("models/vehicle_counters/malecnik_ac/direction_mb/scalers/number_of_vehicles_right_lane_scaler.joblib")
speed_left_lane_scaler = joblib.load("models/vehicle_counters/malecnik_ac/direction_mb/scalers/speed_left_lane_scaler.joblib")
speed_right_lane_scaler = joblib.load("models/vehicle_counters/malecnik_ac/direction_mb/scalers/speed_right_lane_scaler.joblib")

df['number_of_vehicles_left_lane'] = left_lane_scaler.transform(df['number_of_vehicles_left_lane'].values.reshape(-1, 1))
df['number_of_vehicles_right_lane'] = right_lane_scaler.transform(df['number_of_vehicles_right_lane'].values.reshape(-1, 1))
df['speed_left_lane'] = speed_left_lane_scaler.transform(df['speed_left_lane'].values.reshape(-1, 1))
df['speed_right_lane'] = speed_right_lane_scaler.transform(df['speed_right_lane'].values.reshape(-1, 1))

features = ['speed_left_lane', 'speed_right_lane', 'number_of_vehicles_left_lane', 'number_of_vehicles_right_lane']
X = df[features]
X_reshaped = np.reshape(X, (1, len(features), 24))

### KERAS ###
#keras_model = load_model("models/travel_times/LJ_KP/model.keras")
#keras_prediction = keras_model.predict(X_reshaped)
#keras_prediction = minutes_scaler.inverse_transform(keras_prediction)
#print(f"Keras prediction: {keras_prediction}")

### ONNX ###
print(f"ONNX model size: {os.path.getsize('models/vehicle_counters/malecnik_ac/direction_mb/model.onnx')} bytes")

sess = rt.InferenceSession(f'models/vehicle_counters/malecnik_ac/direction_mb/model.onnx')

input_name = sess.get_inputs()[0].name
onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
onnx_predictions = onnx_predictions.reshape(1, -1)
inverse_transformed = right_lane_scaler.inverse_transform(onnx_predictions)

print(f"ONNX prediction: {inverse_transformed}")

"""
### Optimized ONNX ###
print(f"Optimized ONNX model size: {os.path.getsize('models/travel_times/LJ_KP/optimized_model.onnx')} bytes")

sess = rt.InferenceSession(f'models/travel_times/LJ_KP/optimized_model.onnx')

input_name = sess.get_inputs()[0].name
onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
onnx_predictions = onnx_predictions.reshape(1, -1)
inverse_transformed = minutes_scaler.inverse_transform(onnx_predictions)

print(f"Optimized ONNX prediction: {inverse_transformed}")

### Quantized ONNX ###
print(f"Quantized ONNX model size: {os.path.getsize('models/travel_times/LJ_KP/quantized_model.onnx')} bytes")

sess = rt.InferenceSession(f'models/travel_times/LJ_KP/quantized_model.onnx')

input_name = sess.get_inputs()[0].name
onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
onnx_predictions = onnx_predictions.reshape(1, -1)
inverse_transformed = minutes_scaler.inverse_transform(onnx_predictions)

print(f"Quantized ONNX prediction: {inverse_transformed}")
"""