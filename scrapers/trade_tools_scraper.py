import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_trade_tools_price(url: str, driver) -> str:
    # Validate the URL: ensure it's a non-empty string starting with the expected domain.
    if not isinstance(url, str) or pd.isna(url) or url.strip() == "" or not url.startswith("https://www.tradetools.com/"):
        return np.nan
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        price_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.price-2To")))
        # Locate the inner <div> that contains the price spans.
        inner_div = price_container.find_element(By.CSS_SELECTOR, "div")
        spans = inner_div.find_elements(By.TAG_NAME, "span")
        # Append all text from the spans.
        combined_text = "".join([span.text for span in spans]).strip()
        # Remove the '$' sign.
        numeric_text = combined_text.replace("$", "").strip()
        # Split on the dot to get just the integer portion.
        final_price = numeric_text
        return final_price
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
