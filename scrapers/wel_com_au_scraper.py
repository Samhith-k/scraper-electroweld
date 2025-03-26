import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_weld_com_au_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in:
    <p class="price">
        <span class="woocommerce-Price-amount amount">
            <bdi>
                <span class="woocommerce-Price-currencySymbol">$</span>1,669.00
            </bdi>
        </span>
    </p>
    """
    # Basic checks for URL validity
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if len(url) == 0:
        return -1
    # Ensure the URL starts with the Weld product URL base.
    if not url.startswith("https://www.weld.com.au/product/"):
        return -1
    
    # Create an HTTP client with appropriate headers.
    session = httpx.Client(
        headers={
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    
    # Fetch the page
    response = session.get(url)
    sel = Selector(response.text)
    css = lambda query: sel.css(query).get(default="").strip()
    
    # Extract the price text using the appropriate CSS selector.
    price_text = css("p.price span.woocommerce-Price-amount.amount bdi::text")
    
    # Remove a leading currency symbol if present.
    if price_text.startswith("$"):
        price_text = price_text[1:]
    
    return price_text

# Example usage:
if __name__ == "__main__":
    url = "https://www.weld.com.au/product/unimig-razor-multi-175-bundle-pk11091/?v=6502139931c4"
    price = get_weld_com_au_price(url)
    print( price)
