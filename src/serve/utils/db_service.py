import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

def get_db_client():
    """
    Connects to the MongoDB server and returns the database client.
    """
    load_dotenv()
    client = MongoClient(os.getenv("MONGO_URI"))    
    return client[os.getenv("MONGO_DB_NAME")]

def save_to_collection(collection_name, df_row):
    """
    Saves the given df_row data to MongoDB collection.
    """
    db = get_db_client()
    db[collection_name].insert_one(df_row.to_dict())

def get_travel_times_by_date(location_name, date):
    """
    Returns the travel times for the given location and date.
    """
    db = get_db_client()
    cursor = db['travel_time_history'].find({'location_name': location_name, 'datetime': {'$gte': date, '$lt': date + pd.Timedelta(days=1)}})
    return pd.DataFrame(list(cursor))

def get_last_travel_times_window(location_name, window_size=24):
    """
    Returns the last `window_size` rows from the given collection.
    """
    db = get_db_client()
    cursor = db['travel_time_history'].find({'location_name': location_name}).sort([('datetime', -1)]).limit(window_size)
    return pd.DataFrame(list(cursor))

    # get from csv
    #df = pd.read_csv(f'../../data/travel_times/processed/{location_name}/data.csv')
    #return df.tail(window_size)

def get_last_vehicle_counters_window(location_name, direction, window_size=24):
    """
    Returns the last `window_size` rows from the given collection.
    """
    db = get_db_client()

    cursor = db['vehicle_counter_history'].find({'location_name': location_name, 'direction': direction}).sort([('datetime', -1)]).limit(window_size)
    return pd.DataFrame(list(cursor))

def save_travel_time_prediction(datetime_utc, location_name, destination, df_input, prediction):
    """
    Saves the given prediction with input data to MongoDB.
    """
    db = get_db_client()
    existing_predictions = db['travel_time_predictions'].find({'location_name': location_name, 'datetime': datetime_utc})
    count = sum(1 for _ in existing_predictions)

    if existing_predictions is not None and count > 0:
        # Update the existing prediction
        print("Updating existing prediction")
        db['travel_time_predictions'].update_one({'location_name': location_name, 'datetime': datetime_utc}, {'$set': {'prediction': prediction}})
        return

    print("Saving new prediction")

    db['travel_time_predictions'].insert_one({
        "datetime": datetime_utc,
        "location_name": location_name,
        "destination": destination, 
        "input_data": df_input.to_dict(orient='records'),
        "prediction": prediction
    })
    return

def save_vehicle_counter_prediction(datetime_utc, location_name, direction, df_input, prediction):
    """
    Saves the given prediction with input data to MongoDB.
    """
    db = get_db_client()
    existing_predictions = db['vehicle_counter_predictions'].find({'location_name': location_name, 'direction': direction, 'datetime': datetime_utc})
    count = sum(1 for _ in existing_predictions)

    if existing_predictions is not None and count > 0:
        # Update the existing prediction
        print("Updating existing prediction")
        db['vehicle_counter_predictions'].update_one({'location_name': location_name, 'direction': direction, 'datetime': datetime_utc}, {'$set': {'prediction': prediction}})
        return

    print("Saving new prediction")

    db['vehicle_counter_predictions'].insert_one({
        "datetime": datetime_utc,
        "location_name": location_name,
        "direction": direction,
        "input_data": df_input.to_dict(orient='records'),
        "prediction": prediction
    })
    return