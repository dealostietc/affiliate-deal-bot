import os
import requests
import re

def clean_amazon_url(url):
    """
    Extracts clean Amazon India product URL (/dp/ASIN) so Cuelinks converts it reliably.
    """
    if "amazon.in" in url or "amzn.in" in url:
        asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
        if asin_match:
            return f"https://www.amazon.in/dp/{asin_match.group(1)}"
    return url

def fetch_live_deals(limit=5):
    """
    Dynamically fetches live individual product deals from public Indian deal streams.
    Includes strict timeout handling and secondary endpoints to prevent execution stalls.
    """
    print("📡 Dynamically fetching live Indian product deals...")
    
    extracted_deals = []
    seen_links = set()

    # Priority 1: Public Indian Product Deal Streams
    feed_urls = [
        "https://www.desidime.com/feed",
        "https://www.grabon.in/feed/"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    for rss_url in feed_urls:
        if len(extracted_deals) >= limit:
            break
        try:
            print(f"🔍 Attempting stream: {rss_url}")
            response = requests.get(rss_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                
                for item in items:
                    if len(extracted_deals) >= limit:
                        break
                        
                    title_m = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                    link_m = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                    desc_m = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    
                    title = title_m.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if title_m else ""
                    raw_link = link_m.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if link_m else ""
                    desc = desc_m.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if desc_m else ""

                    if not raw_link or not title:
                        continue

                    # Strict Filter: Target individual Indian e-commerce merchants
                    valid_domains = ['amazon.in', 'flipkart.com', 'myntra.com', 'ajio.com', 'croma.com', 'blinkit.com', 'zepto', 'meesho.com']
                    is_indian_merchant = any(domain in raw_link.lower() or domain in desc.lower() for domain in valid_domains)
                    
                    clean_url = clean_amazon_url(raw_link)

                    if is_indian_merchant and clean_url not in seen_links:
                        seen_links.add(clean_url)
                        
                        price_match = re.search(r'(?:at|@)\s*(?:Rs\.?|₹)\s*([\d,]+)', title, re.IGNORECASE)
                        price = f"₹{price_match.group(1)}" if price_match else "Flash Deal Price"
                        
                        deal_id = f"dyn_prod_{abs(hash(clean_url))}"
                        clean_desc = re.sub(r'<[^>]+>', '', desc)[:130]

                        extracted_deals.append({
                            "id": deal_id,
                            "title": title[:110],
                            "effective_price": price,
                            "cb_offer_text": "⚡ Live Price Drop",
                            "raw_cb_link": None,
                            "raw_buy_link": clean_url,
                            "discounts_text": clean_desc if clean_desc else "Limited time loot offer. Grab before stock ends!"
                        })
        except Exception as e:
            print(f"⚠️ Feed source error ({rss_url}): {e}")

    print(f"✅ Extracted {len(extracted_deals)} live dynamic product deals!")
    return extracted_deals
