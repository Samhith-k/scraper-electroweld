import httpx
from parsel import Selector

def get_electroweld_website_price(url: str) -> str:
    """
    Fetch the product page from the given URL and return the product price as a string.
    """
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    response = session.get(url)
    sel = Selector(response.text)
    css = lambda query: sel.css(query).get(default="").strip()

    # Extract the price text from the page.
    price_text = css("p.w-post-elm.product_field.price span.woocommerce-Price-amount.amount bdi::text")
    # Remove a leading currency symbol if present.
    if price_text.startswith("$"):
        price_text = price_text[1:]
    return price_text

url = "https://www.electroweld.com.au/product/unimig-viper-135-multi-3-in-1-mig-tig-stick-welder-welding-torch-mma-u11005k/"
price = get_electroweld_website_price(url)
print("Product Price:", price)
