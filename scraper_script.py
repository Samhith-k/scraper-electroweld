import pandas as pd
import numpy as np
import os
import datetime
import re
import time
import httpx
import logging
from parsel import Selector
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures

from scrapers.hare_and_forbes_scraper import get_hares_and_forbes_price
from scrapers.tools_warehouse_scraper import get_toolswarehouse_price
from scrapers.kennedys_scraper import get_kennedys_price
from scrapers.vektools_scraper import get_vektools_price
from scrapers.sydney_tools_scraper import get_sydney_tools_price
from scrapers.total_tools_scraper import get_total_tools_price
from scrapers.alphaweld_scraper import get_alphaweld_price
from scrapers.waindustrial_scraper import get_waindustrialsupplies_price
from scrapers.gasrep_scraper import get_gasrep_price
from scrapers.electroweld_website_scraper import get_electroweld_website_price
from scrapers.bilba_website_scraper import get_bilba_website_price
from scrapers.stafford_welding_scraper import get_stafford_welding_price
from scrapers.gasweld_scraper import get_gasweld_price
from scrapers.weldquip_scraper import get_weldquip_price

# Configure logging: the log file will be named with the current timestamp.
log_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.log")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def init_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(15)
    return driver

def close_driver(driver: webdriver.Chrome):
    driver.quit()

def fetch_value_by_xpath(driver: webdriver.Chrome, url: str, xpath: str) -> str:
    if not url or not isinstance(url, str) or url.strip() == "":
        return np.nan
    try:
        driver.get(url)
        time.sleep(3)
        element = driver.find_element(By.XPATH, xpath)
        value = element.text.strip()
        return value.replace("A$", "")
    except Exception as e:
        print("Exception:", e)
        print("Exception occurred while fetching value for URL:", url)
        return np.nan

def get_ebay_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        http2=True,
        follow_redirects=True
    )
    try:
        response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    price = sel.css(".x-price-primary>span::text").get(default="").strip()
    return price

def get_gentronics_website_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not (url.startswith("https://www.googleadservices.com/pagead/aclk") or url.startswith("https://www.gentronics.com.au/")):
        return np.nan
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    try:
        response = session.get(url)
    except:
        return np.nan
    sel = Selector(response.text)
    price = sel.css("p.gentronics-price.price::text").get(default="").strip()
    price = price[1:] if price.startswith("$") else price
    return price.replace("per item", "").strip()

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

def get_hampdon_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.hampdon.com.au/"):
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
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                    "image/webp,*/*;q=0.8"
                ),
            },
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
    except (httpx.RequestError, httpx.ReadTimeout, Exception):
        return np.nan

    sel = Selector(response.text)
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

def get_weld_com_au_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.weld.com.au/product/"):
        return np.nan
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        },
        follow_redirects=True
    )
    response = session.get(url)
    sel = Selector(response.text)
    price = sel.css("p.price span.woocommerce-Price-amount.amount bdi::text").get(default="").strip()
    return price[1:] if price.startswith("$") else price

def get_weldconnect_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.weldconnect.com.au/"):
        return np.nan
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True
        ) as session:
            response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    return sel.css("div.h1[itemprop='price']::attr(content)").get(default="").strip()

def get_metweld_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://metweld.com.au/"):
        return np.nan
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15.0,
        ) as session:
            response = session.get(url)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    price = sel.css("span.price.price--withTax::text").get(default="").strip()
    return price[1:] if price.startswith("$") else price

def get_toolkitdepot_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://toolkitdepot.com.au/"):
        return np.nan
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15.0,
        ) as session:
            response = session.get(url)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    price = sel.css("span.price.price--withTax span::text").get(default="").strip()
    if not price:
        price = "".join(sel.css("span.price.price--withTax ::text").getall()).strip()
    return price[1:] if price.startswith("$") else price

def get_supercheapauto_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.supercheapauto.com.au/"):
        return np.nan
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    try:
        with httpx.Client(headers=headers, follow_redirects=True) as session:
            response = session.get(url, timeout=15.0)
    except (httpx.ReadTimeout, Exception):
        return np.nan
    sel = Selector(response.text)
    price_class = "".join(sel.xpath("//span[contains(@class, 'price-sales')]//span[contains(@class, 'promo-price')]/text()").getall()).strip()
    price_full = sel.xpath("/html/body/div[1]/div[14]/div[3]/div/div[2]/div/div[3]/span/span/text()").get(default="").strip()
    price = price_class if price_class else price_full
    return price[1:].strip() if price.startswith("$") else (price if price else np.nan)

def get_primesupplies_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.primesupplies.com.au/product/"):
        return np.nan
        
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15.0,
        ) as session:
            response = session.get(url)
    except (httpx.ReadTimeout, Exception) as e:
        print(f"Error fetching Prime Supplies URL {url}: {e}")
        return np.nan
        
    sel = Selector(response.text)
    
    price = sel.xpath("/html/body/div[2]/main/div[2]/div[2]/div[1]/p[2]/span/bdi/text()").get(default="").strip()
    
    if not price:
        price = sel.css("p.price span.woocommerce-Price-amount.amount bdi::text").get(default="").strip()
    
    if not price:
        price = sel.css(".price .woocommerce-Price-amount.amount::text").get(default="").strip()
    
    if price:
        price = price.replace("$", "").strip()
        price = price.replace("inc. GST", "").strip()
        return price
    else:
        return np.nan
    
def get_australia_industrial_group_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.australiaindustrialgroup.com.au/product-page/"):
        return np.nan
        
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15.0,
        ) as session:
            response = session.get(url)
    except (httpx.ReadTimeout, Exception) as e:
        print(f"Error fetching Australia Industrial Group URL {url}: {e}")
        return np.nan
        
    sel = Selector(response.text)
    price = sel.xpath("/html/body/div[1]/div/div[3]/div/main/div/div/div[2]/div/div/div/section/div[2]/div/div/div/div/div/div/article/div[2]/section[2]/div[1]/div/div/div[2]/span[1]/text()").get(default="").strip()
    if not price:
        price = sel.css('span[data-hook="formatted-primary-price"]::text').get(default="").strip()
    if not price:
        price = sel.css('span.hM4gpp[data-hook="formatted-primary-price"]::text').get(default="").strip()
    if not price:
        price = sel.css('div[data-hook="product-price"] span[data-wix-price]::text').get(default="").strip()
    if price:
        price = price.replace("$", "").replace(",", "").strip()
        return price
    else:
        return np.nan    
    
def get_trade_tools_price(url: str) -> str:
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        return np.nan
    if not url.startswith("https://www.tradetools.com/"):
        return np.nan
        
    try:
        with httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=15.0,
        ) as session:
            response = session.get(url)
    except (httpx.ReadTimeout, Exception) as e:
        print(f"Error fetching Trade Tools URL {url}: {e}")
        return np.nan
        
    sel = Selector(response.text)
    try:
        price_container = sel.css("div.price-2To")
        if not price_container:
            price_container = sel.css("div.priceContainer-3Tv")
        
        if price_container:
            dollar_sign = price_container.css("span:nth-child(1)::text").get("").strip()
            dollars = price_container.css("span:nth-child(2)::text").get("").strip()
            comma = price_container.css("span:nth-child(3)::text").get("").strip()
            cents_part = price_container.css("span:nth-child(4)::text").get("").strip()
            decimal_point = price_container.css("span.cents-1T3:nth-child(5)::text").get("").strip()
            cents = price_container.css("span.cents-1T3:nth-child(6)::text").get("").strip()
            
            full_price = f"{dollars}{cents_part}{decimal_point}{cents}".replace("$", "").replace(",", "").strip()
            if full_price:
                return full_price
    except Exception as e:
        print(f"Error extracting price components: {e}")
    
    try:
        price_text = sel.xpath('/html/body/div[2]/div[1]/main/div/div/div[2]/div/form/div[2]/div/div/div//text()').getall()
        price_text = [t.strip() for t in price_text if t.strip() and t.strip() != "Inc GST"]
        combined_price = "".join(price_text).replace("$", "").replace(",", "").replace(".", "")
        if combined_price and len(combined_price) > 2:
            dollars = combined_price[:-2]
            cents = combined_price[-2:]
            return f"{dollars}.{cents}"
    except Exception as e:
        print(f"Error extracting price with XPath: {e}")
    
    try:
        price_element = sel.css("div.priceRangeWrapper-232 span::text").getall()
        if price_element:
            price = "".join(price_element).replace("$", "").replace(",", "").replace("Inc GST", "").strip()
            return price
    except Exception as e:
        print(f"Error with fallback price extraction: {e}")
        
    return np.nan    

# ------------------------- Scraper Classes -------------------------

class CompanyScraper:
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern
        self.df = None
        self.stats = {}
    def get_price(self, url: str) -> str:
        raise NotImplementedError
    def scrape(self, df: pd.DataFrame) -> pd.DataFrame:
        df_company = df[df['Shop Name'].str.contains(self.pattern, case=False, na=False, regex=True)].copy()
        df_company['Price'] = df_company['PRODUCT LINK'].apply(self.get_price)
        df_company['Price_Bundle'] = df_company.get('BUNDLE LINK', np.nan)
        total = len(df_company)
        valid = df_company['PRODUCT LINK'].notna().sum()
        extracted = df_company['Price'].notna().sum()
        self.df = df_company
        self.stats = {"total_rows": total, "valid_product_links": valid, "extracted_prices": extracted}
        print(f"{self.name} stats: {self.stats}")
        return df_company

class EbayScraper(CompanyScraper):
    def __init__(self):
        super().__init__("EBAY", "EBAY")
    def get_price(self, url: str) -> str:
        return get_ebay_price(url)

class ElectroweldScraper(CompanyScraper):
    def __init__(self):
        super().__init__("ELECTROWELD WEBSITE", "electroweld website")
    def get_price(self, url: str) -> str:
        return get_electroweld_website_price(url)

class BilbaScraper(CompanyScraper):
    def __init__(self):
        super().__init__("BILBA", "Bilba")
    def get_price(self, url: str) -> str:
        return get_bilba_website_price(url)

class GentronicsScraper(CompanyScraper):
    def __init__(self):
        super().__init__("GENTRONICS", "GENTRONICS")
    def get_price(self, url: str) -> str:
        return get_gentronics_website_price(url)

class WeldComAuScraper(CompanyScraper):
    def __init__(self):
        super().__init__("WELD.COM.AU", "WELD.COM.AU")
    def get_price(self, url: str) -> str:
        return get_weld_com_au_price(url)

class WeldConnectScraper(CompanyScraper):
    def __init__(self):
        super().__init__("WELDCONNECT", "WELDCONNECT")
    def get_price(self, url: str) -> str:
        return get_weldconnect_price(url)

class MetweldScraper(CompanyScraper):
    def __init__(self):
        super().__init__("METRO WELDER SERVICE", "METRO WELDER SERVICE")
    def get_price(self, url: str) -> str:
        return get_metweld_price(url)

class ToolkitDepotScraper(CompanyScraper):
    def __init__(self):
        super().__init__("TKD", "TKD")
    def get_price(self, url: str) -> str:
        return get_toolkitdepot_price(url)

class SupercheapAutoScraper(CompanyScraper):
    def __init__(self):
        super().__init__("SUPERCHEAP AUTO", "SUPERCHEAP AUTO")
    def get_price(self, url: str) -> str:
        return get_supercheapauto_price(url)

class ToolsWarehouseScraper(CompanyScraper):
    def __init__(self):
        super().__init__("TOOLS WAREHOUSE", "TOOLS WAREHOUSE")
        self.xpath = "/html/body/main/div[1]/section/article/div[2]/div/div[6]/div[1]/div/div[4]/span[2]"
        self.driver = init_driver()
    def get_price(self, url: str) -> str:
        return fetch_value_by_xpath(self.driver, url, self.xpath)
    def close(self):
        close_driver(self.driver)

class VekToolsScraper(CompanyScraper):
    def __init__(self):
        super().__init__("VEK TOOLS", "VEK TOOLS")
    def get_price(self, url: str) -> str:
        return get_vektools_price(url)

class KennedysScraper(CompanyScraper):
    def __init__(self):
        super().__init__("KENNEDY'S WELDING SUPPLIES", "KENNEDY'S WELDING SUPPLIES")
    def get_price(self, url: str) -> str:
        return get_kennedys_price(url)

class TotalToolsScraper(CompanyScraper):
    def __init__(self):
        super().__init__("TOTAL TOOLS", "total tools")
    def get_price(self, url: str) -> str:
        return get_total_tools_price(url)

class WAIndustrialScraper(CompanyScraper):
    def __init__(self):
        super().__init__("WA INDUSTRIAL SUPPLIES WEBSITE", "WA INDUSTRIAL SUPPLIES WEBSITE")
        self.driver = init_driver()
    def get_price(self, url: str) -> str:
        return get_waindustrialsupplies_price(self.driver, url)
    def close(self):
        close_driver(self.driver)

class SydneyToolsScraper(CompanyScraper):
    def __init__(self):
        super().__init__("SYDNEY TOOLS", "SYDNEY TOOLS")
        self.driver = init_driver()
    def get_price(self, url: str) -> str:
        return get_sydney_tools_price(url, self.driver)
    def close(self):
        close_driver(self.driver)

class HareAndForbesScraper(CompanyScraper):
    def __init__(self):
        super().__init__("hare and forbes", "hare and forbes")
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
    def get_price(self, url: str) -> str:
        return get_hares_and_forbes_price(url, self.driver)
    def close(self):
        close_driver(self.driver)

class GasRepScraper(CompanyScraper):
    def __init__(self):
        super().__init__("GASREP", "GASREP")
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def get_price(self, url: str) -> str:
        return get_gasrep_price(url, self.driver)
    
    def close(self):
        close_driver(self.driver)

class AlphaweldScraper(CompanyScraper):
    def __init__(self):
        super().__init__("ALPHAWELD", "alphaweld")
    def get_price(self, url: str) -> str:
        return get_alphaweld_price(url)

class HampdonScraper(CompanyScraper):
    def __init__(self):
        super().__init__("HAMPDON", "hampdon website")
    def get_price(self, url: str) -> str:
        return get_hampdon_price(url)

class NationalWeldingScraper(CompanyScraper):
    def __init__(self):
        super().__init__("NATIONAL WELDING", "national welding")
    def get_price(self, url: str) -> str:
        return get_national_welding_price(url)
    
class PrimeSuppliesScraper(CompanyScraper):
    def __init__(self):
        super().__init__("PRIME SUPPLIES", "PRIME SUPPLIES")
    def get_price(self, url: str) -> str:
        return get_primesupplies_price(url)
    
class AustraliaIndustrialGroupScraper(CompanyScraper):
    def __init__(self):
        super().__init__("AUSTRALIA INDUSTRIAL GROUP", "AUSTRALIA INDUSTRIAL")
    def get_price(self, url: str) -> str:
        return get_australia_industrial_group_price(url)

class TradeToolsScraper(CompanyScraper):
    def __init__(self):
        super().__init__("TRADE TOOLS", "TRADE TOOLS")
    def get_price(self, url: str) -> str:
        return get_trade_tools_price(url)
    
class StaffordWeldingScraper(CompanyScraper):
    def __init__(self):
        super().__init__("STAFFORD WELDING PRODUCTS", "STAFFORD WELDING")
    def get_price(self, url: str) -> str:
        return get_stafford_welding_price(url)
    
class GasweldScraper(CompanyScraper):
    def __init__(self):
        super().__init__("GASWELD", "GASWELD")
    
    def get_price(self, url: str) -> str:
        return get_gasweld_price(url)
    
class WeldquipScraper(CompanyScraper):
    def __init__(self):
        super().__init__("WELDQUIP PRODUCTS", "WELDQUIP")
    
    def get_price(self, url: str) -> str:
        return get_weldquip_price(url)
    
from scrapers.toolking_scraper import get_toolking_price
class ToolKingScraper(CompanyScraper):
    def __init__(self):
        super().__init__("Robson's Tool King", "Tool King")
    
    def get_price(self, url: str) -> str:
        return get_toolking_price(url)


# ------------------------- End of Scraper Classes -------------------------

def read_and_prepare_df(input_file):
    df = pd.read_excel(input_file, sheet_name="Sheet2")
    df['PRODUCT SKU'] = df['PRODUCT SKU'].str.strip().str.upper()
    df['PRODUCT NAME'] = df['PRODUCT NAME'].str.strip().str.upper()
    df['Shop Name'] = df['Shop Name'].str.strip().str.upper()
    df.loc[df['Shop Name'] == 'WA INDUSTRIAL SUPPLIES', 'Shop Name'] += ' EBAY'
    df.loc[df['Shop Name'] == 'WElDERS ONLINE', 'Shop Name'] += ' EBAY'
    df_sub = df[['BRAND', 'PRODUCT SKU', 'PRODUCT NAME', 'Shop Name', 'PRODUCT LINK']].copy()
    df_sub[['BRAND', 'PRODUCT SKU', 'PRODUCT NAME']] = df_sub[['BRAND', 'PRODUCT SKU', 'PRODUCT NAME']].ffill()
    return df_sub

# A helper function that times the scraping process for each company.
def timed_scrape(scraper, df_sub):
    start = time.time()
    df_company = scraper.scrape(df_sub)
    elapsed = time.time() - start
    return df_company, elapsed

def scrape_all(df_sub, scrapers, scraper_output_folder, combined_csv_folder):
    df_list = []
    scraper_times = {}
    # Use ThreadPoolExecutor to run scrapers concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_scraper = {executor.submit(timed_scrape, scraper, df_sub): scraper for scraper in scrapers}
        for future in concurrent.futures.as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                df_company, elapsed = future.result()
                scraper_times[scraper.name] = elapsed
            except Exception as e:
                print(f"{scraper.name} generated an exception: {e}")
            else:
                df_list.append(df_company)
                filename = os.path.join(scraper_output_folder, f"{scraper.name.replace(' ', '_')}.csv")
                df_company.to_csv(filename, index=False)
                # Log any URLs with missing price
                missing_prices = df_company[df_company['Price'].isna()]
                for _, row in missing_prices.iterrows():
                    url = row['PRODUCT LINK']
                    logging.info(f"Missing Price - {scraper.name},{url}")
            if hasattr(scraper, 'close'):
                scraper.close()
    # Print and log elapsed time for each company
    for company, elapsed in scraper_times.items():
        message = f"{company} took {elapsed:.2f} seconds."
        print(message)
        logging.info(message)
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df.sort_values("PRODUCT NAME", inplace=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = os.path.join(combined_csv_folder, f"combined_{timestamp}.csv")
        combined_df.to_csv(combined_filename, index=False)
        print(f"Scraped all companies. Combined CSV saved as {combined_filename}")
    else:
        print("No data scraped.")

def scrape_single(df_sub, scraper, scraper_output_folder):
    start = time.time()
    df_company = scraper.scrape(df_sub)
    elapsed = time.time() - start
    filename = os.path.join(scraper_output_folder, f"{scraper.name.replace(' ', '_')}.csv")
    df_company.to_csv(filename, index=False)
    # Log URLs missing a price
    missing_prices = df_company[df_company['Price'].isna()]
    for _, row in missing_prices.iterrows():
        url = row['PRODUCT LINK']
        logging.info(f"Missing Price - {scraper.name},{url}")
    print(f"{scraper.name} took {elapsed:.2f} seconds.")
    logging.info(f"{scraper.name} took {elapsed:.2f} seconds.")
    if hasattr(scraper, 'close'):
        scraper.close()
    print(f"{scraper.name} data scraped and saved as {filename}")

def combine_csv(scrapers, scraper_output_folder, combined_csv_folder):
    dfs = []
    for scraper in scrapers:
        filename = os.path.join(scraper_output_folder, f"{scraper.name.replace(' ', '_')}.csv")
        if os.path.exists(filename):
            df_temp = pd.read_csv(filename)
            dfs.append(df_temp)
    
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.sort_values("PRODUCT NAME", inplace=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = os.path.join(combined_csv_folder, f"combined_{timestamp}.csv")
        combined_df.to_csv(combined_filename, index=False)
        print(f"CSV files combined into {combined_filename}")
    else:
        print("No CSV files found to combine.")

def main():
    input_file = 'Pricing.xlsx'
    scraper_output_folder = "scraper_outputs"
    combined_csv_folder = "combined_csvs"
    
    os.makedirs(scraper_output_folder, exist_ok=True)
    os.makedirs(combined_csv_folder, exist_ok=True)
    
    df_sub = read_and_prepare_df(input_file)
    print(df_sub.head())
    scrapers = [
        EbayScraper(),
        ElectroweldScraper(),
        BilbaScraper(),
        GentronicsScraper(),
        WeldComAuScraper(),
        WeldConnectScraper(),
        MetweldScraper(),
        ToolkitDepotScraper(),
        SupercheapAutoScraper(),
        ToolsWarehouseScraper(),
        VekToolsScraper(),
        KennedysScraper(),
        TotalToolsScraper(),
        WAIndustrialScraper(),
        SydneyToolsScraper(),
        HareAndForbesScraper(),
        AlphaweldScraper(),
        HampdonScraper(),
        NationalWeldingScraper(),
        PrimeSuppliesScraper(),
        AustraliaIndustrialGroupScraper(),
        TradeToolsScraper(),
        GasRepScraper(),
        StaffordWeldingScraper(),
        GasweldScraper(),
        WeldquipScraper(),
        ToolKingScraper()
    ]
    while True:
        print("\nMENU")
        print("1. Scrape all")
        print("2. Choose a company to scrape")
        print("3. Create new combined CSV")
        print("4. Exit")
        choice = input("Enter option: ").strip()
        if choice == "1":
            scrape_all(df_sub, scrapers, scraper_output_folder, combined_csv_folder)
        elif choice == "2":
            print("\nSelect a company to scrape:")
            for idx, scraper in enumerate(scrapers, start=1):
                print(f"{idx}. {scraper.name}")
            comp_choice = input("Enter company number: ").strip()
            try:
                comp_idx = int(comp_choice) - 1
                if 0 <= comp_idx < len(scrapers):
                    scrape_single(df_sub, scrapers[comp_idx], scraper_output_folder)
                else:
                    print("Invalid company number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            combine_csv(scrapers, scraper_output_folder, combined_csv_folder)
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
