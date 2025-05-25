import requests
import time
import re
import json
import csv
from pathlib import Path

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

REGEX = config.get("regex", r"https://.*\.pdf$")
CHROME_REMOTE_URL = config.get("chrome_remote_url", "http://localhost:9222/json")
HISTORY_FILE = Path(config.get("history_file", "db.csv"))
UPLOAD_URL = config.get("upload_url", "http://127.0.0.1:5000/upload")

seen_urls = set()
if HISTORY_FILE.exists():
    with open(HISTORY_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                seen_urls.add(row[0])

def get_active_urls():
    try:
        tabs = requests.get(CHROME_REMOTE_URL).json()
        return [tab.get("url") for tab in tabs if tab.get("type") == "page"]
    except Exception as e:
        print(f"nelze načíst již otevřené: {e}")
        return []

def fetch_and_upload_pdf(url):
    try:
        r = requests.get(url)
        content_type = r.headers.get("Content-Type", "")
        if r.status_code == 200 and content_type.startswith("application/pdf"):
            filename = Path(url).name
            files = {'file': (filename, r.content, 'application/pdf')}
            resp = requests.post(UPLOAD_URL, files=files)

            if resp.status_code == 200:
                print(f"[OK] Úspěšně odesláno: {url}")
                with open(HISTORY_FILE, "a", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([url])
            else:
                print(f"[!] Selhalo odesílání PDF: {url} -> HTTP {resp.status_code}")
        else:
            print(f"[!] Nejedná se o PDF nebo špatný Content-Type: {url}")
    except Exception as e:
        print(f"[!] Chyba při zpracování PDF: {e}")

def main():
    print("Spuštěno...")
    while True:
        urls = get_active_urls()
        for url in urls:
            if url and re.match(REGEX, url) and url not in seen_urls:
                print(f"[MATCH] {url}")
                fetch_and_upload_pdf(url)
                seen_urls.add(url)
        time.sleep(2)

if __name__ == "__main__":
    main()
