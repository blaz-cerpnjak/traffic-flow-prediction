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
    
    print(latest_production_models[0].run_id)
    return latest_production_models[0].run_id

def get_model_data(run_id):
    client = MlflowClient()
    data = client.get_run(run_id).data
    return data

"""
def get_metric_history(run_id, metric):
    client = MlflowClient()
    history = client.get_metric_history(run_id, metric)
    return history
"""

def search_experiments(view_type: int = 1, name: str = None):
    """
    Type: 1 = Active, 2 = Deleted, 3 = All
    """
    client = MlflowClient()
    
    if (name is not None):
        experiments = client.search_experiments(view_type=view_type, filter_string=f"name LIKE '%{name}%'")
    else:
        experiments = client.search_experiments(view_type=view_type)
    
    return experiments

def get_runs_by_experiment_id(experiment_id):
    client = MlflowClient()
    runs = client.search_runs(experiment_ids=[experiment_id])
    return runs

def get_registered_models(name: None,):
    client = MlflowClient()

    query = ""
    if name is not None:
        query = f"name LIKE '%{name}%'"

    return client.search_registered_models(filter_string=query)

def get_model_version_by_name(name):
    client = MlflowClient()
    return client.search_model_versions(f"name LIKE '%{name}%'")

def change_model_stage(model_name, version, stage):
    client = MlflowClient()

    if stage == "production":
        latest_production_models = client.get_latest_versions(model_name, stages=["Production"])

        if len(latest_production_models) > 0:
            # Archive the current production model
            client.transition_model_version_stage(
                name=model_name, 
                version=latest_production_models[0].version,
                stage="archived",
            )

    # Promote the new model to production
    client.transition_model_version_stage(name=model_name,version=version, stage=stage)
    return