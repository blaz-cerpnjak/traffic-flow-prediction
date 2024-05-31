import sys
sys.path.append("../../../")
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
from datetime import datetime, timedelta, timezone
import src.serve.utils.db_service as db_service

def get_actual_travel_times(datetime_utc=datetime.now(timezone.utc)):
    """
    Returns travel time for all locations from MongoDB.
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
    results = db['travel_time_history'].find()

    return results

def get_travel_time_predictions(datetime_utc=datetime.now(timezone.utc)):
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
    results = db['travel_time_predictions'].find(query)
    return results

def evaluate_predictions(actual_by_location, predictions_by_location):
    """
    Returns MAE, MSE and EV scores for the given actual values and predictions.
    """

    mae_by_location = {}
    mse_by_location = {}
    ev_by_location = {}

    for location in actual_by_location.keys():
        actual_values = actual_by_location[location]
        predictions = predictions_by_location[location]

        mae = mean_absolute_error(actual_values, predictions)
        mse = mean_squared_error(actual_values, predictions)
        ev = explained_variance_score(actual_values, predictions)

        mae_by_location[location] = mae
        mse_by_location[location] = mse
        ev_by_location[location] = ev

if __name__ == '__main__':
    results = get_actual_travel_times()

    actual_by_locations = {}

    for result in results:
        location_name = result['location_name']
        if location_name not in actual_by_locations:
            actual_by_locations[location_name] = []

        actual_by_locations[location_name].append(result['minutes'])

    results = get_travel_time_predictions()

    predictions_by_locations = {}

    for result in results:
        location_name = result['location_name']
        if location_name not in predictions_by_locations:
            predictions_by_locations[location_name] = []

        predictions_by_locations[location_name].append(result['prediction'])