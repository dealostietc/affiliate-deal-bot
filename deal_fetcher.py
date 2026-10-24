import os
import requests

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def fetch_live_deals(limit=5):
    """
    Dynamically fetches live offers and deals directly from the official 
    Cuelinks Offers API for Indian e-commerce giants (Amazon, Flipkart, etc.).
    """
    print("📡 Querying official Cuelinks API for live Indian merchant offers...")
    
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing!")
        return []

    api_url = "https://developers.cuelinks.com/pub_api/v3/offers"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Filter explicitly for major Indian e-commerce campaigns:
    # 817 = Amazon India, 1 = Flipkart
    params = {
        "per_page": limit * 2, # Fetch extra to account for filtering
        "campaigns": "817,1"  
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        print(f"📡 Cuelinks API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get("data") or data.get("offers") or []
            
            extracted_deals = []
            for offer in offers:
                if len(extracted_deals) >= limit:
                    break
                    
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
                    title = offer.get("title") or "Top Indian Store Offer"
                    campaign_name = offer.get("campaign_name", "Amazon / Flipkart")
                    coupon_code = offer.get("coupon_code")
                    
                    offer_text = f"Code: {coupon_code}" if coupon_code else "Special Discount Offer"
                    
                    extracted_deals.append({
                        "id": f"cuelinks_api_{offer_id}",
                        "title": title[:110],
                        "effective_price": "Best Live Price",
                        "cb_offer_text": offer_text,
                        "raw_cb_link": landing_url,
                        "raw_buy_link": landing_url,
                        "discounts_text": f"Live offer via {campaign_name}. Grab before expiry!"
                    })
            
            print(f"✅ Successfully fetched {len(extracted_deals)} live deals from Cuelinks API!")
            return extracted_deals
        else:
            print(f"⚠️ Cuelinks API error status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception querying Cuelinks Offers API: {e}")
    
    return []
