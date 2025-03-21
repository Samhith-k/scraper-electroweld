import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_alphaweld_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in the element at the following XPath:
    
    /html/body/div[2]/div[5]/div/div/div[2]/div/div[2]/div[3]/div[2]/div[2]
    
    Returns np.nan on any failure.
    Company: Alphaweld
    """
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        #print("DEBUG: URL is invalid or empty.")
        return np.nan
    if not url.startswith("https://www.alphaweld.com.au/"):
        #print("DEBUG: URL does not start with https://www.alphaweld.com.au/")
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
            #print("DEBUG: Response status code:", response.status_code)
            #print("DEBUG: Response length:", len(response.text))
    except (httpx.RequestError, httpx.ReadTimeout, Exception) as e:
        #print("DEBUG: Exception occurred while making the request:", e)
        return np.nan

    # Parse the response text with Selector
    sel = Selector(response.text)
    special_price_text = sel.css("div.price.special div.value::text").get()
    if not price_text:
        price_text = sel.css("div.price div.value::text").get()
    if not price_text:
        return np.nan
    clean_price = price_text.replace("$", "").replace("excl GST", "").strip()
    return clean_price

if __name__ == "__main__":
    url = "https://www.alphaweld.com.au/product/19427-unimig-viper-185-mig-tig-stick-welder"
    price = get_alphaweld_price(url)
    print("Final extracted price:", price)
