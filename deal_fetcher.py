import os
import requests
import xml.etree.ElementTree as ET

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def fetch_cuelinks_offers(limit=5):
    """
    Attempts to fetch live coupons/offers directly from Cuelinks V3 API.
    """
    if not CUELINKS_API_KEY:
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
            print(f"🔍 Raw Cuelinks Offers Response: {data}")  # Inspect structure
            
            # Support multiple V3 envelope types
            offers = data.get("offers") or data.get("data") or (data if isinstance(data, list) else [])
            
            parsed_deals = []
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                
                offer_id = str(offer.get("id") or hash(offer.get("title", "")))
                landing_url = offer.get("url") or offer.get("affiliate_url") or offer.get("landing_page")
                
                if landing_url:
                    parsed_deals.append({
                        "id": f"cuelinks_offer_{offer_id}",
                        "title": offer.get("title") or offer.get("name") or "Special Deal",
                        "effective_price": offer.get("sale_price") or "Best Price",
                        "cb_offer_text": f"Coupon: {offer.get('coupon_code')}" if offer.get("coupon_code") else None,
                        "raw_cb_link": None,
                        "raw_buy_link": landing_url,
                        "discounts_text": offer.get("description") or f"Store: {offer.get('store_name', 'Featured Merchant')}"
                    })
            return parsed_deals
    except Exception as e:
        print(f"❌ Exception in Cuelinks Offers API: {e}")
    
    return []

def fetch_rss_deals(limit=5):
    """
    Fallback deal aggregator: Fetches live top deals from RSS feeds (e.g., DesiDime).
    Extracts title, link, and price alerts dynamically.
    """
    print("📡 Fetching fallback deals from public deal stream...")
    rss_url = "https://www.desidime.com/feed"
    deals = []

    try:
        response = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            for item in root.findall("./channel/item")[:limit]:
                title = item.find("title").text if item.find("title") is not None else "Top Deal"
                link = item.find("link").text if item.find("link") is not None else None
                description = item.find("description").text if item.find("description") is not None else ""
                
                if link:
                    # Clean title and generate unique ID
                    clean_id = f"rss_deal_{hash(link)}"
                    deals.append({
                        "id": clean_id,
                        "title": title[:100],  # Shorten for neat formatting
                        "effective_price": "Deal Price",
                        "cb_offer_text": "Hot Deal Alert",
                        "raw_cb_link": None,
                        "raw_buy_link": link,
                        "discounts_text": "Grab it before the price changes!"
                    })
            print(f"✅ Fetched {len(deals)} dynamic deals from fallback stream!")
    except Exception as e:
        print(f"❌ Exception in RSS fetcher: {e}")

    return deals

def fetch_live_deals(limit=5):
    """
    Main Orchestrator: Tries Cuelinks Offers API first; falls back to live deal stream if empty.
    """
    deals = fetch_cuelinks_offers(limit=limit)
    if not deals:
        print("ℹ️ Cuelinks API returned 0 deals. Switching to live public deal feed...")
        deals = fetch_rss_deals(limit=limit)
    return deals
