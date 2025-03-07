import httpx
from parsel import Selector

def get_price_original(url: str) -> str:
    """
    Given an eBay product URL, fetches the page and returns the original price.
    """
    # establish our HTTP2 client with browser-like headers
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        http2=True,
        follow_redirects=True
    )
    
    # fetch the webpage
    response = session.get(url)
    sel = Selector(response.text)
    
    # helper function to extract and strip text via CSS selectors
    css = lambda query: sel.css(query).get(default="").strip()
    
    # extract the original price
    price_original = css(".x-price-primary>span::text")
    
    return price_original

# Example usage:
url = "https://www.ebay.com.au/itm/275880137475?itmmeta=01J3RRGZ6RGRZ1PA0NB89D3ANK&hash=item403bbcd303:g:FG4AAOSwW1lmc0i2:sc:AU_RegularParcelWithTrackingAndSignature!2190!AU!-1&itmprp=enc%3AAQAJAAAA0Jo7zG6ZrYn%2F5GTELNdvHESu%2F8%2BPfiWY9kU--0LUo18ZDC%2BkIaIZvbRp1qI9So5TpISckKJtf4oGgV7V5XLYXMhG%2FLVX497kkF4F%2BcZyu0ELdaH4TYhi3PZ%2B%2BG7xxw75rLO07cwbga6GANQK6eH5xnlQBFG02TBJBi4CCfYH8LVydeSYVPiJ8rWQKbaKABcsxdxl%2B4uJjP6Ops8YFB%2BzE7T3l62OMSCzA63O1oEmgLiiOQySiIwlAiRx%2Fu3oj4L0GrlW2ZSPf1mHsjewL9BaDsQ%3D%7Ctkp%3ABk9SR7zzw5ieZA"
print(get_price_original(url))
