import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_waindustrialsupplies_price(driver, url: str) -> str:
    # Validate URL
    if not url or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.waindustrialsupplies.net/"):
        return np.nan

    try:
        driver.set_page_load_timeout(15)
        #print("DEBUG: Fetching URL:", url)
        driver.get(url)
        # Wait for JavaScript to load the dynamic content.
        time.sleep(2)  # Adjust as necessary for the content to load

        # Extract the price using the full XPath.
        xpath_price = "/html/body/div[1]/div/div[1]/div[1]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div[2]/form/section[1]/div[1]/div/h3/span"
        price_element = driver.find_element(By.XPATH, xpath_price)
        price_text = price_element.text.strip()
        return price_text
    except Exception as e:
        #print("Exception occurred while fetching price:", e)
        return np.nan

if __name__ == "__main__":
    # Configure Selenium for headless browsing.
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Initialize the WebDriver outside the function.
    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = "https://www.waindustrialsupplies.net/product/razor-350-swf-mig-tig-stick-welder/291"
        price = get_waindustrialsupplies_price(driver, url)
        print("Product Price:", price)
    finally:
        driver.quit()