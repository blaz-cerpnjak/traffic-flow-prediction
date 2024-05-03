import os
import csv
from time import sleep
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

def save_travel_time_to_csv(datetime, location_name, direction, road_lane, number_of_vehicles, speed, spacing, density_type):
    path = f"data/traffic_density/raw/{location_name}"

    if not os.path.exists(path):
        os.makedirs(path)

    csv_file_path = f"{path}/density_data.csv"
    csv_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not csv_exists:
            writer.writerow(["datetime", "location_name", "direction", "road_lane", "number_of_vehicles", "speed", "spacing_in_seconds", "density_type"])
            
        writer.writerow([datetime, location_name, direction, road_lane, number_of_vehicles, speed, spacing, density_type])

def scrape():
    """
    Scrapes traffic density data (number of vehicles, speed, spacing)
    """
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

     # Find the search input
    search_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR))
    )

    for search_query in ["AC-A1", "AC-A2"]:
        # Search for road works
        search_input.clear()
        search_input.send_keys(search_query)

        sleep(3)

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
            continue

        # Extract values from cells in each card
        for card in cards:
            location = card.find_element(By.CSS_SELECTOR, LOCATION_SELECTOR).text
            direction = card.find_element(By.CSS_SELECTOR, DIRECTION_SELECTOR).text
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

            # print(f"Location: {location}. Direction: {direction}. Lane: {road_lane}. Number: {number_of_vehicles}. Speed:{speed} km/h. Spacing: {spacing}s. Type: {density_type}")
            save_travel_time_to_csv(datetime_utc, location, direction, road_lane, number_of_vehicles, speed, spacing, density_type)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    scrape()