import os
import requests

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def convert_to_affiliate_link(original_url):
    """
    Converts any product URL into a Cuelinks short link using V3 API.
    """
    if not original_url:
        return ""

    if not CUELINKS_API_KEY:
        print("Warning: CUELINKS_API_KEY is missing. Returning raw URL.")
        return original_url

    # Updated Cuelinks V3 Endpoint
    api_url = "https://developers.cuelinks.com/pub_api/v3/links/convert"
    
    headers = {
        "Authorization": f"Token {CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": original_url
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Returns the shortened clnk.in tracking URL
            return data.get("short_url") or data.get("affiliate_url", original_url)
        else:
            print(f"Cuelinks API error ({response.status_code}): {response.text}")
            return original_url
    except Exception as e:
        print(f"Error connecting to Cuelinks API: {e}")
        return original_url
