import httpx
import numpy as np
import pandas as pd
from parsel import Selector
import logging

# Uncomment the following line to disable logging output later if desired:
# logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.DEBUG)

def get_trade_tools_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    
    The function targets the price contained in a div with class "price-2To". It looks for
    the inner <div> that holds all the <span> elements for the price. For example, given the HTML:
    
        <div class="price-2To">
            <div class="">
                <span class="">$</span>
                <span class="">399</span>
                <span class="cents-1T3">.</span>
                <span class="cents-1T3">00</span>
            </div>
            <span class="includesGst-1Q_">Inc GST</span>
        </div>
    
    The function joins the text from the spans inside the inner <div> (yielding "$399.00"),
    then removes the "$" to return a cleaned price string like "399.00".
    
    Returns:
        A string containing the cleaned price (e.g., "399.00"), or np.nan on any failure.
    
    Company: Trade Tools
    """
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        logging.debug("Invalid or empty URL provided.")
        return np.nan
    if not url.startswith("https://www.tradetools.com/"):
        logging.debug("URL does not start with https://www.tradetools.com/")
        return np.nan

    try:
        with httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/113.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                    "image/webp,*/*;q=0.8"
                ),
            },
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            logging.debug("Response status code: %s", response.status_code)
            logging.debug("Response length: %d", len(response.text))
    except (httpx.RequestError, httpx.ReadTimeout, Exception) as e:
        logging.debug("Exception occurred while making the request: %s", e)
        return np.nan

    # Parse the response text with Selector
    sel = Selector(response.text)
    
    # Look for the inner div inside the main price container "price-2To"
    price_container = sel.css("div.price-2To > div")
    if not price_container:
        logging.debug("No price container found using selector 'div.price-2To > div'.")
        return np.nan

    # Get all the <span> text inside the inner div and join them
    spans = price_container.css("span::text").getall()
    if not spans:
        logging.debug("No span elements found inside the price container.")
        return np.nan

    joined_price = "".join(span.strip() for span in spans if span.strip())
    logging.debug("Joined price text (raw): %r", joined_price)
    
    # Remove the "$" symbol from the joined string
    clean_price = joined_price.replace("$", "").strip()
    logging.debug("Cleaned price text: %r", clean_price)
    
    return clean_price

if __name__ == "__main__":
    url = "https://www.tradetools.com/unimig-viper-multi-135-mig-tig-stick-welder-u11005k?srsltid=AfmBOopNWJ0MPokIFsR1Q2X08Em8GKPVhYO6sHi-V4q428QXhMSMrwZa"
    price = get_trade_tools_price(url)
    print("Final extracted price:", price)
