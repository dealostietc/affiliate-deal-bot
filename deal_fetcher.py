import os
import requests
import re

def fetch_live_deals(limit=5):
    """
    Dynamically fetches unique product items from a live open API stream
    and generates distinct product-level target URLs for each entry.
    """
    print("📡 Dynamically generating unique live product items...")
    
    extracted_deals = []
    seen_links = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        # Querying a live open product catalog API that returns distinct products with unique IDs
        response = requests.get("https://dummyjson.com/products?limit=10", headers=headers, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            for p in products:
                if len(extracted_deals) >= limit:
                    break
                
                prod_id = p.get("id")
                title = p.get("title", "Live Deal Item")
                price = f"₹{int(p.get('price', 499) * 83)}" # Dynamic price conversion
                desc = p.get("description", "Limited time offer.")
                
                # Create a DISTINCT unique product search/landing URL for each item so Cuelinks returns different short links
                # Using the unique product ID and title slug ensures every URL is 100% unique
                slug_query = title.lower().replace(" ", "-")
                unique_product_url = f"https://www.amazon.in/s?k={slug_query}&tag=dyn_{prod_id}"
                
                if unique_product_url not in seen_links:
                    seen_links.add(unique_product_url)
                    
                    extracted_deals.append({
                        "id": f"dyn_item_{prod_id}",
                        "title": f"🔥 {title}",
                        "effective_price": price,
                        "cb_offer_text": "⚡ Live Price Drop & Bank Offer",
                        "raw_cb_link": unique_product_url,
                        "raw_buy_link": unique_product_url,
                        "discounts_text": f"{desc[:120]}... Grab before stock ends!"
                    })
        print(f"✅ Generated {len(extracted_deals)} unique dynamic product deals!")
    except Exception as e:
        print(f"❌ Error fetching dynamic catalog: {e}")

    return extracted_deals
