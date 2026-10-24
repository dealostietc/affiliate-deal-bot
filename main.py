import json
import os
from affiliate_converter import convert_to_affiliate_link
from telegram_bot import send_deal

# Load previously posted deals to avoid duplicates
CACHE_FILE = "posted_deals.json"

def load_posted_deals():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted_deals(posted_list):
    with open(CACHE_FILE, "w") as f:
        json.dump(posted_list, f, indent=2)

def run_pipeline():
    posted_deals = load_posted_deals()
    
    # Example Deal Object (Replace with dynamic web scraping/API fetching)
    sample_deals = [
        {
            "id": "havells_reo_bldc_1200mm",
            "title": "Havells REO BLDC 1200MM 5 Star Rated Ceiling Fan",
            "effective_price": "1960",
            "cb_offer_text": "15% CB Offer",
            "raw_cb_link": "https://www.amazon.in/dp/example_cb",
            "raw_buy_link": "https://www.amazon.in/dp/B0EXAMPLE",
            "discounts_text": "Apply Rs.390 Coupon + Rs.345 Cashback"
        }
    ]

    for deal in sample_deals:
        if deal["id"] in posted_deals:
            print(f"Skipping deal {deal['id']} (already posted).")
            continue

        # Convert links to affiliate links
        deal["cb_offer_link"] = convert_to_affiliate_link(deal["raw_cb_link"]) if deal.get("raw_cb_link") else None
        deal["affiliate_buy_link"] = convert_to_affiliate_link(deal["raw_buy_link"])

        # Send to Telegram
        success = send_deal(deal)
        if success:
            posted_deals.append(deal["id"])
            print(f"Successfully posted deal: {deal['title']}")

    save_posted_deals(posted_deals)

if __name__ == "__main__":
    run_pipeline()
