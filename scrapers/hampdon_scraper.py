import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_hampdon_price(url: str) -> str:
    
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.hampdon.com.au/"):
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
    except (httpx.RequestError, httpx.ReadTimeout, Exception):
        return np.nan

    # Parse the response text with Selector
    sel = Selector(response.text)
    
    # Locate the price element using the appropriate CSS selector
    price_element = sel.css("div.productprice.productpricetext[itemprop='price']")
    if not price_element:
        return np.nan

    # First, try to extract the price using the "content" attribute
    content_attr = price_element.attrib.get("content", "")
    if content_attr:
        cleaned_price = content_attr.strip()
        return cleaned_price

    # Fallback: extract the inner text and clean it
    price_text = price_element.css("::text").get()
    if not price_text:
        return np.nan
    cleaned_price = price_text.replace("$", "").replace(",", "").strip()
    
    return cleaned_price

if __name__ == "__main__":
    url = "https://www.hampdon.com.au/unimig-razor-tig-200-ac/dc-water-cooler?srsltid=AfmBOooUly0f8iVOdfNeit9ErrVNrUeWi8OdnXLWZ4ZwcJqbb9mrO40C"
    price = get_hampdon_price(url)
    print("Final extracted price:", price)
