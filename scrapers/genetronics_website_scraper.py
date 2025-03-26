import httpx
import numpy as np
import pandas as pd
from parsel import Selector

def get_gentronics_website_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    The price is stored in a <p> element with class="gentronics-price price".
    """
    # Basic checks for URL validity
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if len(url) == 0:
        return np.nan
    
    # Check that the URL starts with the desired domain
    if not url.startswith("https://www.googleadservices.com/pagead/aclk") and not url.startswith("https://www.gentronics.com.au/"):
        return np.nan
    
    # Create an HTTP client with appropriate headers
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    
    # Fetch the page
    response = session.get(url)
    sel = Selector(response.text)
    
    # Helper function for CSS selection
    css = lambda query: sel.css(query).get(default="").strip()
    
    # Extract the price text from <p class="gentronics-price price">
    price_text = css("p.gentronics-price.price::text")
    
    # Remove a leading currency symbol if present
    if price_text.startswith("$"):
        price_text = price_text[1:]
    price_text = price_text.replace("per item", "").strip()
    
    return price_text

# Example usage
if __name__ == "__main__":
    test_url = (
        "https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwjZ9uvXloaLAxU2qGYCHVOQD4oYABAEGgJzbQ&ae=2&aspm=1&co=1&ase=5&gclid=Cj0KCQiAhbi8BhDIARIsAJLOlufVl2KRd0vNv4v9hFa9sC_238MQii4XHsBkOTRn3QUpKMJwPGiQne4aAoLtEALw_wcB&ohost=www.google.com&cid=CAESVeD2k-VpUGbx3aGmilsMu45ZMV1Bprr20N9Gm98bkCSwJQ8jp06PNpCmx-boJX920KleNkC6xKJ8zDKPZs-bKKEYQsYqhnX8VLcD2NqlOMrbMcc2p-A&sig=AOD64_03qiZGD-PJa-lfD8uzdS3I3IM9kQ&ctype=5&q=&ved=2ahUKEwjTsubXloaLAxXByTgGHQiRMmYQww8oAnoECAgQCg&adurl="
        # your full URL here
    )
    price = get_gentronics_website_price(test_url)
    print(price)
