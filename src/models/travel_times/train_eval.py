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

PROCESSED_DATA_DIR = '../../../data/travel_times/processed'
REPORTS_DIR = '../../../reports/travel_times'
MODELS_DIR = '../../../models/travel_times'

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
    
def train_and_evaluate(train_df, test_df, location_name, model_name):
    features = ['apparent_temperature', 'minutes'] 
    target = 'minutes'

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
        os.makedirs(f"{MODELS_DIR}/{location_name}/scalers", exist_ok=True)
        scaler_path = f"{MODELS_DIR}/{location_name}/scalers/{feature_name}_scaler.joblib"
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(scaler_path)

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

    input_shape = (len(features), window_size)

    # Create and train the model
    model = create_gru_model(input_shape)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(X_train, y_train, epochs=5, validation_split=0.2, verbose=1, callbacks=[early_stopping])

    os.makedirs(f'{REPORTS_DIR}/{location_name}', exist_ok=True)
    os.makedirs(f'{REPORTS_DIR}/{location_name}/figures', exist_ok=True)

    # Save train history plot
    plt = thp.create_plot(history, model_name)
    plt.savefig(f'{REPORTS_DIR}/{location_name}/figures/{model_name}_train_history.png')
    mlflow.log_artifact(f'{REPORTS_DIR}/{location_name}/figures/{model_name}_train_history.png')

    # Predict on test data
    scaler = preprocessor.named_transformers_['scaler_minutes']['normalize']
    y_test_inverse = scaler.inverse_transform(y_test.reshape(-1, 1))

    predictions = model.predict(X_test)
    predictions_inverse = scaler.inverse_transform(predictions)

    # Evaluate model
    mae = mean_absolute_error(y_test_inverse, predictions_inverse)
    mse = mean_squared_error(y_test_inverse, predictions_inverse)
    ev = explained_variance_score(y_test_inverse, predictions_inverse)

    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("MSE", mse)
    mlflow.log_metric("EV", ev)

    with open(f'{REPORTS_DIR}/{location_name}/train_{model_name}_metrics.txt', 'w') as f:
        f.write(f"MAE: {mae}\n")
        f.write(f"MSE: {mse}\n")
        f.write(f"EV: {ev}\n")

    df = pd.concat([train_df, test_df], ignore_index=True)

    # Inverse transform the minutes column
    df['minutes'] = scaler.inverse_transform(df['minutes'].values.reshape(-1, 1))
    
    plt = predictions_plot.create_plot(df, predictions_inverse, model_name, 'Travel time predictions', x_label='Time', y_label='Travel time (minutes)')
    plt.savefig(f'{REPORTS_DIR}/{location_name}/figures/{model_name}_predictions.png')
    mlflow.log_artifact(f'{REPORTS_DIR}/{location_name}/figures/{model_name}_predictions.png')
    
    #Convert to onnx
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=[tf.TensorSpec(shape=(None, len(features), window_size), dtype=tf.float32)])
    logged_model_name = f'{location_name}_travel_time_onnx_model'
    mlflow.onnx.log_model(onnx_model, logged_model_name)

    # Register model
    register_model(logged_model_name, mae, mse, ev)
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

def create_gru_model(input_shape):
    """
    model = Sequential([
        GRU(64, input_shape=input_shape, return_sequences=True),
        GRU(32),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.0004), loss='mean_squared_error')
    """
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