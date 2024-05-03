from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://promet.si/sl/aktualna-dela"
CONTAINER_ID = "dogodki-detail-item-66"
SEARCH_INPUT_SELECTOR = "input.form-control"
CARD_SELECTOR = "div.card.shadow-sm.fw-bold.text-primary.mb-3.cursor-pointer.moj-promet-item"

# TODO: A1, A2
def scrape():
    driver = webdriver.Chrome()
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

    # Search for A1
    search_input.send_keys("A1")
    sleep(3)

    # Find all cards in the container
    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR)))

    if not cards:
        print("No road works found")
        driver.quit()
        return
    
    for card in cards:
        print("Card:")
        div = card.find_element(By.CSS_SELECTOR, "div.d-flex.align-items-center.h-100")
        nested_div = div.find_element(By.CSS_SELECTOR, "div.flex-grow-1.text-tail-truncation.d-flex.position-relative")
        location_name = nested_div.find_element(By.CSS_SELECTOR, "div").text
        print(location_name)

    driver.quit()
    return

if __name__ == "__main__":
    scrape()

