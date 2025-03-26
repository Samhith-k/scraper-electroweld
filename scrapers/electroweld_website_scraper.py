import httpx
from parsel import Selector
import pandas as pd
import numpy as np

def get_electroweld_website_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.electroweld.com.au/product/"):
        return np.nan
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    try:
        response = session.get(url)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    price = sel.css("p.w-post-elm.product_field.price span.woocommerce-Price-amount.amount bdi::text").get(default="").strip()
    return price[1:] if price.startswith("$") else price

url = "https://www.electroweld.com.au/product/unimig-viper-135-multi-3-in-1-mig-tig-stick-welder-welding-torch-mma-u11005k/"
price = get_electroweld_website_price(url)
print("Product Price:", price)
