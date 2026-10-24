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
    Dynamically fetches live individual product deals by parsing both RSS and Atom feeds
    from top Indian deal aggregators.
    """
    print("📡 Dynamically fetching live Indian product deals from RSS/Atom streams...")
    
    extracted_deals = []
    seen_links = set()

    feed_urls = [
        "https://www.desidime.com/feed",
        "https://freekamaal.com/feed/",
        "https://www.grabon.in/feed/"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, text/html, */*"
    }

    for rss_url in feed_urls:
        if len(extracted_deals) >= limit:
            break
        try:
            print(f"🔍 Attempting stream: {rss_url}")
            response = requests.get(rss_url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                text = response.text
                
                # Check for Cloudflare/WAF block page
                if "<html" in text.lower() and "cloudflare" in text.lower():
                    print(f"⚠️ Stream blocked by Cloudflare: {rss_url}")
                    continue

                # Parse both RSS (<item>) and Atom (<entry>) formats
                entries = re.findall(r'<item>(.*?)</item>', text, re.DOTALL)
                if not entries:
                    entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
                
                print(f"   Found {len(entries)} items/entries in feed.")

                for entry in entries:
                    if len(extracted_deals) >= limit:
                        break
                        
                    title_m = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
                    
                    # Extract link supporting both <link>url</link> and <link href="url"/>
                    link_m = re.search(r'<link[^>]*href=["\'](.*?)["\']', entry, re.DOTALL)
                    if not link_m:
                        link_m = re.search(r'<link>(.*?)</link>', entry, re.DOTALL)
                        
                    desc_m = re.search(r'<description[^>]*>(.*?)</description>', entry, re.DOTALL)
                    if not desc_m:
                        desc_m = re.search(r'<content[^>]*>(.*?)</content>', entry, re.DOTALL)
                    
                    title = title_m.group(1) if title_m else ""
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title).strip()

                    raw_link = link_m.group(1) if link_m else ""
                    raw_link = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', raw_link).strip()

                    desc = desc_m.group(1) if desc_m else ""
                    desc = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', desc).strip()

                    if not raw_link or not title:
                        continue

                    # Target Indian e-commerce platforms
                    valid_domains = ['amazon.in', 'flipkart.com', 'myntra.com', 'ajio.com', 'croma.com', 'blinkit.com', 'zepto', 'meesho.com']
                    is_indian_merchant = any(domain in raw_link.lower() or domain in desc.lower() or domain in title.lower() for domain in valid_domains)
                    
                    clean_url = clean_amazon_url(raw_link)

                    if is_indian_merchant and clean_url not in seen_links:
                        seen_links.add(clean_url)
                        
                        price_match = re.search(r'(?:at|@)\s*(?:Rs\.?|₹)\s*([\d,]+)', title, re.IGNORECASE)
                        price = f"₹{price_match.group(1)}" if price_match else "Live Deal Price"
                        
                        deal_id = f"dyn_prod_{abs(hash(clean_url))}"
                        clean_desc = re.sub(r'<[^>]+>', '', desc)[:130]

                        extracted_deals.append({
                            "id": deal_id,
                            "title": title[:110],
                            "effective_price": price,
                            "cb_offer_text": "⚡ Live Price Drop",
                            "raw_cb_link": None,
                            "raw_buy_link": clean_url,
                            "discounts_text": clean_desc if clean_desc else "Limited time deal. Grab before stock ends!"
                        })
        except Exception as e:
            print(f"⚠️ Feed error ({rss_url}): {e}")

    print(f"✅ Successfully extracted {len(extracted_deals)} live dynamic product deals!")
    return extracted_deals
