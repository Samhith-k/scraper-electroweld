import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_total_tools_price(url: str) -> str:
    """
    Fetch the product page from the Total Tools website and return the product price as a string.
    The price is expected to be in the HTML structure:
    
    <span id="product-price-107683" data-price-amount="399" data-price-type="finalPrice" content="" class="price-wrapper" itemprop="price">
      <span class="price">
        <span class="currency-symbol">$</span>399
      </span>
    </span>
    
    The CSS selector used is:
      span.price-wrapper span.price::text
      
    which collects the texts "$" and "399". They are then concatenated and cleaned.
    
    Returns np.nan on any failure.
    """
    # Validate the URL
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.totaltools.com.au/"):
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
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                ),
            },
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
    except (httpx.RequestError, httpx.ReadTimeout, Exception) as e:
        print("DEBUG: Exception occurred while fetching URL:", e)
        return np.nan

    # Parse the response text with parsel's Selector
    sel = Selector(response.text)
    
    # Use CSS selector to extract all text nodes inside the <span class="price"> element.
    price_text_list = sel.css("span.price-wrapper span.price::text").getall()
    
    if not price_text_list:
        print("DEBUG: No price text found with CSS selector.")
        return np.nan

    # Debug: Print the list of texts extracted
    #print("DEBUG: Price text list extracted:", price_text_list)
    
    # Combine the text nodes and remove extra whitespace.
    price_text = price_text_list[0].strip()
    
    # Remove the leading currency symbol if present.
    if price_text.startswith("$"):
        price_text = price_text[1:].strip()
    
    return price_text

# Example usage:
if __name__ == "__main__":
    # Replace this URL with a valid Total Tools product URL.
    url = "https://www.totaltools.com.au/195698-unimig-viper-multi-135-mig-tig-stick-welder-u11005k?srsltid=AfmBOoqAlA609D3AedJJKpGhzpFrYHz27IsLASUdzGTEuTnhSe4m-gfq"
    price = get_total_tools_price(url)
    print("Product Price:", price)
