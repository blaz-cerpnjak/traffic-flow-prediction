import sys
sys.path.append("../../../")
import os
import numpy as np
import pandas as pd
import src.visualization.predictions_plot as predictions_plot
import src.visualization.train_history_plot as thp
from keras.callbacks import EarlyStopping
from keras.layers import Dense, GRU, LSTM, SimpleRNN, Dropout
from keras.models import Sequential
from keras import Model, Input
from keras.optimizers import Adam
from keras import layers
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin
import tf2onnx
import onnx
import tensorflow as tf
import joblib
import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

PROCESSED_DATA_DIR = '../../../data/vehicle_counters/processed'
REPORTS_DIR = '../../../reports/vehicle_counters'
MODELS_DIR = '../../../models/vehicle_counters'

class CreateSequencesTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, window_size):
        self.window_size = window_size

    def fit(self, X, y=None):
        return self

    def transform(self, data):
        X, y = [], []
        for i in range(0, len(data) - self.window_size, 1):
            X.append(np.array(data.iloc[i:i + self.window_size]))
            y.append(data.iloc[i + self.window_size - 1, -1])  # -1 is the last target column (PM10)
        return np.array(X), np.array(y)
    
def train_test(train_df, test_df, location_name, direction, model_name):
    features = ['number_of_vehicles_right_lane', 'number_of_vehicles_left_lane', 'density_type_left_lane'] 
    target = ['number_of_vehicles_right_lane', 'number_of_vehicles_left_lane', 'density_type_left_lane']
    
    train_features = train_df[features]
    test_features = test_df[features]
    train_target = train_df[target]
    test_target = test_df[target]

    # Normalize the data
    scaler = MinMaxScaler()
    train_features_scaled = scaler.fit_transform(train_features)
    test_features_scaled = scaler.transform(test_features)
    train_target_scaled = scaler.transform(train_target)
    test_target_scaled = scaler.transform(test_target)

    # Save scaler
    os.makedirs(f"{MODELS_DIR}/{location_name}/{direction}/scalers", exist_ok=True)
    scaler_path = f"{MODELS_DIR}/{location_name}/{direction}/scalers/scaler.joblib"
    joblib.dump(scaler, scaler_path)

    # Prepare input data
    def prepare_data(data, window_size):
        X, y = [], []
        for i in range(len(data) - window_size):
            X.append(data[i:i+window_size])
            y.append(data[i+window_size])
        return np.array(X), np.array(y)

    window_size = 24
    X_train, y_train = prepare_data(train_features_scaled, window_size)
    X_test, y_test = prepare_data(test_features_scaled, window_size)

    input_shape = (window_size, len(features))

    # Define the model
    inputs = layers.Input(shape=input_shape)
    x = layers.GRU(64, return_sequences=True)(inputs)
    x = layers.GRU(32)(x)
    x = layers.Dense(16, activation='relu')(x)
    outputs = layers.Dense(len(target))(x)  # Output size should match the number of target variables
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=Adam(learning_rate=0.0004), loss='mean_squared_error')

    # Train the model
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    #history = model.fit(X_train, y_train, epochs=100, validation_split=0.2, verbose=1, callbacks=[early_stopping])
    history = model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1, callbacks=[early_stopping], validation_split=0.2)

    os.makedirs(f'{REPORTS_DIR}/{location_name}', exist_ok=True)
    os.makedirs(f'{REPORTS_DIR}/{location_name}/{direction}/figures', exist_ok=True)

    # Save train history plot
    plt = thp.create_plot(history, model_name)
    plt.savefig(f'{REPORTS_DIR}/{location_name}/{direction}/figures/{model_name}_train_history.png')

    # Predict
    predicted_values = model.predict(X_test)

    # Inverse transform the predicted values and target values
    predicted_values_unscaled = scaler.inverse_transform(predicted_values)
    y_test_unscaled = scaler.inverse_transform(y_test)

    # Calculate evaluation metrics separately for each target variable
    mse_right_lane = mean_squared_error(y_test_unscaled[:, 0], predicted_values_unscaled[:, 0])
    mae_right_lane = mean_absolute_error(y_test_unscaled[:, 0], predicted_values_unscaled[:, 0])
    ev_right_lane = explained_variance_score(y_test_unscaled[:, 0], predicted_values_unscaled[:, 0])

    mse_left_lane = mean_squared_error(y_test_unscaled[:, 1], predicted_values_unscaled[:, 1])
    mae_left_lane = mean_absolute_error(y_test_unscaled[:, 1], predicted_values_unscaled[:, 1])
    ev_left_lane = explained_variance_score(y_test_unscaled[:, 1], predicted_values_unscaled[:, 1])

    mse_density_type = mean_squared_error(y_test_unscaled[:, 2], predicted_values_unscaled[:, 2])
    mae_density_type = mean_absolute_error(y_test_unscaled[:, 2], predicted_values_unscaled[:, 2])
    ev_density_type = explained_variance_score(y_test_unscaled[:, 2], predicted_values_unscaled[:, 2])

    # Create a DataFrame of actual and predicted values for each target variable
    df = pd.DataFrame({
        'actual_right_lane': y_test_unscaled[:, 0],
        'predicted_right_lane': predicted_values_unscaled[:, 0],
        'actual_left_lane': y_test_unscaled[:, 1],
        'predicted_left_lane': predicted_values_unscaled[:, 1],
        'actual_density_type': y_test_unscaled[:, 2],
        'predicted_density_type': predicted_values_unscaled[:, 2]
    })

    # Save the DataFrame to a CSV file
    df.to_csv(f'{REPORTS_DIR}/{location_name}/{direction}/{model_name}_predictions.csv', index=False)

    # Save evaluation metrics to a text file
    with open(f'{REPORTS_DIR}/{location_name}/{direction}/train_{model_name}_metrics.txt', 'w') as f:
        f.write(f"Right lane - MAE: {mae_right_lane}, MSE: {mse_right_lane}, EV: {ev_right_lane}\n")
        f.write(f"Left lane - MAE: {mae_left_lane}, MSE: {mse_left_lane}, EV: {ev_left_lane}\n")
        f.write(f"Density type - MAE: {mae_density_type}, MSE: {mse_density_type}, EV: {ev_density_type}\n")

    # Convert to onnx
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=[tf.TensorSpec(shape=(None, window_size, len(features)), dtype=tf.float32)])
    model_path = f'{MODELS_DIR}/{location_name}/{direction}/model.onnx'
    onnx.save_model(onnx_model, model_path)
    return

def train_and_evaluate(train_df, test_df, location_name, direction, model_name):
    features = ['number_of_vehicles_left_lane', 'number_of_vehicles_right_lane'] 
    target = ['number_of_vehicles_right_lane']

    train_df = train_df[features]
    test_df = test_df[features]

    window_size = 24
    input_shape = (window_size, len(features))
    
    preprocessor = ColumnTransformer([
        (f"scaler_{feature}", Pipeline([
            ('fillna', SimpleImputer(strategy='mean')),
            ('normalize', MinMaxScaler())
        ]), [feature]) for feature in features
    ])

    # Fit preprocessing on train_df
    train_df = preprocessor.fit_transform(train_df)

    # Transform both train_df and test_df using the fitted preprocessor
    test_df = preprocessor.transform(test_df)

    # Save scalers
    scalers = {}
    for feature in features:
        scaler = preprocessor.named_transformers_[f"scaler_{feature}"]['normalize']
        scalers[feature] = scaler

    # Save the scalers to files
    for feature_name, scaler in scalers.items():
        os.makedirs(f"{MODELS_DIR}/{location_name}/{direction}/scalers", exist_ok=True)
        scaler_path = f"{MODELS_DIR}/{location_name}/{direction}/scalers/{feature_name}_scaler.joblib"
        joblib.dump(scaler, scaler_path)
        # TODO mlflow.log_artifact(scaler_path)

    train_df = pd.DataFrame(train_df, columns=features)
    test_df = pd.DataFrame(test_df, columns=features)

    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]

    X_train, y_train = CreateSequencesTransformer(window_size).fit_transform(X_train)
    X_test, y_test = CreateSequencesTransformer(window_size).fit_transform(X_test)

    X_train = np.reshape(X_train, (X_train.shape[0], len(features), X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], len(features), X_test.shape[1]))

    print("Reshaped X_train shape:", X_train.shape)
    print("Reshaped X_test shape:", X_test.shape)

    input_shape = (len(features), window_size)
    print("Input shape:", input_shape)

    # Create and train the model
    model = create_gru_model(input_shape)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(X_train, y_train, epochs=100, validation_split=0.2, verbose=1, callbacks=[early_stopping])

    os.makedirs(f'{REPORTS_DIR}/{location_name}', exist_ok=True)
    os.makedirs(f'{REPORTS_DIR}/{location_name}/{direction}/figures', exist_ok=True)

    # Save train history plot
    plt = thp.create_plot(history, model_name)
    plt.savefig(f'{REPORTS_DIR}/{location_name}/{direction}/figures/{model_name}_train_history.png')
    mlflow.log_artifact(f'{REPORTS_DIR}/{location_name}/{direction}/figures/{model_name}_train_history.png')

    # Predict on test data
    scaler = preprocessor.named_transformers_['scaler_number_of_vehicles_right_lane']['normalize']
    y_test_inverse = scaler.inverse_transform(y_test.reshape(-1, 1))

    predictions = model.predict(X_test)
    predictions_inverse = scaler.inverse_transform(predictions)

    # Evaluate model
    mae = mean_absolute_error(y_test_inverse, predictions_inverse)
    mse = mean_squared_error(y_test_inverse, predictions_inverse)
    ev = explained_variance_score(y_test_inverse, predictions_inverse)

    # TODO mlflow.log_metric("MAE", mae)
    # TODO mlflow.log_metric("MSE", mse)
    # TODO mlflow.log_metric("EV", ev)

    with open(f'{REPORTS_DIR}/{location_name}/{direction}/train_{model_name}_metrics.txt', 'w') as f:
        f.write(f"MAE: {mae}\n")
        f.write(f"MSE: {mse}\n")
        f.write(f"EV: {ev}\n")

    df = pd.concat([train_df, test_df], ignore_index=True)

    # Inverse transform the minutes column
    df['number_of_vehicles_right_lane'] = scaler.inverse_transform(df['number_of_vehicles_right_lane'].values.reshape(-1, 1))
    
    plt = predictions_plot.create_plot(df, predictions_inverse, model_name, 'Traffic density prediction', x_label='Time', y_label='Vehicle Counters Predictions (Right Lane)', target='number_of_vehicles_right_lane')
    plt.savefig(f'{REPORTS_DIR}/{location_name}/{direction}/figures/{model_name}_right_lane_predictions.png')

    #plt = predictions_plot.create_plot(df, predictions_inverse, model_name, 'Traffic density prediction', x_label='Time', y_label='Vehicle Counters Predictions (Left Lane)', target='number_of_vehicles_left_lane')
    #plt.savefig(f'{REPORTS_DIR}/{location_name}/{direction}/figures/{model_name}_left_lane_predictions.png')
    # TODO mlflow.log_artifact(f'{REPORTS_DIR}/{location_name}/figures/{model_name}_predictions.png')
    
    #Convert to onnx
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=[tf.TensorSpec(shape=(None, len(features), window_size), dtype=tf.float32)])
    logged_model_name = f'{location_name}_{direction}/_vehicle_counters_onnx_model'
    # TODO mlflow.onnx.log_model(onnx_model, logged_model_name)

    # Register model
    # TODO register_model(logged_model_name, mae, mse, ev)
    return

def register_model(logged_model_name, mae, mse, ev):
    client = MlflowClient()

    # Register model
    new_model_uri = f"runs:/{mlflow.active_run().info.run_id}/{logged_model_name}"
    new_registered_model = mlflow.register_model(new_model_uri, f'{logged_model_name}')

    # Check if the new model is better than the current production model
    latest_production_models = client.get_latest_versions(logged_model_name, stages=["Production"])

    if (len(latest_production_models) > 0):
        run = mlflow.get_run(latest_production_models[0].run_id)

        if (mae > run.data.metrics["MAE"]) or (mse > run.data.metrics["MSE"]) or (ev < run.data.metrics["EV"]):
            print(f"New model is not better than the current production model. Keeping the current production model...")
            return

        print(f"New model is better than the current production model. Transitioning to production...")

        # Archive the current production model
        client.transition_model_version_stage(
            name=logged_model_name,
            version=latest_production_models[0].version,
            stage="archived",
        )

    # Promote the new model to production
    client.transition_model_version_stage(
        name=logged_model_name,
        version=new_registered_model.version,
        stage="production",
    )
    return

def create_gru_model(input_shape, num_features=2):
    inputs = layers.Input(shape=input_shape)

    x = layers.GRU(64, return_sequences=True)(inputs)
    x = layers.GRU(32)(x)

    x = layers.Dense(16, activation='relu')(x)
    outputs = layers.Dense(1)(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    model.compile(optimizer=Adam(learning_rate=0.0004), loss='mean_squared_error')
    return model


def create_simple_rnn_model(input_shape):
    model = Sequential([
        SimpleRNN(64, input_shape=input_shape, return_sequences=True),
        SimpleRNN(32),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.0004), loss='mean_squared_error')
    return model


def create_lstm_model(input_shape):
    model = Sequential([
        LSTM(64, input_shape=input_shape, return_sequences=True),
        LSTM(32),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.0004), loss='mean_squared_error')
    return model


if __name__ == '__main__':
    load_dotenv()

    location_name = 'malecnik_ac'
    direction = 'direction_mb'

    path = os.path.join(PROCESSED_DATA_DIR, location_name)
    path = os.path.join(path, direction)

    train_csv_path = os.path.join(path, 'train.csv')
    test_csv_path = os.path.join(path, 'test.csv')

    if os.path.exists(train_csv_path) and os.path.exists(test_csv_path):
        train_df = pd.read_csv(train_csv_path)
        test_df = pd.read_csv(test_csv_path)

        train_test(train_df, test_df, location_name, direction, "gru")
        #train_and_evaluate(train_df, test_df, location_name, direction, "gru")

    """
    for location_name in os.listdir(PROCESSED_DATA_DIR):
        #location_name = "LJ_KP"
        print(f"Processing {location_name} data...")

        location_path = os.path.join(PROCESSED_DATA_DIR, location_name)

        if os.path.isdir(location_path):
            train_csv_path = os.path.join(location_path, 'train.csv')
            test_csv_path = os.path.join(location_path, 'test.csv')
            
            if os.path.exists(train_csv_path) and os.path.exists(test_csv_path):
                train_df = pd.read_csv(train_csv_path)
                test_df = pd.read_csv(test_csv_path)

                print(os.getenv('MLFLOW_TRACKING_URI'))

                mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
                mlflow.environment_variables.MLFLOW_TRACKING_USERNAME = os.getenv('MLFLOW_TRACKING_USERNAME')
                mlflow.environment_variables.MLFLOW_TRACKING_PASSWORD = os.getenv('MLFLOW_TRACKING_PASSWORD')
                mlflow.tensorflow.autolog()
                mlflow.set_experiment(f"{location_name}_travel_time_prediction")
                mlflow.start_run()

                train_and_evaluate(train_df, test_df, location_name, "gru")

                mlflow.end_run()
    """