import sys
sys.path.append("../../../")
import os
import pandas as pd
from evidently.test_suite import TestSuite
from evidently.tests import TestAllColumnsShareOfMissingValues, TestNumberOfConstantColumns, TestNumberOfDuplicatedColumns, TestNumberOfDuplicatedRows, TestNumberOfColumns, TestColumnsType
import json
import src.serve.utils.db_service as db_service

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_processed_travel_time_data():
    data_path = os.path.join(SCRIPT_DIR, '../../../data/travel_times/processed/LJ_KP/data.csv')
    return pd.read_csv(data_path)

def load_processed_vehicle_count_data():
    data_path = os.path.join(SCRIPT_DIR, '../../../data/vehicle_counters/processed/malecnik_ac/direction_lj/data.csv')
    return pd.read_csv(data_path)

def test_travel_time_data():
    df = load_processed_travel_time_data()

    current = df.head(int(len(df)*0.8))
    reference = df.tail(int(len(df)*0.2))

    columns = ['datetime', 'latitude', 'longitude', 'location_name', 'number_of_vehicles_right_lane', 'number_of_vehicles_left_lane', 
               'speed_right_lane', 'speed_left_lane', 'spacing_in_sec_right_lane', 'spacing_in_sec_left_lane', 'density_type_right_lane',
               'density_type_left_lane', 'temperature', 'relative_humidity', 'dew_point', 'precipitation', 'precipitation_probability', 'rain',
               'surface_pressure', 'apparent_temperature']

    data_stability= TestSuite(tests=[
        TestAllColumnsShareOfMissingValues(columns=columns),
        TestNumberOfConstantColumns(),
        TestNumberOfDuplicatedColumns(),
        TestNumberOfDuplicatedRows(),
        TestNumberOfColumns(),
        TestColumnsType(),
    ])

    data_stability.run(current_data=current, reference_data=reference, column_mapping=None)

    report_dir = os.path.join(SCRIPT_DIR, '../../../reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    #report_path = os.path.join(report_dir, 'vehicle_count_data_quality_report.html')
    #data_stability.save_html(report_path)

    report_path = os.path.join(report_dir, 'vehicle_count_data_quality_report.json')
    data_stability.save_json(report_path)

    with open(report_path, 'r') as file:
        data = json.load(file)
        db = db_service.get_db_client()
        db['vehicle_count_data_quality_reports'].drop()
        db['vehicle_count_data_quality_reports'].insert_one(data)

def test_vehicle_counter_data():
    df = load_processed_vehicle_count_data()

    current = df.head(int(len(df)*0.8))
    reference = df.tail(int(len(df)*0.2))

    columns = ['datetime', 'latitude', 'longitude', 'location_name', 'minutes', 'traffic_type', 'temperature',
               'relative_humidity', 'dew_point', 'precipitation', 'precipitation_probability', 'rain', 'surface_pressure', 'apparent_temperature']

    data_stability= TestSuite(tests=[
        TestAllColumnsShareOfMissingValues(columns=columns),
        TestNumberOfConstantColumns(),
        TestNumberOfDuplicatedColumns(),
        TestNumberOfDuplicatedRows(),
        TestNumberOfColumns(),
        TestColumnsType(),
    ])

    data_stability.run(current_data=current, reference_data=reference, column_mapping=None)

    report_dir = os.path.join(SCRIPT_DIR, '../../../reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    #report_path = os.path.join(report_dir, 'travel_time_data_quality_report.html')
    # data_stability.save_html(report_path)

    report_path = os.path.join(report_dir, 'travel_time_data_quality_report.json')
    data_stability.save_json(report_path)

    with open(report_path, 'r') as file:
        data = json.load(file)
        db = db_service.get_db_client()
        db['travel_time_data_quality_reports'].drop()
        db['travel_time_data_quality_reports'].insert_one(data)

if __name__ == '__main__':
    test_travel_time_data()
    test_vehicle_counter_data()