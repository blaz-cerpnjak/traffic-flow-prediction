import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.serve.utils import models_service
from src.serve.utils.predict_travel_times_service import predict_travel_time
import onnx

models = {}
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

@app.get("/travel-times/predict/{location_name}")
async def predict_travel_times_service(location_name: str):
    if location_name not in models:
        raise HTTPException(status_code=404, detail="Location not found")

    if location_name not in scalers:
        raise HTTPException(status_code=404, detail="Location not found")

    model_scalers = scalers[location_name]
    if model_scalers is None:
        raise HTTPException(status_code=404, detail="Location not found")

    prediction = predict_travel_time(f'{location_name}_model.onnx', model_scalers, location_name)
    return {"prediction": int(prediction[0][0])}

def load_production_models():
    print("Loading production models...")
    models['LJ_KP'], scalers['LJ_KP'] = models_service.fetch_current_travel_time_model('LJ_KP')
    onnx.save(models['LJ_KP'], 'LJ_KP_model.onnx')
    
if __name__ == "__main__":
    import uvicorn
    load_production_models()
    uvicorn.run(app, host="0.0.0.0", port=8000)