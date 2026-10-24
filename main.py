import os
import json
import requests

# Load Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

CACHE_FILE = "posted_deals.json"

def load_posted_deals():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted_deals(posted_list):
    with open(CACHE_FILE, "w") as f:
        json.dump(posted_list, f, indent=2)

def convert_to_affiliate_link(original_url):
    if not original_url:
        return ""
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing!")
        return original_url

    api_url = "https://developers.cuelinks.com/pub_api/v3/links/convert"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": original_url, "shorten": True}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        print(f"🔗 Cuelinks Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            # Fallback chain for Cuelinks V3 response fields
            return data.get("short_url") or data.get("tracking_url") or data.get("affiliate_url") or original_url
        else:
            print(f"⚠️ Cuelinks conversion failed: {data}")
            return original_url
    except Exception as e:
        print(f"❌ Exception during Cuelinks conversion: {e}")
        return original_url

def send_deal_to_telegram(deal):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("❌ Telegram Bot Token or Channel ID is missing!")
        return False

    title = deal.get('title', '')
    price = deal.get('effective_price', '')
    cb_text = deal.get('cb_offer_text', '')
    cb_link = deal.get('cb_offer_link', '')
    buy_link = deal.get('affiliate_buy_link', '')
    discounts = deal.get('discounts_text', '')

    # Construct clean message using HTML tags to avoid Markdown parsing crashes
    message = f"<b>{title} at {price}</b>\n\n"
    
    if cb_link and cb_text:
        message += f"Collect {cb_text} : {cb_link}\n\n"
        
    message += f"Then Buy : {buy_link}\n\n"
    
    if discounts:
        message += f"{discounts}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message.strip(),
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        print(f"📢 Telegram API Response: {res_data}")
        return res_data.get("ok", False)
    except Exception as e:
        print(f"❌ Exception sending to Telegram: {e}")
        return False

def run_pipeline():
    print("🚀 Starting deal automation pipeline...")
    posted_deals = load_posted_deals()

    # Sample deal matching your exact requested layout
    sample_deals = [
        {
            "id": "havells_reo_bldc_1200mm_v3",
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
            print(f"⏭️ Skipping deal {deal['id']} (already exists in posted_deals.json).")
            continue

        print(f"🔄 Converting links for: {deal['title']}")
        deal["cb_offer_link"] = convert_to_affiliate_link(deal["raw_cb_link"]) if deal.get("raw_cb_link") else None
        deal["affiliate_buy_link"] = convert_to_affiliate_link(deal["raw_buy_link"])

        print(f"📤 Posting to Telegram channel...")
        success = send_deal_to_telegram(deal)
        
        if success:
            posted_deals.append(deal["id"])
            print(f"✅ Successfully posted and cached deal ID: {deal['id']}")
        else:
            print(f"❌ Failed to post deal ID: {deal['id']}")

    save_posted_deals(posted_deals)
    print("🏁 Pipeline execution finished.")

if __name__ == "__main__":
    run_pipeline()
