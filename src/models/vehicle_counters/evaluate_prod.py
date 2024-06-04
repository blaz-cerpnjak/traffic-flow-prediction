import sys
sys.path.append("../../../")
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
from datetime import datetime, timedelta, timezone
import src.serve.utils.db_service as db_service
import pandas as pd

def get_vehicle_counter_predictions(datetime_utc=datetime.now(timezone.utc)):
    """
    Returns travel time predictions for all locations from MongoDB.
    """
    start_date = datetime(datetime_utc.year, datetime_utc.month, datetime_utc.day)
    end_date = start_date + timedelta(days=1)

    query = {
        "datetime": {
            "$gte": start_date,
            "$lt": end_date
        }
    }

    db = db_service.get_db_client()
    results = db['vehicle_counter_predictions'].find(query).sort("datetime", 1)
    return results

def calculate_metrics(predictions_by_locations):
    db = db_service.get_db_client()
    metrics_by_location = {}

    for location, directions in predictions_by_locations.items():
        for direction, hours in directions.items():
            predicted_values = []
            actual_values = []

            for hour, values in hours.items():
                predicted_values.append(values['prediction'])
                actual_values.append(values['actual'])

            mae = mean_absolute_error(actual_values, predicted_values)
            mse = mean_squared_error(actual_values, predicted_values)
            ev = explained_variance_score(actual_values, predicted_values)

            metrics_by_location[location] = {
                'mae': mae,
                'mse': mse,
                'ev': ev
            }

            print(f"Location: {location}. Direction: {direction}")
            print(f"MAE: {mae}")
            print(f"MSE: {mse}")
            print(f"EV: {ev}")

            db['vehicle_counter_evaluations'].insert_one({
                "datetime": datetime.now(timezone.utc),
                "location_name": location,
                "direction": direction,
                "mae": mae,
                "mse": mse,
                "ev": ev
            })

if __name__ == '__main__':
    yesterday = datetime.now(timezone.utc) - timedelta(days=4)

    db = db_service.get_db_client()
    results = get_vehicle_counter_predictions(datetime_utc=yesterday)
    predictions_by_locations = {}

    for result in results:
        location_name = result['location_name']
        direction = result['direction']
        hour = pd.to_datetime(result['datetime']).hour

        prediction_time_dt = result['datetime']

        df = pd.read_csv(f'../../../data/vehicle_counters/processed/{location_name}/{direction}/data.csv')
        df['datetime'] = pd.to_datetime(df['datetime'])

        actual_value_row = df[
            (df['location_name'] == location_name) & 
            (df['datetime'].dt.date == prediction_time_dt.date()) & 
            (df['datetime'].dt.hour == prediction_time_dt.hour)
        ]
        
        if not actual_value_row.empty:
            actual_value = actual_value_row['number_of_vehicles_right_lane'].values[0]
        else:
            continue

        if location_name not in predictions_by_locations:
            predictions_by_locations[location_name] = {}

        if direction not in predictions_by_locations[location_name]:
            predictions_by_locations[location_name][direction] = {}

        if hour not in predictions_by_locations[location_name][direction]:
            predictions_by_locations[location_name][direction][hour] = { 'actual': 0, 'prediction': 0 }

        predictions_by_locations[location_name][direction][hour] = {
            'actual': actual_value,
            'prediction': result['prediction']
        }

    calculate_metrics(predictions_by_locations)