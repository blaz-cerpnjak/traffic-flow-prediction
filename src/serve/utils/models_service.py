import os
import mlflow
import joblib
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv

def fetch_current_travel_time_model(location_name):
    """
    Fetches and returns the current production model with scalers for predicting travel times for the given location.
    Model gets fetched from Mlfow model registry.
    """
    load_dotenv()

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    mlflow_username = os.getenv("MLFLOW_USERNAME")
    mlflow_password = os.getenv("MLFLOW_PASSWORD")

    mlflow.environment_variables.MLFLOW_TRACKING_USERNAME = mlflow_username
    mlflow.environment_variables.MLFLOW_TRACKING_PASSWORD = mlflow_password
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    client = MlflowClient()
    
    model_name = f"{location_name}_travel_time_onnx_model"
    latest_production_models = client.get_latest_versions(model_name, stages=["Production"])
    if len(latest_production_models) == 0:
        print(f"No production model found for {location_name}")
        return None, None

    latest_model_uri = latest_production_models[0].source

    # Download the current production model
    model = mlflow.onnx.load_model(latest_model_uri)

    # Get the run associated with the model version
    run_id = latest_production_models[0].run_id

    # Download the scalers
    local_path = client.download_artifacts(run_id, "minutes_scaler.joblib", ".")
    minutes_scaler = joblib.load(local_path)

    local_path = client.download_artifacts(run_id, "apparent_temperature_scaler.joblib", ".")
    temperature_scaler = joblib.load(local_path)

    if minutes_scaler is None or temperature_scaler is None:
        print(f"Scalers not found for {location_name}")
        return None, None
    
    scalers = {
        "minutes_scaler": minutes_scaler,
        "apparent_temperature_scaler": temperature_scaler
    }

    return model, scalers

def fetch_current_vehicle_counter_model(location_name, direction):
    """
    Fetches and returns the current production model with scalers for predicting vehicle counters for the given location and direction.
    Model gets fetched from Mlfow model registry.
    """
    load_dotenv()

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    mlflow_username = os.getenv("MLFLOW_USERNAME")
    mlflow_password = os.getenv("MLFLOW_PASSWORD")

    mlflow.environment_variables.MLFLOW_TRACKING_USERNAME = mlflow_username
    mlflow.environment_variables.MLFLOW_TRACKING_PASSWORD = mlflow_password
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    client = MlflowClient()
    
    model_name = f"{location_name}_{direction}_vehicle_counter_onnx_model"
    latest_production_models = client.get_latest_versions(model_name, stages=["Production"])
    if len(latest_production_models) == 0:
        print(f"No production model found for {location_name}")
        return None, None

    latest_model_uri = latest_production_models[0].source

    # Download the current production model
    model = mlflow.onnx.load_model(latest_model_uri)

    # Get the run associated with the model version
    run_id = latest_production_models[0].run_id

    # Download the scalers
    local_path = client.download_artifacts(run_id, "number_of_vehicles_left_lane_scaler.joblib", ".")
    number_of_vehicles_left_lane_scaler = joblib.load(local_path)

    local_path = client.download_artifacts(run_id, "number_of_vehicles_right_lane_scaler.joblib", ".")
    number_of_vehicles_right_lane_scaler = joblib.load(local_path)

    local_path = client.download_artifacts(run_id, "speed_left_lane_scaler.joblib", ".")
    speed_left_lane_scaler = joblib.load(local_path)

    local_path = client.download_artifacts(run_id, "speed_right_lane_scaler.joblib", ".")
    speed_right_lane_scaler = joblib.load(local_path)

    if number_of_vehicles_left_lane_scaler is None or number_of_vehicles_right_lane_scaler is None or speed_left_lane_scaler is None or speed_right_lane_scaler is None:
        print(f"Scalers not found for {location_name} - {direction}")
        return None, None
    
    scalers = {
        "number_of_vehicles_left_lane_scaler": number_of_vehicles_left_lane_scaler,
        "number_of_vehicles_right_lane_scaler": number_of_vehicles_right_lane_scaler,
        "speed_left_lane_scaler": speed_left_lane_scaler,
        "speed_right_lane_scaler": speed_right_lane_scaler
    }

    return model, scalers