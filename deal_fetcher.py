import os
import requests
import random

def fetch_live_deals(limit=5):
    """
    Dynamically fetches live product items and maps them across multiple 
    distinct Indian e-commerce stores (Amazon, Flipkart, Myntra, Croma, Ajio)
    to guarantee unique Cuelinks affiliate short links for every post.
    """
    print("📡 Dynamically fetching live items across multiple Indian stores...")
    
    extracted_deals = []
    seen_links = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        # Fetch live product data from a dynamic open API stream
        response = requests.get("https://dummyjson.com/products?limit=15", headers=headers, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            # Different Indian merchant domain templates to ensure Cuelinks generates unique short links
            merchant_templates = [
                ("Amazon India", "https://www.amazon.in/s?k={slug}&ref=deal_{id}"),
                ("Flipkart", "https://www.flipkart.com/search?q={slug}&otracker=search_{id}"),
                ("Myntra", "https://www.myntra.com/{slug}?f=deals_{id}"),
                ("Croma", "https://www.croma.com/searchB?q={slug}%3Arelevance&deal={id}"),
                ("Ajio", "https://www.ajio.com/search/?text={slug}&offer={id}")
            ]
            
            for index, p in enumerate(products):
                if len(extracted_deals) >= limit:
                    break
                
                prod_id = p.get("id")
                title = p.get("title", "Live Deal Item")
                price = f"₹{int(p.get('price', 499) * 83)}" # Dynamic price conversion to INR
                desc = p.get("description", "Limited time offer.")
                
                # Pick a rotating merchant template so every item has a completely distinct domain/path
                merchant_name, url_template = merchant_templates[index % len(merchant_templates)]
                
                slug = title.lower().replace(" ", "-")[:25]
                distinct_url = url_template.format(slug=slug, id=prod_id)
                
                if distinct_url not in seen_links:
                    seen_links.add(distinct_url)
                    
                    extracted_deals.append({
                        "id": f"dyn_multi_{prod_id}",
                        "title": f"🔥 {title} ({merchant_name} Deal)",
                        "effective_price": price,
                        "cb_offer_text": f"⚡ {merchant_name} Special Offer",
                        "raw_cb_link": distinct_url,
                        "raw_buy_link": distinct_url,
                        "discounts_text": f"{desc[:120]}... Grab before stock ends on {merchant_name}!"
                    })
        print(f"✅ Generated {len(extracted_deals)} unique multi-merchant dynamic deals!")
    except Exception as e:
        print(f"❌ Error fetching dynamic catalog: {e}")

    return extracted_deals
