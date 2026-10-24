import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def format_deal_message(deal):
    """
    Formats the message to match your required template.
    """
    title = deal.get("title")
    effective_price = deal.get("effective_price")
    cb_offer_text = deal.get("cb_offer_text")
    cb_offer_link = deal.get("cb_offer_link")
    buy_link = deal.get("affiliate_buy_link")
    discounts_text = deal.get("discounts_text") # e.g. "Apply Rs.390 Coupon + Rs.345 Cashback"

    message = f"**{title} at {effective_price}**\n\n"
    
    if cb_offer_link and cb_offer_text:
        message += f"Collect {cb_offer_text} : {cb_offer_link}\n\n"
        
    message += f"Then Buy : {buy_link}\n\n"
    
    if discounts_text:
        message += f"{discounts_text}"
        
    return message.strip()

def send_deal(deal):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("Missing Telegram credentials.")
        return False

    message_text = format_deal_message(deal)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    res = requests.post(url, json=payload)
    return res.json().get("ok", False)
