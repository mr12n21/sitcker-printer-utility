import requests
import time
import re
import json
import csv
from pathlib import Path

# Načtení konfigurace
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

REGEX = config.get("regex", r"https://pms.previo.app.*")
OUTPUT_DIR = Path(config.get("output_dir", r"./"))
CHROME_REMOTE_URL = config.get("chrome_remote_url", "http://localhost:9222/json")
HISTORY_FILE = Path(config.get("history_file", "db.csv"))

# Načtení historie již stažených URL
seen_urls = set()
if HISTORY_FILE.exists():
    with open(HISTORY_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                seen_urls.add(row[0])

# Získání URL z otevřených karet Chrome
def get_active_urls():
    try:
        tabs = requests.get(CHROME_REMOTE_URL).json()
        return [tab.get("url") for tab in tabs if tab.get("type") == "page"]
    except Exception as e:
        print(f"nelze načíst již otevřené: {e}")
        return []

# Stažení a uložení obsahu z URL jako PDF
def download_pdf(url):
    try:
        filename = Path(url).name
        # Přidej .pdf, i když tam není
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        dest_path = OUTPUT_DIR / filename

        if dest_path.exists():
            return

        r = requests.get(url)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"[OK] Uloženo: {dest_path}")

            # Zapiš URL do historie
            with open(HISTORY_FILE, "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([url])
        else:
            print(f"[!] Chyba při stahování {url} – Status code: {r.status_code}")
    except Exception as e:
        print(f"[!] Chyba při stahování: {e}")


# Hlavní smyčka
def main():
    print("Spuštěno...")
    while True:
        urls = get_active_urls()
        for url in urls:
            if url and re.match(REGEX, url) and url not in seen_urls:
                print(f"[MATCH] {url}")
                download_pdf(url)
                seen_urls.add(url)
        time.sleep(2)

# Spuštění programu
if __name__ == "__main__":
    main()
