import os
import time
import requests
import json
from dotenv import load_dotenv
from scrapper import get_listings

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEARCH_ITEM = os.getenv("SEARCH_ITEM", "Fahrrad")
SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "Berlin")
SEARCH_PRICE_MAX = int(os.getenv("SEARCH_PRICE_MAX", "0"))
CATEGORY_ID = int(os.getenv("CATEGORY_ID", "115"))  # 115 = Fahrräder
SEARCH_INTERVAL = int(os.getenv("SEARCH_INTERVAL", "300"))

# Config file to store user settings
CONFIG_FILE = "bot_config.json"


def load_config():
    """Load bot configuration from file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "search_item": SEARCH_ITEM,
        "search_location": SEARCH_LOCATION,
        "max_price": SEARCH_PRICE_MAX,
        "category_id": CATEGORY_ID,
        "search_interval": SEARCH_INTERVAL,
    }


def save_config(config):
    """Save bot configuration to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def send_message(text):
    """Send a message via Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")


def send_listing(item):
    """Send a listing notification via Telegram."""
    message = f"🚲 *{item['title']}*\n\n"
    message += f"💰 {item['price']}\n"
    message += f"📍 {item['location']}\n"
    message += f"🔗 [Angebot anschauen]({item['link']})"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
    except Exception as e:
        print(f"Error sending listing: {e}")


def get_category_name(category_id):
    """Get human-readable category name from category ID."""
    categories = {
        0: "Alle Kategorien",
        115: "Fahrräder",
        1: "Mode",
        2: "Heimwerken",
        3: "Elektronik",
        4: "Möbel",
        5: "Spielzeug",
        6: "Sport & Freizeit",
        7: "Bücher",
        8: "Auto",
    }
    return categories.get(category_id, f"Kategorie {category_id}")


def get_updates(offset=0):
    """Get updates from Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"offset": offset}, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return {"result": []}


def handle_update(update):
    """Handle incoming Telegram updates/commands."""
    if "message" not in update:
        return

    message = update["message"]
    text = message.get("text", "").lower()
    
    if text.startswith("/start"):
        send_message(
            "🤖 *Kleinanzeigen Benachrichtigungsbot*\n\n"
            "Verfügbare Befehle:\n"
            "/item <name> - Suchbegriff ändern\n"
            "/location <ort> - Suchort ändern\n"
            "/price <preis> - Maximalprice setzen (0 = kostenlos)\n"
            "/category <id> - Kategorien-ID setzen (115 = Fahrräder)\n"
            "/interval <sekunden> - Suchinterval setzen\n"
            "/status - Aktuelle Einstellungen anzeigen\n"
            "/help - Diese Hilfe anzeigen"
        )
    
    elif text.startswith("/item "):
        item = text.replace("/item ", "").strip()
        if item:
            config = load_config()
            config["search_item"] = item
            save_config(config)
            send_message(f"✅ Suchbegriff geändert zu: *{item}*")
        else:
            send_message("❌ Bitte geben Sie einen Suchbegriff an: /item <name>")
    
    elif text.startswith("/location "):
        location = text.replace("/location ", "").strip()
        if location:
            config = load_config()
            config["search_location"] = location
            save_config(config)
            send_message(f"✅ Suchort geändert zu: *{location}*")
        else:
            send_message("❌ Bitte geben Sie einen Ort an: /location <ort>")
    
    elif text.startswith("/price "):
        try:
            price = int(text.replace("/price ", "").strip())
            config = load_config()
            config["max_price"] = price
            save_config(config)
            price_text = "kostenlos" if price == 0 else f"€{price}"
            send_message(f"✅ Maximalprice geändert zu: *{price_text}*")
        except ValueError:
            send_message("❌ Bitte geben Sie einen gültigen Preis an: /price <zahl>")
    
    elif text.startswith("/category "):
        try:
            category_id = int(text.replace("/category ", "").strip())
            config = load_config()
            config["category_id"] = category_id
            save_config(config)
            category_name = get_category_name(category_id)
            send_message(f"✅ Kategorie geändert zu: *{category_name}* (ID: {category_id})")
        except ValueError:
            send_message("❌ Bitte geben Sie eine gültige Kategorien-ID an: /category <id>")
    
    elif text.startswith("/interval "):
        try:
            interval = int(text.replace("/interval ", "").strip())
            if interval < 30:
                send_message("❌ Interval muss mindestens 30 Sekunden sein")
            else:
                config = load_config()
                config["search_interval"] = interval
                save_config(config)
                send_message(f"✅ Suchinterval geändert zu: *{interval} Sekunden*")
        except ValueError:
            send_message("❌ Bitte geben Sie eine gültige Zeit an: /interval <sekunden>")
    
    elif text.startswith("/status"):
        config = load_config()
        category_name = get_category_name(config.get("category_id", 115))
        status = (
            f"📊 *Aktuelle Einstellungen:*\n\n"
            f"🔍 Suchbegriff: `{config['search_item']}`\n"
            f"📍 Suchort: `{config['search_location']}`\n"
            f"💰 Maximalpreis: `€{config['max_price']}` ("
            f"{'kostenlos' if config['max_price'] == 0 else 'begrenzt'})\n"
            f"🏷️ Kategorie: `{category_name}`\n"
            f"⏱️ Suchinterval: `{config['search_interval']} Sekunden`"
        )
        send_message(status)
    
    elif text.startswith("/help"):
        send_message(
            "🤖 *Kleinanzeigen Benachrichtigungsbot*\n\n"
            "Verfügbare Befehle:\n"
            "`/item <name>` - Suchbegriff ändern\n"
            "`/location <ort>` - Suchort ändern (z.B.: Berlin, München)\n"
            "`/price <preis>` - Maximalprice setzen (0 = nur kostenlose)\n"
            "`/category <id>` - Kategorien-ID setzen (115 = Fahrräder, 0 = alle)\n"
            "`/interval <sekunden>` - Suchinterval ändern (min. 30s)\n"
            "`/status` - Zeigt aktuelle Einstellungen\n"
            "`/help` - Diese Hilfe anzeigen\n\n"
            "Der Bot sucht automatisch nach neuen Angeboten und sendet dir Benachrichtigungen!"
        )


def check_listings(config):
    """Check for new listings and send notifications."""
    try:
        new_items = get_listings(
            config["search_item"],
            config["search_location"],
            config["max_price"],
            config.get("category_id", 115),
        )
        for item in new_items:
            send_listing(item)
            print(f"✅ Sent notification: {item['title']}")
    except Exception as e:
        print(f"Error checking listings: {e}")


def main():
    """Main bot loop."""
    print("🤖 Kleinanzeigen Bot gestartet...")
    send_message("🤖 Kleinanzeigen Bot ist nun aktiv!")
    
    offset = 0
    last_search = 0
    
    while True:
        # Handle incoming commands
        try:
            result = get_updates(offset)
            if result.get("ok"):
                for update in result.get("result", []):
                    handle_update(update)
                    offset = update["update_id"] + 1
        except Exception as e:
            print(f"Error handling updates: {e}")
        
        # Check for new listings periodically
        config = load_config()
        current_time = time.time()
        if current_time - last_search >= config["search_interval"]:
            check_listings(config)
            last_search = current_time
        
        time.sleep(1)


if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("❌ Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env file")
        exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
        send_message("🛑 Bot wurde gestoppt")