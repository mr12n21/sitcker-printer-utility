import requests
import time
import re
import json
from pathlib import Path

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

REGEX = config.get("regex", r"https://.*\.pdf$")
OUTPUT_DIR = Path(config.get("output_dir", r"\\server\sdilena\slozka\doklady"))
CHROME_REMOTE_URL = config.get("chrome_remote_url", "http://localhost:9222/json")

seen_urls = set()

def get_active_urls():
    try:
        tabs = requests.get(CHROME_REMOTE_URL).json()
        urls = [tab.get("url") for tab in tabs if tab.get("type") == "page"]
        return urls
    except Exception as e:
        print(f"[!] Nelze načíst záložky: {e}")
        return []

def download_pdf(url):
    try:
        filename = Path(url).name
        dest_path = OUTPUT_DIR / filename
        if dest_path.exists():
            return
        r = requests.get(url)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/pdf"):
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"[OK] Staženo: {dest_path}")
        else:
            print(f"[!] Nejedná se o PDF: {url}")
    except Exception as e:
        print(f"[!] Chyba při stahování: {e}")

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

if __name__ == "__main__":
    main()
