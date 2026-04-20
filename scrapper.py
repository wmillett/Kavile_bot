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


def get_listings(search_item, location, max_price=0, category_id=None, search_url=None):
    """
    Search Kleinanzeigen for items (defaults to free items if max_price=0).
    
    Args:
        search_item: Item to search for (e.g., "Fahrrad", "Bike")
        location: Location to search in (e.g., "Berlin")
        max_price: Maximum price (0 = free items only)
        category_id: Optional Kleinanzeigen category ID (e.g., 115 for "Fahrräder")
        search_url: Optional full Kleinanzeigen search URL override
    
    Returns:
        List of new items not previously seen
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9",
    }
    
    def slugify(text):
        replacements = {
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "Ä": "ae",
            "Ö": "oe",
            "Ü": "ue",
            "ß": "ss",
        }
        text = text.strip()
        for src, dst in replacements.items():
            text = text.replace(src, dst)
        return "-".join(text.lower().split())

    # Use a full custom search URL if provided; otherwise build the standard Kleinanzeigen query.
    if search_url:
        url = search_url
    else:
        search_item_formatted = slugify(search_item)
        location_formatted = slugify(location)

        cat_id = category_id if category_id else "0"
        url = f"https://www.kleinanzeigen.de/s-{search_item_formatted}/{location_formatted}/anzeige:angebote"

        if max_price == 0:
            url += "/preis:0:0"
        elif max_price > 0:
            url += f"/preis:0:{max_price}"

        if cat_id != "0":
            url += f"/c{cat_id}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []
    
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    
    # Kleinanzeigen uses article.aditem elements for search results.
    for ad in soup.select("#srchrslt article.aditem, article.aditem"):
        try:
            # Extract title and link from the ad header
            title_elem = ad.select_one("h2 a.ellipsis") or ad.select_one("a.ellipsis")
            if not title_elem:
                continue
            title = title_elem.text.strip()

            # Extract link
            link_elem = title_elem if title_elem.name == "a" else ad.select_one("a[href*='/s-anzeige/']")
            if not link_elem or not link_elem.get("href"):
                continue

            href = link_elem.get("href", "")
            if href.startswith("/"):
                link = "https://www.kleinanzeigen.de" + href
            else:
                link = href

            # Extract item ID for duplicate detection
            item_id = ad.get("data-adid") or link.rstrip("/").split("/")[-1].split("-")[0]
            if not item_id:
                continue

            # Extract price if available
            price_elem = ad.select_one(".aditem-main--middle--price-shipping--price")
            price = price_elem.text.strip() if price_elem else "Kostenlos"

            # Extract location if available
            location_elem = ad.select_one(".aditem-main--top--left")
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