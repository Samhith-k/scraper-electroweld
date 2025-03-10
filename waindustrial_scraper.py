import httpx

# Create a session with browser-like headers.
session = httpx.Client(
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
    http2=True,
    follow_redirects=True
)

# Specify the URL to scrape.
url = "https://www.waindustrialsupplies.net/product/razor-multi-175-mig-tig-stick-welder/296"

# Get the response.
response = session.get(url)
print("DEBUG: Response length =", len(response.text), "characters")

# Write the received HTML into a file called x.html.
with open("x.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("DEBUG: HTML saved to x.html")
