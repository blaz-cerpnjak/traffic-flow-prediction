import mlflow
from mlflow.tracking import MlflowClient

def get_latest_travel_time_production_model_run_id(location_name):
    logged_model_name = f'{location_name}_travel_time_onnx_model'

    client = MlflowClient()
    latest_production_models = client.get_latest_versions(logged_model_name, stages=["Production"])

    if (len(latest_production_models) <= 0):
        return None
    
    return latest_production_models[0].run_id

def get_latest_vehicle_counter_production_model_run_id(location_name, direction):
    logged_model_name = f'{location_name}_{direction}_vehicle_counter_onnx_model'

    client = MlflowClient()
    latest_production_models = client.get_latest_versions(logged_model_name, stages=["Production"])

    if (len(latest_production_models) <= 0):
        return None
    
    return latest_production_models[0].run_id

def get_model_data(run_id):
    client = MlflowClient()
    data = client.get_run(run_id).data
    return data

if __name__ == "__main__":
    location_name = "LJ_KP"
    run_id = get_latest_travel_time_production_model_run_id(location_name)
    if run_id is not None:
        get_model_data(run_id)
    else:
        print(f"No production model found for {location_name}")