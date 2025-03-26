from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import time

def get_sydney_tools_price(url, driver):
    # Validate the URL: if empty or doesn't start with the expected prefix, return np.nan
    if not url or not isinstance(url, str) or not url.startswith("https://sydneytools.com.au/product"):
        return np.nan
    if not url or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://sydneytools.com.au/product"):
        return np.nan

    try:
        # Navigate to the product page
        driver.get(url)
        
        # Wait for the page to load dynamic content
        time.sleep(2)
        
        # Try to extract the price using the exact XPath provided
        try:
            # The parts of the price
            price_xpath = (
                "/html/body/div[1]/div/div/section/section/div[2]/div/div/div[3]/div[2]/div[3]/div/div[2]/span[2]"
            )
            price_element = driver.find_element(By.XPATH, price_xpath)
            
            dollar_xpath = (
                "/html/body/div[1]/div/div/section/section/div[2]/div/div/div[3]/div[2]/div[3]/div/div[2]/span[1]"
            )
            dollar_element = driver.find_element(By.XPATH, dollar_xpath)
            
            decimal_xpath = (
                "/html/body/div[1]/div/div/section/section/div[2]/div/div/div[3]/div[2]/div[3]/div/div[2]/span[3]"
            )
            decimal_element = driver.find_element(By.XPATH, decimal_xpath)
            
            cents_xpath = (
                "/html/body/div[1]/div/div/section/section/div[2]/div/div/div[3]/div[2]/div[3]/div/div[2]/span[4]"
            )
            cents_element = driver.find_element(By.XPATH, cents_xpath)
            
            # Combine the parts
            price = dollar_element.text + price_element.text + decimal_element.text + cents_element.text
            return price.strip()
            
        except NoSuchElementException:
            # If the specific XPath fails, try a fallback using a CSS selector
            try:
                price_container = driver.find_element(By.CSS_SELECTOR, "div.price")
                return price_container.text.strip()
            except NoSuchElementException:
                return np.nan
    
    except Exception as e:
        #print(f"Error extracting price: {e}")
        return np.nan

# Example usage
if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the driver using webdriver_manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Provide a valid Sydney Tools product URL here
    url = "https://sydneytools.com.au/product/unimig-u12002k-240v-90kva-razor-tig-200-acdc-welder"  # Replace with an actual product URL
    price = get_sydney_tools_price(url, driver)
    print(f"Price: {price}")
    
    driver.quit()
