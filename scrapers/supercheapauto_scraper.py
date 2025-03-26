import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_supercheapauto_price(url: str) -> str:
    """
    Fetch the product page from the given Supercheapauto URL and return the product price as a string.
    The price can be found in the HTML via XPath such as:
      Full absolute path: /html/body/div[1]/div[14]/div[3]/div/div[2]/div/div[3]/span/span/text()
      Or via classes: //span[contains(@class, 'price-sales')]//span[contains(@class, 'promo-price')]/text()
    Returns np.nan for any failure.
    """
    # URL validations
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.supercheapauto.com.au/"):
        return np.nan

    # Create an HTTP client with browser-like headers
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as session:
            response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception) as e:
        # Could also log the exception e if desired
        return np.nan

    # Parse the HTML using Selector
    sel = Selector(response.text)

    # First try to extract using class-based XPath
    price_class_nodes = sel.xpath("//span[contains(@class, 'price-sales')]//span[contains(@class, 'promo-price')]/text()").getall()
    price_class = "".join(price_class_nodes).strip()

    # Then try using the full absolute XPath (if class-based extraction is empty)
    price_full = sel.xpath("/html/body/div[1]/div[14]/div[3]/div/div[2]/div/div[3]/span/span/text()").get(default="").strip()

    # Choose the first non-empty result
    price_text = price_class if price_class else price_full

    # If the price text starts with a currency symbol, remove it
    if price_text.startswith("$"):
        price_text = price_text[1:].strip()

    # Return np.nan if no price was found
    if not price_text:
        return np.nan

    return price_text

# Example usage:
if __name__ == "__main__":
    url = "https://www.supercheapauto.com.au/p/unimig-unimig-viper-185-multiprocess-welder/678408.html"
    price = get_supercheapauto_price(url)
    print("Product Price:", price)
