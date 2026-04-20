# Kleinanzeigen Benachrichtigungsbot 🤖

Ein Telegram-Bot, der automatisch nach kostenlosen Fahrrädern (oder anderen Artikeln) auf Kleinanzeigen in Berlin (oder einer anderen Stadt) sucht und dich benachrichtigt, wenn neue Angebote gefunden werden.

## Features 🚀

- 🔍 Automatische Suche auf Kleinanzeigen
- 🎯 Kategorie-Filter zur Vermeidung unerwünschter Ergebnisse (z.B. nur Fahrräder statt Fahrradzubehör)
- 💬 Telegram-Benachrichtigungen für neue Angebote
- 🎨 Formatierte Messages mit direkten Links
- ⚙️ Konfigurierbare Suchanfragen im laufenden Betrieb
- 🌍 Unterstützung für beliebige Orte
- 💰 Filter nach Preisbereich
- ⏱️ Anpassbares Suchintervall
- 🇩🇪 Vollständig auf Deutsch

## Installation 📦

### Voraussetzungen

- Python 3.8+
- Telegram Bot Token (von [@BotFather](https://t.me/botfather))
- Deine Telegram Chat ID

### Setup

1. **Repository klonen/erstellen:**
   ```bash
   cd /path/to/Kavile
   ```

2. **Virtual Environment erstellen:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder
   venv\Scripts\activate  # Windows
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **.env-Datei erstellen:**
   ```bash
   cp .env.example .env
   ```

5. **.env-Datei ausfüllen:**
   ```env
   TELEGRAM_BOT_TOKEN=dein_bot_token_hier
   TELEGRAM_CHAT_ID=deine_chat_id_hier
   SEARCH_ITEM=Fahrrad
   SEARCH_LOCATION=Berlin
   SEARCH_PRICE_MAX=0
   CATEGORY_ID=115
   SEARCH_INTERVAL=300
   ```

   **Wichtige Kategorien:**
   - `115` - Fahrräder (Standard)
   - `0` - Alle Kategorien
   - `3` - Elektronik
   - `4` - Möbel
   - `8` - Auto

### Telegram Bot erstellen

1. Öffne [@BotFather](https://t.me/botfather) in Telegram
2. Sende `/newbot`
3. Folge den Anweisungen und erhalte deinen Bot Token
4. Starte eine Konversation mit deinem neuen Bot
5. Besuche `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe` um deine Chat ID zu erhalten

## Verwendung 🎯

### Bot starten:

```bash
python main.py
```

Der Bot wird dann:
- Automatisch nach neuen Angeboten suchen (StandardMäßig alle 5 Minuten)
- Dir Benachrichtigungen senden, wenn neue Angebote gefunden werden
- Auf deine Befehle warten

### Befehle 📋

Sende diese Befehle an deinen Bot:

| Befehl | Beschreibung | Beispiel |
|--------|-------------|---------|
| `/start` | Zeigt eine Willkommensnachricht | `/start` |
| `/item <name>` | Ändert den Suchbegriff | `/item PS5` |
| `/location <ort>` | Ändert den Suchort | `/location München` |
| `/price <preis>` | Setzt maximalen Preis (0 = kostenlos) | `/price 100` |
| `/category <id>` | Ändert die Kategorie (115 = Fahrräder, 0 = alle) | `/category 115` |
| `/interval <sekunden>` | Ändert das Suchintervall | `/interval 600` |
| `/status` | Zeigt aktuelle Einstellungen | `/status` |
| `/help` | Zeigt Hilfeinformationen | `/help` |

### Beispiele 💡

**Kostenlose iPhones in Berlin suchen (ohne Kategorie-Filter):**
```
/item iPhone
/location Berlin
/price 0
/category 0
/interval 300
```

**Nur kostenlose Fahrräder in München (mit Kategorie-Filter):**
```
/item Fahrrad
/location München
/price 0
/category 115
```

**Tische unter 50€ in Hamburg:**
```
/item Tisch
/location Hamburg
/price 50
/category 0
```

## Konfiguration ⚙️

### Umgebungsvariablen (.env)

- `TELEGRAM_BOT_TOKEN`: Dein Telegram Bot Token (erforderlich)
- `TELEGRAM_CHAT_ID`: Deine Telegram Chat ID (erforderlich)
- `SEARCH_ITEM`: Standard-Suchbegriff (Standard: "Fahrrad")
- `SEARCH_LOCATION`: Standard-Suchort (Standard: "Berlin")
- `SEARCH_PRICE_MAX`: Maximaler Preis (0 = kostenlos, Standard: "0")
- `CATEGORY_ID`: Kategorie-ID (115 = Fahrräder, 0 = alle Kategorien, Standard: "115")
- `SEARCH_URL`: Optionaler kompletter Kleinanzeigen-Suchlink (überschreibt die dynamische Suche)
- `SEARCH_INTERVAL`: Suchintervall in Sekunden (Standard: "300")

## Dateistruktur 📁

```
.
├── main.py              # Haupt-Bot Logik
├── scrapper.py          # Kleinanzeigen Scraper
├── requirements.txt     # Python Abhängigkeiten
├── .env.example        # Beispiel Umgebungskonfiguration
├── .env                # Aktuelle Umgebungskonfiguration (NICHT committen!)
├── .gitignore          # Git ignore Regeln
├── bot_config.json     # Bot Konfiguration (wird automatisch erstellt)
├── seen_items.json     # Liste gesehener Items (wird automatisch erstellt)
└── LICENSE             # MIT Lizenz
```

## Wichtige Hinweise ⚠️

- **Behalte dein Bot Token privat!** Füge ihn NICHT ins Git-Repository ein
- Die `.env`-Datei ist im `.gitignore` eingetragen
- **Kategorie-Filter verwenden:** Um unerwünschte Ergebnisse zu vermeiden, nutze Kategorie-IDs (z.B. `115` für nur Fahrräder statt Fahrradzubehör)
- Der Bot werden gesehene Angebote nicht zweimal anzeigen
- Setze das Suchintervall nicht zu kurz (mindestens 30 Sekunden), um Kleinanzeigen nicht zu überlasten

## Fehlerbehandlung 🐛

- Der Bot läuft kontinuierlich und versucht, Fehler automatisch zu behandeln
- Bei fehlender Netzwerkverbindung werden Anfragen wiederholt
- Alle Fehler werden in die Konsole geloggt

## Lizenz 📄

MIT License - siehe [LICENSE](LICENSE) für Details
