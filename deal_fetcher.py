import os
import requests
import re
from xml.etree import ElementTree as ET

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def fetch_cuelinks_offers(limit=5):
    """
    Fetches live offers directly from Cuelinks V3 API.
    """
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing!")
        return []

    api_url = "https://developers.cuelinks.com/pub_api/v3/offers"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers, params={"per_page": limit})
        print(f"📡 Cuelinks Offers API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get("data") or data.get("offers") or []
            
            parsed_deals = []
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                
                offer_id = str(offer.get("id") or hash(offer.get("title", "")))
                
                # Check all possible URL fields in Cuelinks V3 schema
                landing_url = (
                    offer.get("tracking_url") or 
                    offer.get("url") or 
                    offer.get("affiliate_url") or 
                    offer.get("landing_page")
                )
                
                if landing_url:
                    parsed_deals.append({
                        "id": f"cuelinks_offer_{offer_id}",
                        "title": offer.get("title") or "Special Discount Offer",
                        "effective_price": "Special Price",
                        "cb_offer_text": f"Coupon: {offer.get('coupon_code')}" if offer.get("coupon_code") else None,
                        "raw_cb_link": None,
                        "raw_buy_link": landing_url,
                        "discounts_text": offer.get("description", "").strip() or f"Store: {offer.get('campaign_name', 'Merchant')}"
                    })
            
            print(f"✅ Extracted {len(parsed_deals)} live deals from Cuelinks!")
            return parsed_deals
    except Exception as e:
        print(f"❌ Exception in Cuelinks Offers API: {e}")
    
    return []

def fetch_rss_deals(limit=5):
    """
    Fallback deal stream using robust regex pattern matching on DesiDime feed.
    """
    print("📡 Fetching fallback deals from public deal feed...")
    rss_url = "https://www.desidime.com/feed"
    deals = []

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(rss_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            for item in items[:limit]:
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                
                title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if title_match else "Hot Deal Alert"
                link = link_match.group(1).strip() if link_match else None
                
                if link:
                    clean_id = f"rss_deal_{abs(hash(link))}"
                    deals.append({
                        "id": clean_id,
                        "title": title[:120],
                        "effective_price": "Deal Price",
                        "cb_offer_text": "Loot Alert ⚡",
                        "raw_cb_link": None,
                        "raw_buy_link": link,
                        "discounts_text": "Check platform for applicable coupons & cashback!"
                    })
            print(f"✅ Fetched {len(deals)} dynamic deals from fallback stream!")
    except Exception as e:
        print(f"❌ Exception in RSS fetcher: {e}")

    return deals

def fetch_live_deals(limit=5):
    """
    Main Orchestrator: Tries Cuelinks Offers API first; falls back to RSS feed.
    """
    deals = fetch_cuelinks_offers(limit=limit)
    if not deals:
        print("ℹ️ Cuelinks API returned 0 valid deals. Switching to live public deal feed...")
        deals = fetch_rss_deals(limit=limit)
    return deals
