import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.serve.utils import models_service, mlflow_service
from src.serve.utils.predict_travel_times_service import predict_travel_times_for_next_hours
from src.serve.utils.predict_vehicle_counters_service import predict_vehicle_count_for_next_hours
from src.utils.locations import LOCATIONS, HIGHWAY_LOCATIONS
import onnx
import joblib
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

scalers = {}

app = FastAPI(
    title="Traffic Flow Prediction API",
    description="API for predicting travel times (in minutes) and vehicle counts (per hour) for different highway locations in Slovenia.",
    version="1.0.0",
    contact={
        "name": "Blaž Čerpnjak",
        "url": "https://github.com/blaz-cerpnjak",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

def verify_api_key(token: str = Depends(oauth2_scheme)):
    if token != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden")

@app.get("/ping", summary="Ping the server", response_description="pong response")
async def ping():
    """Check if the server is running."""
    return "pong"

@app.get("/api/v1/travel-times/predict/{route}/{hours}", summary="Predict travel times for a specific location", response_description="Travel time predictions")
async def predict_travel_times_service(route: str, hours: int):
    """
    Predict travel times for a specific location and number of hours.
    - **route**: The name of the route (LJ_KP, KP_LJ...). 
    - **hours**: The number of hours to predict.
    """
    if route not in scalers:
        raise HTTPException(status_code=404, detail="Location not found")

    model_scalers = scalers[route]
    if model_scalers is None:
        raise HTTPException(status_code=404, detail="Location not found")

    predictions = predict_travel_times_for_next_hours(f'{route}_model.onnx', model_scalers, route, hours)
    print(predictions)
    return {'predictions': predictions}

@app.get("/api/v1/travel-times/predict", summary="Predict travel times for all locations", response_description="Travel time predictions for all locations")
async def predict_travel_times_service():
    """
    Predict travel times for all locations.
    """
    predictions = []

    for location_name in LOCATIONS.keys():
        if location_name not in scalers:
            continue

        model_scalers = scalers[location_name]
        if model_scalers is None:
            continue

        prediction = predict_travel_times_for_next_hours(f'{location_name}_model.onnx', model_scalers, location_name, 0)
        predictions.append(prediction)

    return {'predictions': predictions}

@app.get("/api/v1/travel-times/model-data/{route}", summary="Get travel time model data", response_description="Model data for the travel time prediction")
async def predict_travel_times_service(route: str):
    """
    Retrieve the model data for a specific location.
    - **route**: The name of the route.
    """
    run_id = mlflow_service.get_latest_travel_time_production_model_run_id(route)
    if run_id is None:
        raise HTTPException(status_code=404, detail="Model data not found")
    
    model_data = mlflow_service.get_model_data(run_id)
    return {'data': model_data}

@app.get("/api/v1/vehicle-counter/routes", summary="Get vehicle counter routes", response_description="List of vehicle counter routes")
async def get_vehicle_counter_routes():
    """
    Retrieve all vehicle counter routes.
    """ 
    routes = []

    for location, directions in HIGHWAY_LOCATIONS.items():
        for direction, value in directions.items():
            print(f'location: "{location}", direction: "{direction}", value: "{value}",')
            routes.append({
                'location': location,
                'direction': direction,
                'value': value
            })

    return {'routes': routes}

@app.get("/api/v1/vehicle-counter/model-data/{location_name}/{direction}", summary="Get vehicle counter model data", response_description="Model data for the vehicle counter")
async def get_vehicle_counter_model_data(location_name: str, direction: str):
    """
    Retrieve the model data for a specific location and direction.
    - **location_name**: The name of the location.
    - **direction**: The direction of the vehicle counter.
    """
    run_id = mlflow_service.get_latest_vehicle_counter_production_model_run_id(location_name, direction)
    if run_id is None:
        raise HTTPException(status_code=404, detail="Model data not found")
    
    model_data = mlflow_service.get_model_data(run_id)
    return {'data': model_data}

@app.get("/api/v1/vehicle-counter/predict/{location_name}/{direction}/{hours}", summary="Predict vehicle count for a specific location and direction", response_description="Vehicle count predictions")
async def predict_vehicle_counter_service(location_name: str, direction: str, hours: int):
    """
    Predict vehicle counts for a specific location, direction, and number of hours.
    - **location_name**: The name of the traffic (camera) sensor location.
    - **direction**: The direction of the vehicle counter.
    - **hours**: The number of hours to predict.
    """
    if not os.path.exists(location_name):
        os.makedirs(location_name)
    
    if not os.path.exists(f'{location_name}/{direction}'):
        os.makedirs(f'{location_name}/{direction}')

    model_path = f'{location_name}_{direction}_vehicle_counter_model.onnx'

    # Check if the model file exists
    if not os.path.exists(model_path):
        run_id = mlflow_service.get_latest_vehicle_counter_production_model_run_id(location_name, direction)
        if run_id is None:
            raise HTTPException(status_code=404, detail="Model data not found")
        
        model, scalers = models_service.fetch_current_vehicle_counter_model(location_name, direction)
        number_of_vehicle_right_lane_scaler = scalers['number_of_vehicles_right_lane_scaler']
        apparent_temperature_scaler = scalers['apparent_temperature_scaler']

        # save scalers
        with open(f'{location_name}/{direction}/number_of_vehicles_right_lane_scaler.joblib', 'wb') as f:
            joblib.dump(number_of_vehicle_right_lane_scaler, f)

        with open(f'{location_name}/{direction}/apparent_temperature_scaler.joblib', 'wb') as f:
            joblib.dump(apparent_temperature_scaler, f)

        # Save the model to a local file
        onnx.save_model(model, model_path)

    my_scalers = {}
    with open(f'{location_name}/{direction}/number_of_vehicles_right_lane_scaler.joblib', 'rb') as f:
        my_scalers['number_of_vehicles_right_lane_scaler'] = joblib.load(f)

    with open(f'{location_name}/{direction}/apparent_temperature_scaler.joblib', 'rb') as f:
        my_scalers['apparent_temperature_scaler'] = joblib.load(f)

    predictions = predict_vehicle_count_for_next_hours(
        f'{location_name}_{direction}_vehicle_counter_model.onnx', 
        my_scalers, 
        location_name, 
        direction, 
        hours
    )

    print(predictions)
    return {'predictions': predictions}

class ExperimentSearchRequest(BaseModel):
    type: str
    name: Optional[str] = None

@app.post("/api/v1/vehicle-counter/search-experiments", summary="Search Mlflow experiments", response_description="List of Mlflow experiments", dependencies=[Depends(verify_api_key)])
async def search_experiments(request: ExperimentSearchRequest):
    """
    ! Requires API key !
    Search for experiments.
    - **type**: The type of experiment.
    - **name**: Optional name of the experiment.
    """
    experiments = mlflow_service.search_experiments(int(request.type), request.name)
    return {'experiments': experiments}

@app.get("/api/v1/vehicle-counter/runs/{experiment_id}", summary="Get Mlflow runs by experiment ID", response_description="List of Mlflow runs")
async def get_runs_by_experiment_id(experiment_id: int):
    """
    Retrieve runs by experiment ID.
    - **experiment_id**: The ID of the experiment.
    """
    runs = mlflow_service.get_runs_by_experiment_id(experiment_id)
    return {'runs': runs}

class ModelSearchRequest(BaseModel):
    name: Optional[str] = None

@app.post("/api/v1/models", summary="Get registered models", response_description="List of models in Mlflow registry")
async def get_registered_models(request: ModelSearchRequest):
    """
    Retrieve registered models.
    - **name**: Optional name of the model.
    """
    models = mlflow_service.get_registered_models(request.name)
    return {'models': models}

@app.get("/api/v1/models/{model_name}", summary="Get model versions by name", response_description="List of model versions")
def get_model_versions_by_name(model_name):
    """
    Retrieve model versions by model name.
    - **model_name**: The name of the model.
    """
    model_versions = mlflow_service.get_model_version_by_name(model_name)
    return model_versions

class ChangeModelStageRequest(BaseModel):
    model_name: str
    version: str
    stage: str

@app.post("/api/v1/change-model-stage", summary="Change model stage", response_description="Confirmation message", dependencies=[Depends(verify_api_key)])
async def change_model_stage(request: ChangeModelStageRequest):
    """
    ! Requires API key !
    Change the stage of a model.
    - **model_name**: The name of the model.
    - **version**: The version of the model.
    - **stage**: The new stage of the model.
    """
    mlflow_service.change_model_stage(request.model_name, request.version, request.stage)
    return {'message': 'Model stage changed'}

def load_production_models():
    print("Loading production models...")
    for location_name in LOCATIONS.keys():
        model, scalers[location_name] = models_service.fetch_current_travel_time_model(location_name)
        print(f'Loaded model for location: {location_name}')
        onnx.save(model, f'{location_name}_model.onnx')
    
if __name__ == "__main__":
    import uvicorn
    load_dotenv()
    load_production_models()
    uvicorn.run(app, host="0.0.0.0", port=8000)