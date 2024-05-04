import os
import csv
from time import sleep
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from locations import HIGHWAY_LOCATIONS

URL = "https://promet.si/sl/stevci-prometa"
CONTAINER_ID = "stevci-detail-container-34"
CARD_SELECTOR = "div.card.shadow-sm.moj-promet-item.mt-3"
LOCATION_SELECTOR = "div.col-2:nth-child(1)"
DIRECTION_SELECTOR = "div.col-2:nth-child(2)"
ROAD_LANE_SELECTOR = "div.col-2:nth-child(3)"
NUMBER_OF_VEHICLES_SELECTOR = "div.col-2:nth-child(4)"
SPEED_SELECTOR = "div.col-2:nth-child(5)"
VEHICLE_SPACING_SELECTOR = "div.col-1"
SEARCH_INPUT_SELECTOR = "input.form-control"

def append_csv_row(location_name, direction, row):
    path = f"data/vehicle_counters/raw/{location_name}/{direction}"

    if not os.path.exists(path):
        os.makedirs(path)

    csv_file_path = f"{path}/counters_data.csv"
    csv_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not csv_exists:
            writer.writerow(["datetime", "location_name", "number_of_vehicles_right_lane", "number_of_vehicles_left_lane",
                             "speed_right_lane", "speed_left_lane", "spacing_in_sec_right_lane", "spacing_in_sec_right_lane",
                             "density_type_right_lane", "density_type_left_lane"])
            
        writer.writerow([row["datetime"], row["location_name"], row["number_of_vehicles_right_lane"], row["number_of_vehicles_left_lane"],
                        row["speed_right_lane"], row["speed_left_lane"], row["spacing_in_sec_right_lane"], row["spacing_in_sec_right_lane"],
                        row["density_type_right_lane"], row["density_type_left_lane"]])

def search_traffic_counters_by_location(datetime_utc, location_name, direction, search_query, search_input, driver, wait):
    # Search for traffic counters data
    search_input.clear()
    search_input.send_keys(search_query)

    sleep(1)

    cards_wrapper = driver.find_element(By.ID, "stevci-detail-wrapper-34")

    # Scroll to the bottom of the container repeatedly until no new cards are found
    last_height = driver.execute_script("return arguments[0].scrollHeight", cards_wrapper)
    while True:
        print("Scrolling...")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", cards_wrapper)
        sleep(0.5)
        new_height = driver.execute_script("return arguments[0].scrollHeight", cards_wrapper)
        if new_height == last_height:
            break
        last_height = new_height

    # Find all cards in the container
    try:
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR)))
    except:
        print("No data found")
        return

    csv_row = {}
    csv_row["datetime"] = datetime_utc
    csv_row["location_name"] = location_name

    # Extract values from cells in each card
    for card in cards:
        # location = card.find_element(By.CSS_SELECTOR, LOCATION_SELECTOR).text
        # direction = card.find_element(By.CSS_SELECTOR, DIRECTION_SELECTOR).text
        road_lane = card.find_element(By.CSS_SELECTOR, ROAD_LANE_SELECTOR).text
        number_of_vehicles = card.find_element(By.CSS_SELECTOR, NUMBER_OF_VEHICLES_SELECTOR).text
        speed = card.find_element(By.CSS_SELECTOR, SPEED_SELECTOR).text
        spacing = card.find_element(By.CSS_SELECTOR, VEHICLE_SPACING_SELECTOR).text

        img = card.find_element(By.CSS_SELECTOR, "img.list-item-icon")
        if img:
            image_source = img.get_attribute("src")
            density_type = 0 # 0 - no data, 1 - green, 2 - orange, 3 - red

        if image_source == None or "stevec_white" in image_source:
            density_type = 0
        elif "stevec_green" in image_source:
            density_type = 1
        elif "stevec_orange" in image_source:
            density_type = 2
        elif "stevec_red" in image_source:
            density_type = 3

        if "vozni" in road_lane:
            csv_row["number_of_vehicles_right_lane"] = number_of_vehicles
            csv_row["speed_right_lane"] = speed
            csv_row["spacing_in_sec_right_lane"] = spacing
            csv_row["density_type_right_lane"] = density_type
        elif "prehitevalni" in road_lane:
            csv_row["number_of_vehicles_left_lane"] = number_of_vehicles
            csv_row["speed_left_lane"] = speed
            csv_row["spacing_in_sec_left_lane"] = spacing
            csv_row["density_type_left_lane"] = density_type
        
        #print(f"Location: {location_name}. Direction: {direction}. Lane: {road_lane}. Number: {number_of_vehicles}. Speed:{speed} km/h. Spacing: {spacing}s. Type: {density_type}")
    
    append_csv_row(location_name, direction, csv_row)

def scrape():
    """
    Scrapes traffic counters data (number of vehicles, speed, spacing)
    """
    datetime_utc = datetime.now(timezone.utc)

    chrome_options = Options()
    #chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    wait = WebDriverWait(driver, 20)

    # Wait for the page to load
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    # Wait for the container to load
    wait.until(EC.presence_of_element_located((By.ID, CONTAINER_ID)))

    # Find the search input
    search_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR))
    )

    # Search traffic counters by locations names
    for highway_location in HIGHWAY_LOCATIONS:
        # print(highway_location)
        location_details = HIGHWAY_LOCATIONS[highway_location]

        for direction, location_name in location_details.items():
            # print(f"  - {direction}: {location_name}")
            search_traffic_counters_by_location(
                datetime_utc=datetime_utc,
                location_name=highway_location,
                direction=direction,
                search_query=location_name, 
                search_input=search_input,
                driver=driver,
                wait=wait)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    scrape()