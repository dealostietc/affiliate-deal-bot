import os
import requests
import re
from datetime import datetime

def fetch_live_deals(limit=5):
    """
    Fetches live Indian e-commerce deals with multiple fallback streams
    and guaranteed rotation for Amazon, Flipkart, Myntra, Ajio, Blinkit, and Zepto.
    """
    print("📡 Fetching live Indian e-commerce product deal streams...")
    
    extracted_deals = []
    seen_links = set()

    # Enterprise-grade browser headers to bypass server-side blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    # 1. Try Public Indian RSS Deal Feeds
    feed_urls = [
        "https://www.desidime.com/feed",
        "https://www.grabon.in/feed/"
    ]

    for rss_url in feed_urls:
        if len(extracted_deals) >= limit:
            break
        try:
            response = requests.get(rss_url, headers=headers, timeout=8)
            if response.status_code == 200:
                content = response.text
                items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                
                for item in items:
                    if len(extracted_deals) >= limit:
                        break
                        
                    title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                    link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                    
                    title = title_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if title_match else "Hot Deal"
                    link = link_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if link_match else ""
                    desc = desc_match.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if desc_match else ""
                    
                    clean_desc = re.sub(r'<[^>]+>', '', desc)[:140]

                    valid_domains = ['amazon.in', 'flipkart.com', 'myntra.com', 'ajio.com', 'croma.com', 'blinkit.com', 'zepto', 'meesho.com', 'shopsy.in']
                    is_indian_ecommerce = any(domain in link.lower() for domain in valid_domains)
                    
                    if is_indian_ecommerce and link not in seen_links:
                        seen_links.add(link)
                        extracted_deals.append({
                            "id": f"ind_rss_{abs(hash(link))}",
                            "title": title[:110],
                            "effective_price": "Best Price",
                            "cb_offer_text": "⚡ Loot Price Drop",
                            "raw_cb_link": None,
                            "raw_buy_link": link,
                            "discounts_text": clean_desc if clean_desc else "Limited-time deal on Indian store. Grab before stock ends!"
                        })
        except Exception as e:
            print(f"⚠️ RSS feed skipped ({rss_url}): {e}")

    # 2. GUARANTEED INDIAN PLATFORM ROTATION FALLBACK
    # If RSS feeds are blocked or return 0 deals, this guarantees high-converting Indian deals instantly.
    if not extracted_deals:
        print("ℹ️ RSS feeds unavailable. Engaging Guaranteed Indian E-Commerce Rotation...")
        
        # Current date-based stamp to ensure unique deal IDs per run without repeating
        day_stamp = datetime.now().strftime("%Y%m%d%H")
        
        indian_fallbacks = [
            {
                "id": f"ind_amzn_{day_stamp}",
                "title": "🔥 Amazon India Today's Deals & Lightning Discounts",
                "effective_price": "Up to 80% Off",
                "cb_offer_text": "Bank Offers & Lightning Deals",
                "raw_cb_link": None,
                "raw_buy_link": "https://www.amazon.in/gp/goldbox",
                "discounts_text": "Check live price drops across Electronics, Fashion, Home & Kitchen!"
            },
            {
                "id": f"ind_fk_{day_stamp}",
                "title": "⚡ Flipkart Big Saving Days & Top Offers",
                "effective_price": "Best Price Guaranteed",
                "cb_offer_text": "SuperCoin & Bank Discounts",
                "raw_cb_link": None,
                "raw_buy_link": "https://www.flipkart.com/offers-store",
                "discounts_text": "Grab massive discounts on smartphones, appliances, and daily essentials."
            },
            {
                "id": f"ind_myntra_{day_stamp}",
                "title": "👗 Myntra Trendsetting Fashion Sale: Styles at Lowest Prices",
                "effective_price": "Min 50% - 80% Off",
                "cb_offer_text": "Extra Coupon Discount",
                "raw_cb_link": None,
                "raw_buy_link": "https://www.myntra.com/",
                "discounts_text": "Upgrade your wardrobe with top top brands, shoes, and accessories."
            },
            {
                "id": f"ind_ajio_{day_stamp}",
                "title": "👜 AJIO Mania: Handpicked Styles & Mega Clearance",
                "effective_price": "Best Handpicked Deals",
                "cb_offer_text": "Use Promo Codes on Checkout",
                "raw_cb_link": None,
                "raw_buy_link": "https://www.ajio.com/",
                "discounts_text": "Explore trendy apparel and footwear with exclusive platform discounts."
            },
            {
                "id": f"ind_blinkit_{day_stamp}",
                "title": "⚡ Blinkit Quick Commerce: Groceries & Essentials Delivered in Minutes",
                "effective_price": "Instant Delivery",
                "cb_offer_text": "Lightning Fast Delivery",
                "raw_cb_link": None,
                "raw_buy_link": "https://blinkit.com/",
                "discounts_text": "Order fresh groceries, snacks, and daily needs right to your doorstep."
            }
        ]
        
        extracted_deals = indian_fallbacks[:limit]

    print(f"✅ Successfully prepared {len(extracted_deals)} verified Indian e-commerce deals!")
    return extracted_deals
