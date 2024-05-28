import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.serve.utils import models_service, mlflow_service
from src.serve.utils.predict_travel_times_service import predict_travel_times_for_next_hours
from src.serve.utils.predict_vehicle_counters_service import predict_vehicle_count_for_next_hours
from src.utils.locations import LOCATIONS, HIGHWAY_LOCATIONS
import onnx
import joblib

scalers = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/travel-times/predict/{location_name}/{hours}")
async def predict_travel_times_service(location_name: str, hours: int):
    if location_name not in scalers:
        raise HTTPException(status_code=404, detail="Location not found")

    model_scalers = scalers[location_name]
    if model_scalers is None:
        raise HTTPException(status_code=404, detail="Location not found")

    predictions = predict_travel_times_for_next_hours(f'{location_name}_model.onnx', model_scalers, location_name, hours)
    print(predictions)
    return {'predictions': predictions}

@app.get("/travel-times/predict")
async def predict_travel_times_service():
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

@app.get("/travel-times/model-data/{location_name}")
async def predict_travel_times_service(location_name):
    run_id = mlflow_service.get_latest_travel_time_production_model_run_id(location_name)
    if run_id is None:
        raise HTTPException(status_code=404, detail="Model data not found")
    
    model_data = mlflow_service.get_model_data(run_id)
    return {'data': model_data}

@app.get("/vehicle-counter/routes")
async def get_vehicle_counter_routes():
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

@app.get("/vehicle-counter/model-data/{location_name}/{direction}")
async def predict_travel_times_service(location_name: str, direction: str):
    run_id = mlflow_service.get_latest_vehicle_counter_production_model_run_id(location_name, direction)
    if run_id is None:
        raise HTTPException(status_code=404, detail="Model data not found")
    
    model_data = mlflow_service.get_model_data(run_id)
    return {'data': model_data}

@app.get("/vehicle-counter/predict/{location_name}/{direction}/{hours}")
async def predict_vehicle_counter_service(location_name: str, direction: str, hours: int):
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

def load_production_models():
    print("Loading production models...")
    for location_name in LOCATIONS.keys():
        model, scalers[location_name] = models_service.fetch_current_travel_time_model(location_name)
        onnx.save(model, f'{location_name}_model.onnx')
    
if __name__ == "__main__":
    import uvicorn
    load_production_models()
    uvicorn.run(app, host="0.0.0.0", port=8000)