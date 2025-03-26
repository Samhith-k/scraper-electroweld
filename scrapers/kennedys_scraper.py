import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_kennedys_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in the element at the following XPath:
    
    /html/body/main/section[1]/section/div/div[2]/div/div[2]/div/div/div[1]/span[2]
    
    Returns np.nan on any failure.
    """
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.kennedys.com.au/"):
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
    except (httpx.RequestError, httpx.ReadTimeout, Exception) as e:
        print("DEBUG: Exception occurred:", e)
        return np.nan

    # Debug: print response length
    #print("DEBUG: Response length =", len(response.text), "characters")

    # Parse the response text with Selector
    sel = Selector(response.text)
    
    # Extract the price text using the provided XPath
    price_text = sel.xpath("/html/body/main/section[1]/section/div/div[2]/div/div[2]/div/div/div[1]/span[2]/text()").get(default="").strip()
    #print("DEBUG: Extracted raw price text:", price_text)
    
    # Optionally remove a leading currency symbol (if desired)
    if price_text.startswith("$"):
        price_text = price_text[1:].strip()

    return price_text.replace("AUD","")

if __name__ == "__main__":
    url = "https://www.kennedys.com.au/products/unimig-razor-cut-45-gen-2"
    price = get_kennedys_price(url)
    print(price)
