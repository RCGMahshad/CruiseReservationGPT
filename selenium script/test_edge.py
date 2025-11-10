from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_driver():
    # Configure Edge options
    edge_options = Options()
    edge_options.add_argument('--log-level=3')  # Suppress console logs
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress DevTools logging
    
    # Setup the service with the driver path
    service = Service(r'C:\Users\h0uz6\Documents\CruiseReservationGPT\msedgedriver.exe')
    
    # Create and return the driver instance
    return webdriver.Edge(service=service, options=edge_options)

try:
    # Initialize the driver
    driver = setup_driver()
    
    # Set implicit wait time
    driver.implicitly_wait(100)
    
    # Navigate to Royal Caribbean website
    print("Navigating to Royal Caribbean website...")
    driver.get("https://www.royalcaribbean.com/cruises?search=ship:IC&country=USA&icid=yrfcns_tctclp_cs:_hm_hero_4146")
    
    # Wait for the page to load (wait for the logo or a main element)
    wait = WebDriverWait(driver, 100)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "header")))

    link = driver.find_element(By.LINK_TEXT, "BOOK NOW")
    link.click()
    
    print(f"Successfully loaded: {driver.title}")

except TimeoutException:
    print("Timeout: Page took too long to load")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # Ensure the driver is closed properly
    if 'driver' in locals():
        driver.quit()
        print("Browser closed successfully")
