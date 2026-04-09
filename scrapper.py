import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


def load_seen_items():
    """Load previously seen item IDs to avoid duplicates."""
    if os.path.exists("seen_items.json"):
        with open("seen_items.json", "r") as f:
            return json.load(f)
    return []


def save_seen_items(items):
    """Save seen item IDs to avoid duplicates."""
    with open("seen_items.json", "w") as f:
        json.dump(items, f)


def get_listings(search_item, location, max_price=0, category_id=None):
    """
    Search Kleinanzeigen for items (defaults to free items if max_price=0).
    
    Args:
        search_item: Item to search for (e.g., "Fahrrad", "Bike")
        location: Location to search in (e.g., "Berlin")
        max_price: Maximum price (0 = free items only)
        category_id: Optional Kleinanzeigen category ID (e.g., 115 for "Fahrräder")
    
    Returns:
        List of new items not previously seen
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    
    # Build URL for Kleinanzeigen search
    # Format: https://www.kleinanzeigen.de/s-{item}/{location}/k{category_id}
    search_item_formatted = search_item.lower().replace(" ", "-")
    location_formatted = location.lower().replace(" ", "-")
    
    # Use category ID if provided, otherwise use k0 for all categories
    cat_id = category_id if category_id else "0"
    url = f"https://www.kleinanzeigen.de/s-{search_item_formatted}/{location_formatted}/k{cat_id}"
    
    # Add price filter for free items
    if max_price == 0:
        url += "?priceFrom=0&priceTo=0"
    elif max_price > 0:
        url += f"?priceFrom=0&priceTo={max_price}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []
    
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    
    # Kleinanzeigen uses '.adlistitem' as the main listing class
    for ad in soup.select("#srchrslt article, .adlistitem"):
        try:
            # Extract title
            title_elem = ad.select_one(".ellipsis")
            if not title_elem:
                continue
            title = title_elem.text.strip()
            
            # Extract link
            link_elem = ad.select_one("a[href*='/s-']")
            if not link_elem or not link_elem.get("href"):
                continue
            
            href = link_elem.get("href", "")
            if href.startswith("/"):
                link = "https://www.kleinanzeigen.de" + href
            else:
                link = href
            
            # Extract item ID for duplicate detection
            item_id = link.split("/")[-1]
            
            # Extract price if available
            price_elem = ad.select_one(".aditem-price")
            price = price_elem.text.strip() if price_elem else "Kostenlos"
            
            # Extract location if available
            location_elem = ad.select_one(".aditem-text--location")
            item_location = location_elem.text.strip() if location_elem else "N/A"
            
            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "location": item_location,
                "link": link,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error parsing ad: {e}")
            continue
    
    # Filter out already seen items
    seen = load_seen_items()
    new_items = []
    for item in items:
        if item["id"] not in seen:
            new_items.append(item)
            seen.append(item["id"])
    
    save_seen_items(seen)
    return new_items