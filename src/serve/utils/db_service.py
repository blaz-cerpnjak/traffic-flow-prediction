import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import json

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
    Returns the last `window_size` rows from the given `location_name`.
    """
    db = get_db_client()
    cursor = db['travel_time_history'].find({'location_name': location_name}).sort([('datetime', 1)]).limit(window_size)
    df = pd.DataFrame(list(cursor))
    if df.empty:
        raise ValueError("Last travel time window data not found")

    df.columns = df.columns.str.strip()
    df.drop(columns=['_id'], inplace=True)
    return df

    # get from csv
    #df = pd.read_csv(f'../../data/travel_times/processed/{location_name}/data.csv')
    #return df.tail(window_size)

def get_last_vehicle_counters_window(location_name, direction, window_size=24):
    """
    Returns the last `window_size` rows from the given collection.
    """
    db = get_db_client()
    cursor = db['vehicle_counter_history'].find({'location_name': location_name, 'direction': direction}).sort([('datetime', 1)]).limit(window_size)
    df = pd.DataFrame(list(cursor))
    if df.empty:
        raise ValueError("Last travel time window data not found")

    df.columns = df.columns.str.strip()
    df.drop(columns=['_id'], inplace=True)
    return df

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

def replace_travel_time_history_db():
    """
    Refreshes the travel time history database collection.
    """
    raw_data_dir = 'data/travel_times/processed'
    db = get_db_client()
    db['travel_time_history'].drop()

    for location in os.listdir(raw_data_dir):
        location_dir = os.path.join(raw_data_dir, location)
        data_path = os.path.join(location_dir, 'data.csv')
        print(data_path)

        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            db['travel_time_history'].insert_many(df.to_dict(orient='records'))
            continue

def get_latest_data_test_report(collection_name):
    """
    Returns the latest travel times data test report.
    """
    print(collection_name)
    db = get_db_client()
    latest_report = db[collection_name].find_one({}, sort=[('_id', -1)]) 
    latest_report['_id'] = str(latest_report['_id']) # Convert ObjectId to string
    return latest_report

def get_latest_data_drift_report(collection_name):
    """
    Returns the latest travel times data drift report.
    """
    db = get_db_client()
    latest_report = db[collection_name].find_one({}, sort=[('_id', -1)]) 
    latest_report['_id'] = str(latest_report['_id']) # Convert ObjectId to string
    return latest_report

def get_travel_time_evaluations():
    """
    Returns the travel time evaluations.
    """
    db = get_db_client()
    cursor = db['travel_time_evalutations'].find({})
    documents = list(cursor)
    for doc in documents:
        doc['_id'] = str(doc['_id']) # Convert ObjectId to string
    return documents

def get_vehicle_counter_evaluations():
    """
    Returns the vehicle counter evaluations.
    """
    db = get_db_client()
    cursor = db['vehicle_counter_evaluations'].find({})
    documents = list(cursor)
    for doc in documents:
        doc['_id'] = str(doc['_id']) # Convert ObjectId to string
    return documents

if __name__ == '__main__':
    replace_travel_time_history_db()
    print("Travel time history database refreshed.")
    pass