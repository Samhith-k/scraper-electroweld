import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_weldconnect_price(url: str) -> str:

    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if len(url) == 0:
        return np.nan
    if not url.startswith("https://www.weldconnect.com.au/"):
        return np.nan

    try:
        with httpx.Client(
            headers={
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True
        ) as session:
            # Set an explicit timeout (in seconds) for the request.
            response = session.get(url, timeout=10.0)
    except httpx.ReadTimeout:
        # If a timeout occurs, return np.nan (or any other appropriate fallback)
        return np.nan

    sel = Selector(response.text)
    # Extract the price using the "content" attribute from the <div> element.
    price_text = sel.css("div.h1[itemprop='price']::attr(content)").get(default="").strip()
    
    return price_text

# Example usage with df.apply:
if __name__ == "__main__":
    # Sample dataframe for demonstration
    data = {
        'PRODUCT LINK': ["https://www.weldconnect.com.au/razor-compact-250-welder"]
    }
    df = pd.DataFrame(data)
    df['Price'] = df['PRODUCT LINK'].apply(get_weldconnect_price)
    print(df)
