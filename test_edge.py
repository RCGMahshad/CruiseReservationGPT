from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlencode
from datetime import datetime
import time

def setup_driver():
    # Configure Edge options
    edge_options = Options()
    edge_options.add_argument('--log-level=3')  # Suppress console logs
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress DevTools logging
    
    # Setup the service with the driver path
    service = Service(r'C:\Users\h0uz6\Documents\CruiseReservationGPT\msedgedriver.exe')
    
    # Create and return the driver instance
    return webdriver.Edge(service=service, options=edge_options)

def build_royal_caribbean_url(
    departure_ports=None,
    nights_range=None,
    start_date=None,
    end_date=None,
    ship=None,
    country="USA"
):
    # Base URL components
    base_url = "https://www.royalcaribbean.com/cruises"
    icid = "yrfcns_tctclp_cs:_hm_hero_4146"
    
    # Initialize search parameters
    search_params = []
    
    # Add departure ports
    if departure_ports:
        ports_str = ",".join(departure_ports)
        search_params.append(f"departurePort:{ports_str}")
    
    # Add nights range
    if nights_range:
        search_params.append(f"nights:{nights_range[0]}~{nights_range[1]}")
    
    # Add date range
    if start_date and end_date:
        search_params.append(f"startDate:{start_date}~{end_date}")
    
    # Add ship
    if ship:
        search_params.append(f"ship:{ship}")
    
    # Combine search parameters
    search_string = "|".join(search_params)
    
    # Build query parameters
    query_params = {
        "search": search_string,
        "country": country,
        "icid": icid
    }
    
    # Construct final URL
    final_url = f"{base_url}?{urlencode(query_params)}"
    return final_url

def get_user_input():
    print("\n=== Royal Caribbean Cruise Search ===")
    
    # Get ship code
    ship = input("Enter ship code (e.g., AN for Anthem, or press Enter to skip): ").strip() or None
    
    # Get departure ports if no ship specified
    departure_ports = None
    if not ship:
        ports_input = input("Enter departure ports (comma-separated, e.g., FLL,MIA): ").strip()
        if ports_input:
            departure_ports = [p.strip() for p in ports_input.split(',')]
    
    # Get nights range
    min_nights = int(input("Enter minimum nights: "))
    max_nights = int(input("Enter maximum nights: "))
    
    # Get date range
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    
    # Create search parameters dictionary
    search_params = {
        "ship": ship,
        "departure_ports": departure_ports,
        "nights_range": (min_nights, max_nights),
        "start_date": start_date,
        "end_date": end_date,
        "country": "USA"  # Default to USA
    }
    
    return search_params

def search_cruises(search_params):
    driver = None
    try:
        # Initialize the driver
        driver = setup_driver()
        
        # Set implicit wait time
        driver.implicitly_wait(10)
        
        # Build and navigate to the URL
        url = build_royal_caribbean_url(**search_params)
        print(f"\nNavigating to URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "header")))
        
        print(f"Successfully loaded: {driver.title}")
        
        # Add a longer wait for the search results to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cruise-card, .no-results-container")))
        
        # Example of how to click a button by ID
        # Replace 'your-button-id' with the actual button ID
        button_id = input("\nEnter the button ID to click (or press Enter to skip): ").strip()
        if button_id:
            if click_button(driver, button_id):
                # Wait after clicking to allow for any page changes
                time.sleep(2)
        print(url)
        return True

    except TimeoutException:
        print("Timeout: Page took too long to load")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    finally:
        # Ensure the driver is closed properly
        if driver:
            driver.quit()
            print("Browser closed successfully")

    


def click_view_dates_button(driver, index=0):
    try:
        # Wait for cruise cards to be present
        wait = WebDriverWait(driver, 10)
        
        # Find all "View dates" buttons using the specific class combination
        buttons = wait.until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, 
                "button.RefinedCruiseCard-styles__RefinedCruiseCardButton-sc-769f74cd-13[data-testid^='cruise-view-dates-button']"
            ))
        )
        
        if not buttons:
            print("No 'View dates' buttons found")
            return False
            
        if index >= len(buttons):
            print(f"Button index {index} is out of range. Only {len(buttons)} buttons found.")
            return False
            
        # Get the specified button
        button = buttons[index]
        
        # Print some information about the button
        button_id = button.get_attribute('id')
        button_text = button.text
        print(f"Found button: ID={button_id}, Text={button_text}")
        
        # Scroll the button into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)  # Wait for scroll to complete
        
        # Click the button
        button.click()
        print("Successfully clicked the 'View dates' button")
        
        return True
        
    except TimeoutException:
        print("Timeout: No 'View dates' buttons found on the page")
        return False
    except Exception as e:
        print(f"Error clicking button: {str(e)}")
        return False

def get_example_params():
    """Returns example search parameters for testing"""
    return {
        "ship": "AN",                      # Anthem of the Seas
        "departure_ports": None,           # Not needed when searching by ship
        "nights_range": (2, 5),           # 2-5 nights
        "start_date": "2026-01-01",       # Start date
        "end_date": "2026-01-31",         # End date
        "country": "USA"                   # Country
    }

if __name__ == "__main__":
    while True:
        print("\n=== Royal Caribbean Cruise Search ===")
        print("1. Enter search parameters manually")
        print("2. Use example parameters")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            params = get_user_input()
            success = search_cruises(params)
            if success:
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            print("\nUsing example parameters:")
            params = get_example_params()
            print(f"Departure Ports: {params['departure_ports']}")
            print(f"Nights Range: {params['nights_range']}")
            print(f"Date Range: {params['start_date']} to {params['end_date']}")
            
            if input("\nProceed with these parameters? (y/n): ").lower().startswith('y'):
                success = search_cruises(params)
                if success:
                    input("\nPress Enter to continue...")
        
        elif choice == "3":
            print("\nExiting program...")
            break
        
        else:
            print("\nInvalid choice. Please try again.")