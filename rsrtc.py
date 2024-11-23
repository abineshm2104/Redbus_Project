from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd


# URL of the website
URL = "https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile"

# List to hold all bus details
all_rajasthan_bus_details = []

def initialize_load_Webdriver(url):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    time.sleep(5)# Wait for the page to load
    return driver


# Function to scrape bus routes
def fetch_bus_routes(driver):
    route_list = driver.find_elements(By.CLASS_NAME, 'route')
    bus_routes_link = [route.get_attribute('href') for route in route_list]
    bus_routes_name = [route.text.strip() for route in route_list]
    return bus_routes_link, bus_routes_name

# Function to scrape bus details
def scrape_bus_details(driver, url, route_name):
    try:
        driver.get(url)
        time.sleep(5)  # Allow the page to load
        
        # Click the "View Buses" button if it exists
        try:
            view_buses_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button"))
            )
            driver.execute_script("arguments[0].click();", view_buses_button)
            time.sleep(5)  # Wait for buses to load
            
            # Scroll down to load all bus items
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for the page to load more content

           # Find bus item details
            bus_name_list = driver.find_elements(By.CLASS_NAME, "travels.lh-24.f-bold.d-color")
            bus_type_list = driver.find_elements(By.CLASS_NAME, "bus-type.f-12.m-top-16.l-color.evBus")
            departing_time_list = driver.find_elements(By.CLASS_NAME, "dp-time.f-19.d-color.f-bold")
            duration_list = driver.find_elements(By.CLASS_NAME, "dur.l-color.lh-24")
            reaching_time_list = driver.find_elements(By.CLASS_NAME, "bp-time.f-19.d-color.disp-Inline")
            star_rating_list = driver.find_elements(By.XPATH, "//div[@class='rating-sec lh-24']")
            price_list = driver.find_elements(By.CLASS_NAME, "fare.d-block")

            # Use XPath to handle both seat availability classes
            seat_availability_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'seat-left m-top-30') or contains(@class, 'seat-left m-top-16')]")

            bus_details = []
            for i in range(len(bus_name_list)):
                bus_detail = {
                    "Route_Name": route_name,
                    "Route_Link": url,
                    "Bus_Name": bus_name_list[i].text,
                    "Bus_Type": bus_type_list[i].text,
                    "Departing_Time": departing_time_list[i].text,
                    "Duration": duration_list[i].text,
                    "Reaching_Time": reaching_time_list[i].text,
                    "Star_Rating": star_rating_list[i].text if i < len(star_rating_list) else '0',
                    "Price": price_list[i].text.replace("INR",""),
                    "Seat_Availability": seat_availability_list[i].text if i < len(seat_availability_list) else '0'
                }
                bus_details.append(bus_detail)
            return bus_details
        
        except Exception as e:
            print(f"Error occurred while scraping bus details for {url}: {str(e)}")
            return []

    except Exception as e:
        print(f"Error occurred while accessing {url}: {str(e)}")
        return []



# Function to scrape all pages
def scrape_all_pages():
    for page in range(1, 3):  # There are 2 pages
        driver = initialize_load_Webdriver(URL)
        try:
            if page > 1:
                pagination_tab = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'DC_117_pageTabs')][text()='{page}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", pagination_tab)
                driver.execute_script("arguments[0].click();", pagination_tab)
                time.sleep(5)  # Wait for the page to load
            
            all_bus_routes_link, all_bus_routes_name = fetch_bus_routes(driver)
            # Iterate over each bus route link and scrape the details
            for link, name in zip(all_bus_routes_link, all_bus_routes_name):
                bus_details = scrape_bus_details(driver, link, name)
                if bus_details:
                    all_rajasthan_bus_details.extend(bus_details)
            
        except Exception as e:
            print(f"Error occurred while accessing page {page}: {str(e)}")
        finally:
            driver.quit()
# Scrape routes and details from all pages
scrape_all_pages()
# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(all_rajasthan_bus_details)

# Save the DataFrame to a CSV file
df.to_csv('rajasthan_bus_details.csv', index=False)


    
    
