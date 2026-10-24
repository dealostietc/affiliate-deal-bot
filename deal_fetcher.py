import os
import requests

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def fetch_live_deals(limit=10):
    """
    Fetches dynamic deals and coupons from Cuelinks Offers API.
    Fallback: Offers API endpoint on Cuelinks v3/offers or pub_api/v3/offers.
    """
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing. Cannot fetch live deals.")
        return []

    # Cuelinks V3 Offers Endpoint
    api_url = "https://developers.cuelinks.com/pub_api/v3/offers"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {
        "page": 1,
        "per_page": limit,
        "status": "active"
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        print(f"📡 Dynamic Deal Fetch Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            offers = data.get("offers") or data.get("data") or []
            
            parsed_deals = []
            for offer in offers:
                # Generate unique ID for deduplication
                offer_id = str(offer.get("id") or offer.get("code") or hash(offer.get("title")))
                
                deal = {
                    "id": f"cuelinks_offer_{offer_id}",
                    "title": offer.get("title") or offer.get("name") or "Special Discount Offer",
                    "effective_price": offer.get("sale_price") or offer.get("offer_price") or "Best Price",
                    "cb_offer_text": offer.get("coupon_code") and f"Coupon: {offer.get('coupon_code')}",
                    "raw_cb_link": None,
                    "raw_buy_link": offer.get("url") or offer.get("affiliate_url") or offer.get("landing_page"),
                    "discounts_text": offer.get("description") or f"Store: {offer.get('store_name', 'Top Store')}"
                }
                
                if deal["raw_buy_link"]:
                    parsed_deals.append(deal)
                    
            print(f"✅ Dynamically fetched {len(parsed_deals)} live deals!")
            return parsed_deals
        else:
            print(f"⚠️ Failed to fetch dynamic deals: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception while fetching dynamic deals: {e}")
        return []
