import httpx
from parsel import Selector
import pandas as pd
import numpy as np


def get_bilba_website_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://bilba.com.au/products"):
        return np.nan
    with httpx.Client(
        headers={
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    ) as client:
        response = client.get(url)
    sel = Selector(response.text)
    price = sel.css("span.price-item.price-item-regular::text").get(default="").strip()
    return price[1:] if price.startswith("$") else price

# Example usage:
if __name__ == "__main__":
    url = "https://bilba.com.au/products/unimig-razor-multi-175-welder?srsltid=AfmBOoqrcyItnYkdHvmmHMrp6Z7N-pFgOuiv_wJhyPmV19CKmUt5LIBi"
    price = get_bilba_website_price(url)
    print( price)
