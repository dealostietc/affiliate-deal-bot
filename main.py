import os
import json
import requests
import re
from urllib.parse import urlparse, urlunparse

def clean_merchant_url(url):
    """
    Strips tracking queries and cleans Amazon/Flipkart URLs 
    so Cuelinks generates valid, non-404 affiliate links.
    """
    if not url:
        return ""

    # Fix Amazon URLs to canonical /dp/ASIN
    if "amazon.in" in url or "amzn.in" in url:
        asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
        if asin_match:
            return f"https://www.amazon.in/dp/{asin_match.group(1)}"

    # Strip query strings (?tag=..., &ref=...) for other merchants to avoid double-encoding
    parsed = urlparse(url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return clean_url if clean_url else url

def convert_to_affiliate_link(original_url):
    """
    Converts cleaned merchant URLs into active Cuelinks short links.
    """
    if not original_url:
        return ""
    if not CUELINKS_API_KEY:
        print("❌ CUELINKS_API_KEY is missing!")
        return original_url

    # Clean destination URL first
    clean_url = clean_merchant_url(original_url)

    api_url = "https://developers.cuelinks.com/pub_api/v3/links/convert"
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"url": clean_url, "shorten": True}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        
        if response.status_code in [200, 201]:
            res_data = data.get("data", {})
            converted = (
                res_data.get("short_url") or 
                res_data.get("tracking_url") or 
                res_data.get("affiliate_url") or 
                clean_url
            )
            print(f"🔗 Cleaned Input: {clean_url} -> Converted: {converted}")
            return converted
        else:
            print(f"⚠️ Link conversion fallback status {response.status_code}: {data}")
            return clean_url
    except Exception as e:
        print(f"❌ Exception in conversion: {e}")
        return clean_url
