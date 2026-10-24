import os
import requests

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def fetch_cuelinks_offers(limit=5):
    """
    Fetches live offers filtered specifically for major Indian e-commerce campaigns.
    """
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing!")
        return []

    api_url = "https://developers.cuelinks.com/pub_api/v3/offers"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # FILTER EXPLICITLY FOR INDIAN MERCHANTS 
    # 817 = Amazon India, 1 = Flipkart (You can add more comma-separated IDs if needed)
    params = {
        "per_page": limit,
        "campaigns": "817,1" 
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        print(f"📡 Cuelinks Indian Store Offers Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get("data") or data.get("offers") or []
            
            parsed_deals = []
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                
                offer_id = str(offer.get("id") or hash(offer.get("title", "")))
                landing_url = (
                    offer.get("tracking_url") or 
                    offer.get("url") or 
                    offer.get("affiliate_url") or 
                    offer.get("landing_page")
                )
                
                if landing_url:
                    parsed_deals.append({
                        "id": f"indian_deal_{offer_id}",
                        "title": offer.get("title") or "Indian Store Deal",
                        "effective_price": offer.get("sale_price") or "Best Price",
                        "cb_offer_text": f"Code: {offer.get('coupon_code')}" if offer.get("coupon_code") else "Special Offer",
                        "raw_cb_link": None,
                        "raw_buy_link": landing_url,
                        "discounts_text": f"Store: {offer.get('campaign_name', 'Top Merchant')}"
                    })
            
            print(f"✅ Extracted {len(parsed_deals)} deals from Amazon/Flipkart/Indian merchants!")
            return parsed_deals
    except Exception as e:
        print(f"❌ Exception querying Indian store offers: {e}")
    
    return []

def fetch_live_deals(limit=5):
    """
    Main Orchestrator for Indian Deals.
    """
    return fetch_cuelinks_offers(limit=limit)
