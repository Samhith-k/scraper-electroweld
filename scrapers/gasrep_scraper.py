import time
import logging
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_gasrep_price(url, driver):
    try:
        # Validate the URL and ensure it comes from gasrep.com.au
        if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
            return np.nan
        if not url.startswith("https://gasrep.com.au"):
            return np.nan
        
        # Provided XPath with /text() removed because Selenium returns element nodes
        xpath_price = "/html/body/div[1]/main/div[2]/div[1]/div/div[2]/div[4]/div/p/span/span/bdi"
        
        driver.get(url)
        time.sleep(2)  # Adjust sleep time as needed for your connection and the site's response
        price_elements = driver.find_elements(By.XPATH, xpath_price)
        
        if not price_elements:
            return np.nan
        else:
            return price_elements[0].text.replace("$", "")

    except Exception as e:
        # Log the error if needed
        print(f"Error retrieving price from {url}: {e}")
        return np.nan

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://gasrep.com.au/shop/welders/mig-welders/viper-multi-165-mig-tig-stick-welder-u11006k/"
    price = get_gasrep_price(url, driver)
    print(price)
    driver.quit()
