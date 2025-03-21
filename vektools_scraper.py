import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_vektools_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in the element at the following XPath:
    
    /html/body/div[2]/main/div[2]/div/div[1]/div[2]/div[3]/div/span[1]/span/span[2]/span
    
    Returns np.nan on any failure.
    """
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.vektools.com.au/"):
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

    # Uncomment the next line if you want to check the response length for debugging
    # print("DEBUG: Response length =", len(response.text), "characters")
    
    # Parse the response text with Selector
    sel = Selector(response.text)
    
    # Extract the price text using the provided full XPath
    price_text2=sel.xpath("/html/body/div[2]/main/div[2]/div/div[1]/div[2]/div[3]/div/span/span/span").get(default="").strip()
    price_text = sel.xpath("/html/body/div[2]/main/div[2]/div/div[1]/div[2]/div[3]/div/span[1]/span/span[2]/span/text()").get(default="").strip()
    if price_text == "":
        price_text = price_text2
    # Uncomment the next line to see the raw extracted price text for debugging
    # print("DEBUG: Extracted raw price text:", price_text)
    
    # Optionally remove a leading currency symbol if present
    if price_text.startswith("$"):
        price_text = price_text[1:].strip()

    return price_text

if __name__ == "__main__":
    url = "https://www.vektools.com.au/unimig-kumjrr180ca-180-amp-inverter-arc-stick-welder.html"
    price = get_vektools_price(url)
    print("Product Price:", price)
