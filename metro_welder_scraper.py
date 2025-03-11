import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_metweld_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in an element like:
    
    <span data-product-price-with-tax="" class="price price--withTax">$979.00</span>
    
    Returns np.nan for any failure.
    """
    # Validate URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if len(url) == 0:
        return np.nan
    if not url.startswith("https://metweld.com.au/"):
        return np.nan

    try:
        # Create an HTTP client with browser-like headers
        with httpx.Client(
            headers={
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/113.0.0.0 Safari/537.36"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True
        ) as session:
            # Fetch the page with a 15-second timeout
            response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception):
        return np.nan

    sel = Selector(response.text)
    # Helper function for CSS selection
    css = lambda query: sel.css(query).get(default="").strip()
    
    # Extract the price text from the <span> element
    price_text = css("span.price.price--withTax::text")
    
    # Remove a leading currency symbol if present
    if price_text.startswith("$"):
        price_text = price_text[1:]
    
    return price_text

# Example usage:
if __name__ == "__main__":
    url = "https://metweld.com.au/viper-185-mig-tig-stick-welder/"
    price = get_metweld_price(url)
    print("Product Price:", price)
