import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def get_trade_tools_price(url: str, driver) -> str:
    # Validate the URL
    if not isinstance(url, str) or pd.isna(url) or url.strip() == "" or not url.startswith("https://www.tradetools.com/"):
        return np.nan
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        price_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.price-2To")))
        price_element = price_container.find_element(By.CSS_SELECTOR, "div > span:nth-child(2)")
        price_text = price_element.text.strip()
        return price_text
    except Exception:
        return np.nan

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options)
    url = "https://www.tradetools.com/unimig-viper-multi-135-mig-tig-stick-welder-u11005k?srsltid=AfmBOopNWJ0MPokIFsR1Q2X08Em8GKPVhYO6sHi-V4q428QXhMSMrwZa"
    price = get_trade_tools_price(url, driver)
    print("Extracted Price:", price)
    driver.quit()
