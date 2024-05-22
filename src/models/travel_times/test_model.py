import onnxruntime as rt
from keras.models import load_model
import numpy as np
import pandas as pd
import joblib

# Get last 25 rows from df. 24 are used for input, 1 for target
df = pd.read_csv("data/travel_times/processed/LJ_KP/data.csv")
df = df.tail(25)
print(f'To predict: {df.tail(1)}')
df = df.head(24)

# Scale the input
temperature_scaler = joblib.load("models/travel_times/LJ_KP/scalers/apparent_temperature_scaler.joblib")
minutes_scaler = joblib.load("models/travel_times/LJ_KP/scalers/minutes_scaler.joblib")

df['apparent_temperature'] = temperature_scaler.transform(df['apparent_temperature'].values.reshape(-1, 1))
df['minutes'] = minutes_scaler.transform(df['minutes'].values.reshape(-1, 1))

features = ['apparent_temperature', 'minutes']
X = df[features]
X_reshaped = np.reshape(X, (1, len(features), 24))

### KERAS ###
keras_model = load_model("models/travel_times/LJ_KP/model.keras")
keras_prediction = keras_model.predict(X_reshaped)
keras_prediction = minutes_scaler.inverse_transform(keras_prediction)
print(f"Keras prediction: {keras_prediction}")

### ONNX ###
sess = rt.InferenceSession(f'models/travel_times/LJ_KP/model.onnx')

input_name = sess.get_inputs()[0].name
onnx_predictions = sess.run(None, {input_name: X_reshaped.astype(np.float32)})
onnx_predictions = onnx_predictions[0]  # Select the first element (prediction)
onnx_predictions = onnx_predictions.reshape(1, -1)
inverse_transformed = minutes_scaler.inverse_transform(onnx_predictions)

print(f"ONNX prediction: {inverse_transformed}")