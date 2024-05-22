import sys
sys.path.append("../../../")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import os
import csv
from src.data.scrapers.locations import LOCATIONS
from datetime import datetime, timezone

URL = "https://promet.si/sl/potovalni-casi"
CONTAINER_ID = "potovalni-casi-general-card-26"
CARD_SELECTOR = "div.card.shadow-sm.moj-promet-item.mt-2"
LOCATION_SELECTOR = "div.flex-grow-1.fw-bold.text-primary"
GREEN_BADGE_SELECTOR = "div.badge.badge-green.text-white.text-right.me-1"
RED_BADGE_SELECTOR = "div.badge.badge-red.text-white.text-right.me-1"
ORANGE_BADGE_SELECTOR = "div.badge.badge-orange.text-white.text-right.me-1"

def trim_text(text):
    """
    Trims text by replacing non-alphanumeric characters with underscores.
    Example: "Avenue 123, 4th floor" -> "Avenue_123_4th_floor"
    """
    # Define a regular expression pattern to find characters that need to be trimmed
    pattern = r'[^\w\s]'
    
    # Replace non-alphanumeric characters with an underscore
    trimmed_text = re.sub(pattern, '_', text)
    
    # Replace multiple underscores with a single underscore
    trimmed_text = re.sub(r'_+', '_', trimmed_text)
    
    # Replace spaces with underscores and remove leading and trailing underscores
    trimmed_text = trimmed_text.replace(' ', '_').strip('_')
    
    # Remove all consecutive underscores
    return re.sub(r'_{2,}', '_', trimmed_text)

def convert_to_minutes(time_str):
    """
    Converts a string representing time to minutes.
    Examples: "30 min" -> 30, "1 h 30 min" -> 90
    """
    if time_str == "Zaprto":
        return 0
    
    parts = time_str.split() # Split the string by space

    if len(parts) == 2: # "30 min" or "1 h"
        if parts[1] == "min": # "30 min"
            return int(parts[0])
        else: # "1 h"
            return int(parts[0]) * 60
    elif len(parts) == 4: # "1 h 30 min"
        hours = int(parts[0])
        minutes = int(parts[2])
        return hours * 60 + minutes
    else:
        return 0  # Invalid format

def save_to_csv(datetime, location_name, travel_time_min, latitude, longitude, type):
    path = f"data/travel_times/raw/{location_name}"

    if not os.path.exists(path):
        os.makedirs(path)

    csv_file_path = f"{path}/travel_time_data.csv"
    csv_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
    
        if not csv_exists:
            writer.writerow(["datetime", "latitude", "longitude", "location_name", "minutes", "traffic_type"])
            
        writer.writerow([datetime, latitude, longitude, location_name, travel_time_min, type])

def scrape_travel_times():
    """
    Scrapers and returns current travel times for each location.
    """
    travel_times = {}
    datetime_utc = datetime.now(timezone.utc)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)

    wait = WebDriverWait(driver, 20)

    # Wait for the page to load
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    # Wait for the container to load
    wait.until(EC.presence_of_element_located((By.ID, CONTAINER_ID)))

    # Find the container
    #container = driver.find_element(By.ID, CONTAINER_ID)

    cards = driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR)

    # Extract values from cells in each card
    for card in cards:
        location_name = card.find_element(By.CSS_SELECTOR, LOCATION_SELECTOR).text
        type = "unknown"

        # Check if green badge is present, that means the road is open
        try:
            green_badge = card.find_element(By.CSS_SELECTOR, GREEN_BADGE_SELECTOR)
            if green_badge:
                time = green_badge.text
                type = "normal"
        except: pass

        try:
            orange_badge = card.find_element(By.CSS_SELECTOR, ORANGE_BADGE_SELECTOR)
            if orange_badge:
                time = orange_badge.text
                type = "medium"
        except:
            pass

        # Check if red badge is present, that means the road is closed
        try:
            red_badge = card.find_element(By.CSS_SELECTOR, RED_BADGE_SELECTOR)
            if red_badge:
                time = red_badge.text
                type = "high"
        except: pass

        #road_closed = "Zaprto" in time # Check if the road is closed
        print(f"Location: {location_name}. Time: {time}. Trimmed: {trim_text(location_name)}. Min: {convert_to_minutes(time)}")

        trimmed_location_name = trim_text(location_name)
        location = LOCATIONS[trimmed_location_name]

        travel_times[trimmed_location_name] = {
            'datetime': datetime_utc,
            'location': trimmed_location_name,
            'time': convert_to_minutes(time),
            'type': type,
            'latitude': location.Latitude,
            'longitude': location.Longitude
        }

    # Close the browser
    driver.quit()

    return travel_times

if __name__ == "__main__":
    travel_times_dictionary = scrape_travel_times()

    for location, data in travel_times_dictionary.items():
        save_to_csv(
            data['datetime'], 
            trim_text(location),
            convert_to_minutes(data['time']),
            data['latitude'],
            data['longitude'],
            data['type']
        )