import time
import logging
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Set up debug logging

def get_hares_and_forbes_price(url, driver):
    try:
        # Check if the URL is valid and starts with the expected domain.
        if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
            return np.nan
        if not url.startswith("https://www.machineryhouse.com.au"):
            return np.nan
                    
        xpath_price = "/html/body/div[1]/div[3]/main/section/div/div[4]/div[2]/div[1]/div[3]/div/div[2]/span"
        xpath_price_2 = "/html/body/div[1]/div[3]/main/section/div/div[4]/div[2]/div[1]/div[2]/div/div[2]/meta"

        driver.get(url)
        time.sleep(12)  # Adjust as necessary based on your connection and the site's response

        price_elements = driver.find_elements(By.XPATH, xpath_price)
        price_elements_2 = driver.find_elements(By.XPATH, xpath_price_2)

        if not price_elements:
            if not price_elements_2:
                return np.nan
            else:
                return price_elements_2[0].get_attribute("content")
        else:
            return price_elements[0].text

    except Exception as e:
        # Log the error if needed (print or use logging)
        print(f"Error retrieving price from {url}: {e}")
        return np.nan

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.machineryhouse.com.au/w194"
    price = get_hares_and_forbes_price(url,driver)
    print(price)
    driver.quit()
