import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

def print_machineryhouse_spans_undetected(url: str) -> None:
    """
    Uses undetected-chromedriver to bypass bot detection and fetch the Machinery House page.
    Prints debug information and then all text from <span> elements.
    """
    # Set up Chrome options.
    options = uc.ChromeOptions()
    options.headless = True  # Use headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Specify version_main to match your installed Chrome version (133 in your case)
    driver = uc.Chrome(version_main=133, options=options)
    
    try:
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait until the page title no longer contains "Just a moment".
        WebDriverWait(driver, 30).until(lambda d: "Just a moment" not in d.title)
        time.sleep(5)  # Additional wait to ensure content is loaded
        
        print("Page title:", driver.title)
        page_source = driver.page_source
        print("Length of page source:", len(page_source))
        
        spans = driver.find_elements(By.TAG_NAME, "span")
        print("Total number of <span> elements found:", len(spans))
        
        for idx, span in enumerate(spans, start=1):
            text = span.text.strip()
            if text:
                print(f"Span {idx}: {text}")
    except Exception as e:
        print("Error occurred:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.machineryhouse.com.au/w243"
    print_machineryhouse_spans_undetected(url)
