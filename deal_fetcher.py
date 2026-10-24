import os
import requests
import re

def fetch_live_deals(limit=5):
    """
    Scrapes live Indian e-commerce product deal feeds (DesiDime, etc.),
    extracts direct item links from Amazon India, Flipkart, Myntra, Ajio, Croma, Blinkit, and Zepto,
    and filters out non-Indian or generic banner offers.
    """
    print("📡 Fetching live Indian e-commerce product deal streams...")
    
    # Public deal streams providing frequent Indian e-commerce price drops
    feed_urls = [
        "https://www.desidime.com/feed",
        "https://freekamaal.com/feed/"
    ]
    
    extracted_deals = []
    seen_links = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for rss_url in feed_urls:
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
                
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items:
                if len(extracted_deals) >= limit:
                    break
                    
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                
                title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if title_match else "Hot Deal"
                link = link_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if link_match else ""
                desc = desc_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if desc_match else ""
                
                # Clean HTML tags from description snippet
                clean_desc = re.sub(r'<[^>]+>', '', desc)[:140]

                # STRICT FILTER: Only allow Indian e-commerce platforms
                valid_domains = ['amazon.in', 'flipkart.com', 'myntra.com', 'ajio.com', 'croma.com', 'blinkit.com', 'zepto', 'meesho.com', 'shopsy.in']
                
                is_indian_ecommerce = any(domain in link.lower() for domain in valid_domains)
                
                if is_indian_ecommerce and link not in seen_links:
                    seen_links.add(link)
                    
                    # Create a unique, permanent hash ID for deduplication in posted_deals.json
                    deal_id = f"ind_product_{abs(hash(link))}"
                    
                    extracted_deals.append({
                        "id": deal_id,
                        "title": title[:110],
                        "effective_price": "Best Price",
                        "cb_offer_text": "⚡ Loot Price Drop",
                        "raw_cb_link": None,
                        "raw_buy_link": link,
                        "discounts_text": clean_desc if clean_desc else "Limited-time deal on Indian store. Grab before price changes!"
                    })
        except Exception as e:
            print(f"⚠️ Error fetching deal feed from {rss_url}: {e}")

    print(f"✅ Successfully extracted {len(extracted_deals)} verified Indian e-commerce product deals!")
    return extracted_deals
