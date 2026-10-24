import os
import json
import requests
from deal_fetcher import fetch_live_deals

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
    """
    Converts merchant URLs into Cuelinks short links.
    """
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
        
        if response.status_code in [200, 201]:
            res_data = data.get("data", {})
            return res_data.get("short_url") or res_data.get("tracking_url") or res_data.get("affiliate_url") or original_url
        else:
            print(f"⚠️ Link conversion fallback: {response.status_code}")
            return original_url
    except Exception as e:
        print(f"❌ Exception in conversion: {e}")
        return original_url

def send_deal_to_telegram(deal):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("❌ Missing Telegram credentials.")
        return False

    title = deal.get('title', '')
    price = deal.get('effective_price', '')
    cb_text = deal.get('cb_offer_text', '')
    cb_link = deal.get('cb_offer_link', '')
    buy_link = deal.get('affiliate_buy_link', '')
    discounts = deal.get('discounts_text', '')

    message = f"<b>{title} at {price}</b>\n\n"
    
    if cb_link and cb_text:
        message += f"Collect {cb_text} : {cb_link}\n\n"
    elif cb_text:
        message += f"<b>Offer Info:</b> {cb_text}\n\n"
        
    message += f"Then Buy : {buy_link}\n\n"
    
    if discounts:
        message += f"<i>{discounts}</i>"

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
        print(f"📢 Telegram API Status: {res_data.get('ok')}")
        return res_data.get("ok", False)
    except Exception as e:
        print(f"❌ Telegram exception: {e}")
        return False

def run_pipeline():
    print("🚀 Starting dynamic deal automation pipeline...")
    posted_deals = load_posted_deals()

    # Dynamic fetching from Cuelinks Live API (no hardcoded deals)
    live_deals = fetch_live_deals(limit=5)

    if not live_deals:
        print("ℹ️ No new live deals returned from the API.")
        return

    for deal in live_deals:
        if deal["id"] in posted_deals:
            print(f"⏭️ Skipping deal '{deal['title'][:30]}...' (already posted).")
            continue

        print(f"🔄 Converting links for: {deal['title']}")
        deal["cb_offer_link"] = convert_to_affiliate_link(deal["raw_cb_link"]) if deal.get("raw_cb_link") else None
        deal["affiliate_buy_link"] = convert_to_affiliate_link(deal["raw_buy_link"])

        print(f"📤 Posting deal to Telegram...")
        success = send_deal_to_telegram(deal)
        
        if success:
            posted_deals.append(deal["id"])
            print(f"✅ Successfully posted and cached deal ID: {deal['id']}")
        else:
            print(f"❌ Failed to post deal ID: {deal['id']}")

    save_posted_deals(posted_deals)
    print("🏁 Dynamic pipeline execution finished.")

if __name__ == "__main__":
    run_pipeline()
