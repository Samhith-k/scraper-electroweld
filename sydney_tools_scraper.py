from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_sydney_tools_price(url: str, timeout: int = 20) -> str:
    """
    Uses Selenium with headless Chrome to load the Sydney Tools product page,
    waits for the <div class="price"> element to appear, and collects all text
    from the <span> elements inside that div. Returns the combined text.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)

        try:
            # Wait until the <div class="price"> is present in the DOM
            price_div = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.price"))
            )
            # Gather all <span> elements inside the price div
            span_elements = price_div.find_elements(By.CSS_SELECTOR, "span")
            
            # Combine the text from all spans into a single string
            price_text = " ".join(span.text.strip() for span in span_elements if span.text.strip())
            return price_text

        except TimeoutException:
            print(f"Timeout: No <div class='price'> found within {timeout} seconds.")
            # For debugging: print the page source to see what actually loaded
            print(driver.page_source)
            return ""
    finally:
        driver.quit()

if __name__ == "__main__":
    url = (
        "https://sydneytools.com.au/product/"
        "unimig-u11008k-240v-razor-3in1-multi-220-mitigstick-welder"
    )
    price = get_sydney_tools_price(url)
    print("Price found:", price)
