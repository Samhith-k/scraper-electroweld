import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_gasweld_price(url: str) -> str:
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if len(url) == 0:
        return np.nan
    if not url.startswith("https://www.gasweld.com.au/"):
        return np.nan

    try:
        with httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True
        ) as session:
            # Set an explicit timeout (in seconds) for the request.
            response = session.get(url, timeout=10.0)
    except httpx.ReadTimeout:
        # Return np.nan if a timeout occurs.
        return np.nan

    sel = Selector(response.text)
    # Extract the price from the targeted element.
    # The price is inside a <span> with class "price".
    price_text = sel.css("span.price::text").get(default="").strip()
    # Remove the '$' sign
    price_text = price_text.replace("$", "").strip()
    
    return price_text

# Example usage with df.apply:
if __name__ == "__main__":
    # Test URL provided for Gasweld
    link="https://www.gasweld.com.au/unimig-u11005k-viper-multi-135-mig-tig-stick-electric-welder"
    print(get_gasweld_price(link))
 
