import csv
import json
import sys
import os
import time
import random
import httpx
from parsel import Selector

def get_client():
    # Create an HTTPX client with HTTP/2 enabled and browser-like headers.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    client = httpx.Client(
        headers=headers,
        http2=True,
        follow_redirects=True
    )
    return client

def parse_product(response: httpx.Response) -> dict:
    """
    Parse eBay's product page to extract key fields.
    Expected fields:
      - url (canonical URL)
      - id (extracted from the URL)
      - price_original
      - name
      - seller_name
      - photos (list of image URLs)
      - features (a dictionary of item specifics)
    """
    sel = Selector(response.text)
    css_join = lambda css: "".join(sel.css(css).getall()).strip()
    css = lambda css: sel.css(css).get("").strip()
    
    item = {}
    # Canonical URL and extract ID from it.
    item["url"] = css('link[rel="canonical"]::attr(href)')
    if item["url"]:
        try:
            item["id"] = item["url"].split("/itm/")[1].split("?")[0]
        except IndexError:
            item["id"] = ""
    else:
        item["id"] = ""
    
    # Price original from the primary price span.
    item["price_original"] = css(".x-price-primary > span::text")
    # Name: join all text from the h1 span.
    item["name"] = css_join("h1 span::text")
    # Seller name.
    item["seller_name"] = sel.xpath("//div[contains(@class,'info__about-seller')]/a/span/text()").get() or ""
    # Photos from both carousel selectors.
    photos = sel.css('.ux-image-filmstrip-carousel-item.image img::attr("src")').getall()
    photos.extend(sel.css('.ux-image-carousel-item.image img::attr("src")').getall())
    item["photos"] = photos

    # Extract item specifics (features) from common containers.
    features = {}
    container = (sel.css("div.ux-layout-section--features") or 
                 sel.css("div.itemAttr") or 
                 sel.css("section.itemAttr") or 
                 sel.css("div#viTabs_0_is"))
    if container:
        for feature in container.css("dl.ux-labels-values"):
            label = "".join(feature.css(".ux-labels-values__labels-content > div > span::text").getall()).strip(":\n ")
            value = "".join(feature.css(".ux-labels-values__values-content > div > span *::text").getall()).strip(":\n ")
            if label:
                features[label] = value
    item["features"] = features

    return item

def main(input_csv, output_csv):
    # Open the input CSV and read rows.
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        print("Input CSV is empty.")
        return

    header = rows[0]
    try:
        link_index = header.index("electroweld--link")
    except ValueError:
        print("Column 'electroweld--link' not found in header.")
        return
    try:
        product_index = header.index("product")
    except ValueError:
        print("Column 'product' not found in header.")
        product_index = None

    # Count total valid eBay links.
    total_valid = sum(
        1 for row in rows[1:] if len(row) > link_index and row[link_index].strip().startswith("http")
    )
    processed = 0
    timeout_count = 0
    failure_count = 0

    client = get_client()

    # Prepare output CSV.
    with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        # Output columns as requested.
        writer.writerow([
            "url",
            "id",
            "price_original",
            "name",
            "seller_name",
            "photos",
            "Item Type",
            "Custom Bundle",
            "Brand",
            "Bundle Description",
            "Model"
        ])

        for row in rows[1:]:
            if len(row) <= link_index:
                continue
            url = row[link_index].strip()
            if not url or not url.startswith("http"):
                continue

            # Use the CSV "product" field to determine local custom bundle flag.
            product_val = row[product_index].strip() if product_index is not None and len(row) > product_index else ""
            local_custom_bundle = "Yes" if "bundle" in product_val.lower() else "No"

            try:
                response = client.get(url, timeout=30)
                response.raise_for_status()
                product_data = parse_product(response)
            except httpx.ReadTimeout:
                print(f"Timeout fetching {url}")
                timeout_count += 1
                product_data = {}
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                failure_count += 1
                product_data = {}

            # Map scraped features to desired fields.
            features = product_data.get("features", {})
            out_item_type = features.get("Item Type", "")
            # Use the listing's "Custom Bundle" if present; otherwise fallback to our CSV logic.
            out_custom_bundle = features.get("Custom Bundle", local_custom_bundle)
            out_brand = features.get("Brand", "")
            out_bundle_desc = features.get("Bundle Description", "No")
            out_model = features.get("MPN", "")

            writer.writerow([
                product_data.get("url", url),
                product_data.get("id", ""),
                product_data.get("price_original", ""),
                product_data.get("name", ""),
                product_data.get("seller_name", ""),
                json.dumps(product_data.get("photos", [])),  # store photos as a JSON array
                out_item_type,
                out_custom_bundle,
                out_brand,
                out_bundle_desc,
                out_model
            ])

            processed += 1
            print(f"Processed {processed} of {total_valid}. Timeouts: {timeout_count}. Failures: {failure_count}")
            # Throttle requests slightly.
            time.sleep(2 + random.random())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scrape_ebay_filtered.py input_csv output_csv")
        sys.exit(1)
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    if not os.path.exists(input_csv):
        print(f"Input file {input_csv} does not exist.")
        sys.exit(1)
    main(input_csv, output_csv)
