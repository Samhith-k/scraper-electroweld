import json
import math
import httpx
import asyncio

from typing import Dict, List, Literal
from urllib.parse import urlencode
from parsel import Selector

SORTING_MAP = {
    "best_match": 12,
    "ending_soonest": 1,
    "newly_listed": 10,
}

session = httpx.AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
    http2=True,
    follow_redirects=True
)


def parse_search(response: httpx.Response) -> List[Dict]:
    """parse ebay's search page for listing preview details"""
    previews = []
    # each listing has it's own HTML box where all of the data is contained
    sel = Selector(response.text)
    listing_boxes = sel.css(".srp-results li.s-item")
    for box in listing_boxes:
        # quick helpers to extract first element and all elements
        css = lambda css: box.css(css).get("").strip()
        css_all = lambda css: box.css(css).getall()
        previews.append(
            {
                "url": css("a.s-item__link::attr(href)").split("?")[0],
                "title": css(".s-item__title>span::text"),
                "price": css(".s-item__price::text"),
                "shipping": css(".s-item__shipping::text"),
                "list_date": css(".s-item__listingDate span::text"),
                "subtitles": css_all(".s-item__subtitle::text"),
                "condition": css(".s-item__subtitle .SECONDARY_INFO::text"),
                "photo": css(".s-item__image img::attr(src)"),
                "rating": css(".s-item__reviews .clipped::text"),
                "rating_count": css(".s-item__reviews-count span::text"),
            }
        )
    return previews


async def scrape_search(
    query,
    max_pages=1,
    category=0,
    items_per_page=240,
    sort: Literal["best_match", "ending_soonest", "newly_listed"] = "newly_listed",
) -> List[Dict]:
    """Scrape Ebay's search results page for product preview data for given"""

    def make_request(page):
        return "https://www.ebay.com.au/sch/i.html?" + urlencode(
            {
                "_nkw": query,
                "_sacat": category,
                "_ipg": items_per_page,
                "_sop": SORTING_MAP[sort],
                "_pgn": page,
            }
        )

    first_page = await session.get(make_request(page=1))
    results = parse_search(first_page)
    if max_pages == 1:
        return results
    # find total amount of results for concurrent pagination
    total_results = first_page.selector.css(".srp-controls__count-heading>span::text").get()
    total_results = int(total_results.replace(",", ""))
    total_pages = math.ceil(total_results / items_per_page)
    if total_pages > max_pages:
        total_pages = max_pages
    other_pages = [session.get(make_request(page=i)) for i in range(2, total_pages + 1)]
    for response in asyncio.as_completed(other_pages):
        response = await response
        try:
            results.extend(parse_search(response))
        except Exception as e:
            print(f"failed to scrape search page {response.url}")
    return results


data = asyncio.run(scrape_search("UNIMIG viper 165"))
print(json.dumps(data[0], indent=2))