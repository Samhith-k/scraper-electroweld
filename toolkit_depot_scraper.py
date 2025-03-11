import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_toolkitdepot_price(url: str) -> str:
    """
    Fetch the Toolkit Depot product page from the given URL and return the product price as a string.
    The price is stored in an element like:
    
      <span data-product-price-with-tax="" class="price price--withTax">
         <sup>$</sup>
         <span>399</span>
      </span>
    
    Returns np.nan if any error occurs.
    """
    # Validate URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://toolkitdepot.com.au/"):
        return np.nan

    try:
        # Create an HTTP client with browser-like headers.
        with httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/113.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True
        ) as session:
            # Fetch the page (timeout=15 seconds)
            response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception) as e:
        print("Error fetching the page:", e)
        return np.nan

    # Print debug info about response length (optional)
    #print("DEBUG: Response length =", len(response.text), "characters")

    # Parse the HTML response using Parsel
    sel = Selector(response.text)

    # Try to extract the price by selecting the nested <span> inside the price container.
    price_text = sel.css("span.price.price--withTax span::text").get(default="").strip()
    
    # Fallback: if the above selector returns empty, concatenate all text nodes within the element.
    if not price_text:
        price_text = "".join(sel.css("span.price.price--withTax ::text").getall()).strip()

    # Remove a leading currency symbol if present
    if price_text.startswith("$"):
        price_text = price_text[1:]
    
    return price_text

if __name__ == "__main__":
    url = "https://toolkitdepot.com.au/unimig-viper-multi-135-mig-tig-stick-welder-u11005k/"
    price = get_toolkitdepot_price(url)
    print(price)
