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

def get_last_travel_times_window(location_name, window_size=24):
    """
    Returns the last `window_size` rows from the given collection.
    """
    collection_name = 'travel_time_history'
    db = get_db_client()

    cursor = db[collection_name].find({'location_name': location_name}).sort([('datetime', -1)]).limit(window_size)
    return pd.DataFrame(list(cursor))

def get_last_vehicle_counters_window(location_name, direction, window_size=24):
    """
    Returns the last `window_size` rows from the given collection.
    """
    collection_name = 'vehicle_counter_history'
    db = get_db_client(collection_name)

    cursor = db[collection_name].find({'location_name': location_name, 'direction': direction}).sort([('datetime', -1)]).limit(window_size)
    return pd.DataFrame(list(cursor))
