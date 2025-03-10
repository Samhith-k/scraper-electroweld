import json
import httpx
from parsel import Selector

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

def parse_product(response: httpx.Response) -> dict:
    """Parse Ebay's product listing page for core product data"""
    sel = Selector(response.text)
    # define helper functions that chain the extraction process
    css_join = lambda css: "".join(sel.css(css).getall()).strip()  # join all selected elements
    css = lambda css: sel.css(css).get("").strip()  # take first selected element and strip of leading/trailing spaces

    item = {}
    item["url"] = css('link[rel="canonical"]::attr(href)')
    item["id"] = item["url"].split("/itm/")[1].split("?")[0]  # we can take ID from the URL
    item["price_original"] = css(".x-price-primary>span::text")
    item["price_converted"] = css(".x-price-approx__price ::text")  # ebay automatically converts price for some regions
    item["name"] = css_join("h1 span::text")
    item["seller_name"] = sel.xpath("//div[contains(@class,'info__about-seller')]/a/span/text()").get()
    item["seller_url"] = sel.xpath("//div[contains(@class,'info__about-seller')]/a/@href").get().split("?")[0]
    item["photos"] = sel.css('.ux-image-filmstrip-carousel-item.image img::attr("src")').getall()  # carousel images
    item["photos"].extend(sel.css('.ux-image-carousel-item.image img::attr("src")').getall())  # main image
    # description is an iframe (independant page). We can keep it as an URL or scrape it later.
    item["description_url"] = css("iframe#desc_ifr::attr(src)")
    
    # feature details from the description table:
    features = {}
    feature_table = sel.css("div.ux-layout-section--features")
    for feature in feature_table.css("dl.ux-labels-values"):
        # iterate through each label of the table and select first sibling for value:
        label = "".join(feature.css(".ux-labels-values__labels-content > div > span::text").getall()).strip(":\n ")
        value = "".join(feature.css(".ux-labels-values__values-content > div > span *::text").getall()).strip(":\n ")
        features[label] = value
    item["features"] = features

    return item


response = session.get("https://www.ebay.com.au/itm/275880137475?itmmeta=01J3RRGZ6RGRZ1PA0NB89D3ANK&hash=item403bbcd303:g:FG4AAOSwW1lmc0i2:sc:AU_RegularParcelWithTrackingAndSignature!2190!AU!-1&itmprp=enc%3AAQAJAAAA0Jo7zG6ZrYn%2F5GTELNdvHESu%2F8%2BPfiWY9kU--0LUo18ZDC%2BkIaIZvbRp1qI9So5TpISckKJtf4oGgV7V5XLYXMhG%2FLVX497kkF4F%2BcZyu0ELdaH4TYhi3PZ%2B%2BG7xxw75rLO07cwbga6GANQK6eH5xnlQBFG02TBJBi4CCfYH8LVydeSYVPiJ8rWQKbaKABcsxdxl%2B4uJjP6Ops8YFB%2BzE7T3l62OMSCzA63O1oEmgLiiOQySiIwlAiRx%2Fu3oj4L0GrlW2ZSPf1mHsjewL9BaDsQ%3D%7Ctkp%3ABk9SR7zzw5ieZA")
product_data = parse_product(response)

# print the results in JSON format
print(json.dumps(product_data, indent=2))