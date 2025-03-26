import httpx
from parsel import Selector
import numpy as np
import pandas as pd

def get_toolswarehouse_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in an element like:
    <div class="price__current" data-price-container="">
      <span class="visually-hidden">Current price</span>
      <span class="money" data-price="">$899.00</span>
    </div>
    
    Returns np.nan if any error occurs or the price is not found.
    """
    # Validate URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan

    # Optional: check if the URL starts with the expected domain
    if not url.startswith("https://toolswarehouse.com.au/"):
        return np.nan

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
            response = client.get(url)
    except (httpx.ReadTimeout, Exception) as e:
        print("Error fetching URL:", e)
        return np.nan

    # Debug: print response length
    
    # Parse the HTML using parsel's Selector
    sel = Selector(response.text)

    # Use CSS selector to extract the text inside the <span class="money" data-price="">
    price_text = sel.css("div.price__current span.money::text").get(default="").strip()

    # Debug: Print the extracted raw price text

    # Remove a leading currency symbol if needed (e.g., '$')
    if price_text.startswith("$"):
        price_text = price_text[1:]

    if price_text == "":
        return np.nan

    return price_text

# Example usage:
if __name__ == "__main__":
    url = "https://toolswarehouse.com.au/products/unimig-kumjrvm185-viper-185-mig-tig-stick-inverter-welder?srsltid=AfmBOopS-8q_TA5xhCjQbaPTbBXndGSCjjb1QXbwoaUeaxJDfpfXowdj"
    price = get_toolswarehouse_price(url)
    print("Product Price:", price)
