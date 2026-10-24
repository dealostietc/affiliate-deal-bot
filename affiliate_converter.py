import os
import requests

EARNKARO_API_KEY = os.getenv("EARNKARO_API_KEY")

def convert_to_affiliate_link(original_url):
    """
    Converts any store URL (Amazon, Flipkart, etc.) into your custom affiliate short link.
    Replace this block with your Cuelinks or EarnKaro API call.
    """
    if not EARNKARO_API_KEY:
        # Fallback / Direct tag append for Amazon if API is omitted
        if "amazon" in original_url:
            tag = os.getenv("AMAZON_AFFILIATE_TAG", "yourtag-21")
            return f"{original_url}?tag={tag}"
        return original_url

    api_url = "https://api.earnkaro.com/v1/convert" # Example API endpoint
    payload = {"url": original_url, "api_key": EARNKARO_API_KEY}
    
    try:
        response = requests.post(api_url, json=payload)
        data = response.json()
        return data.get("affiliate_url", original_url)
    except Exception as e:
        print(f"Error converting link: {e}")
        return original_url
