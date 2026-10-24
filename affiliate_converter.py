import os
import requests

CUELINKS_API_KEY = os.getenv("CUELINKS_API_KEY")

def convert_to_affiliate_link(original_url):
    """
    Converts any store URL (Amazon, Flipkart, Myntra, etc.) 
    into your tracked Cuelinks affiliate link.
    """
    if not original_url:
        return ""

    if not CUELINKS_API_KEY:
        print("Warning: CUELINKS_API_KEY is missing. Returning raw URL.")
        return original_url

    # Cuelinks Link Conversion Endpoint
    api_url = "https://www.cuelinks.com/api/v2/links.json"
    
    headers = {
        "Authorization": f"Token token={CUELINKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": original_url,
        "shorten": "true" # Optional: returns a shortened clnk.in link if desired
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Cuelinks returns the affiliate URL under 'url' or 'short_url'
            return data.get("url", original_url)
        else:
            print(f"Cuelinks API error ({response.status_code}): {response.text}")
            return original_url
    except Exception as e:
        print(f"Error connecting to Cuelinks API: {e}")
        return original_url
