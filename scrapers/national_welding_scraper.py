import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_national_welding_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.nationalwelding.com.au/"):
        return np.nan
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            },
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
    except (httpx.RequestError, httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    promo_price_element = sel.css("div.productpromo[itemprop='price']")
    if promo_price_element:
        content_attr = promo_price_element.attrib.get("content", "")
        if content_attr:
            return content_attr.strip()
        promo_price_text = promo_price_element.css("::text").get()
        if promo_price_text:
            return promo_price_text.replace("NOW", "").replace("$", "").replace(",", "").strip()
    price_element = sel.css("div.productprice.productpricetext[itemprop='price']")
    if not price_element:
        return np.nan
    content_attr = price_element.attrib.get("content", "")
    if content_attr:
        return content_attr.strip()
    price_text = price_element.css("::text").get()
    if not price_text:
        return np.nan
    return price_text.replace("$", "").replace(",", "").strip()

if __name__ == "__main__":
    url = "https://www.nationalwelding.com.au/unimig-viper-multi-195-max-welder-u11011?srsltid=AfmBOorwGPQVjdFtBS0Lq0iL7htZ-DDhidL9QyhL-g0rKZeX8E4gN9Vm"
    price = get_national_welding_price(url)
    print("Final extracted price:", price)
