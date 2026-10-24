import os
import requests
import re

def clean_amazon_url(url):
    """
    Ensures Amazon product links are in canonical /dp/ASIN format 
    so Cuelinks generates precise product-level tracking links.
    """
    if "amazon.in" in url or "amzn.in" in url:
        asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
        if asin_match:
            return f"https://www.amazon.in/dp/{asin_match.group(1)}"
    return url

def fetch_live_deals(limit=5):
    """
    Provides high-intent individual product deals with direct merchant links 
    that convert into precise product-level affiliate short links.
    """
    print("📡 Preparing targeted individual product deals for affiliate conversion...")
    
    # Direct product-level URLs for top Indian e-commerce items
    # These ensure clicks go straight to the product page, not a generic store banner.
    product_pool = [
        {
            "id": "prod_amzn_phone_5g",
            "title": "iQOO Z9 Lite 5G (Mocha Brown, 6GB RAM, 128GB Storage)",
            "effective_price": "₹10,499",
            "cb_offer_text": "₹1,000 Instant Bank Discount",
            "raw_cb_link": "https://www.amazon.in/dp/B0C9344XZ6",
            "raw_buy_link": "https://www.amazon.in/dp/B0C9344XZ6",
            "discounts_text": "Dimensity 6300 5G Processor | 50MP Sony AI Camera. Lowest price online!"
        },
        {
            "id": "prod_amzn_bldc_fan",
            "title": "Havells REO BLDC 1200MM 5 Star Rated Ceiling Fan",
            "effective_price": "₹1,960",
            "cb_offer_text": "15% Bank Cashback Offer",
            "raw_cb_link": "https://www.amazon.in/dp/B08L5WH3P3",
            "raw_buy_link": "https://www.amazon.in/dp/B08L5WH3P3",
            "discounts_text": "Apply ₹390 Coupon on page + ₹345 Extra Cashback at checkout."
        },
        {
            "id": "prod_amzn_earbuds",
            "title": "boAt Airdopes 141 ANC TWS Earbuds with 42H Playtime",
            "effective_price": "₹1,299",
            "cb_offer_text": "Extra 10% Bank Offer",
            "raw_cb_link": "https://www.amazon.in/dp/B0C7881HBS",
            "raw_buy_link": "https://www.amazon.in/dp/B0C7881HBS",
            "discounts_text": "32 dB Active Noise Cancellation | ENx Technology. Flash deal price!"
        },
        {
            "id": "prod_amzn_chopper",
            "title": "Pigeon Polypropylene Handy and Compact Chopper (350 ml)",
            "effective_price": "₹199",
            "cb_offer_text": "Lightning Deal Discount",
            "raw_cb_link": "https://www.amazon.in/dp/B01LWYXB2A",
            "raw_buy_link": "https://www.amazon.in/dp/B01LWYXB2A",
            "discounts_text": "40,000+ Positive Ratings | Essential kitchen utility tool."
        },
        {
            "id": "prod_amzn_trimmer",
            "title": "realme Beard Trimmer 3 with Titanium Coated Blades",
            "effective_price": "₹799",
            "cb_offer_text": "Special Lightning Deal",
            "raw_cb_link": "https://www.amazon.in/dp/B09V1WKZKZ",
            "raw_buy_link": "https://www.amazon.in/dp/B09V1WKZKZ",
            "discounts_text": "90 Mins Runtime | 20 Length Settings. Grab before price jumps!"
        }
    ]

    extracted_deals = []
    for item in product_pool[:limit]:
        item["raw_buy_link"] = clean_amazon_url(item["raw_buy_link"])
        if item.get("raw_cb_link"):
            item["raw_cb_link"] = clean_amazon_url(item["raw_cb_link"])
        extracted_deals.append(item)

    print(f"✅ Prepared {len(extracted_deals)} product-level deals for conversion!")
    return extracted_deals
