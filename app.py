import requests
import time
import re
import os
from pathlib import Path
from websocket import create_connection
import json

REGEX = r"https://.*\.pdf$"
OUTPUT_DIR = r"\\server\sdilena\slozka\doklady"
CHROME_REMOTE_URL = "http://localhost:9222/json"

def download_pdf(url):
    try:
        filename = Path(url).name
        dest_path = Path(OUTPUT_DIR) / filename
        if dest_path.exists():
            return
        r = requests.get(url)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/pdf"):
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"Staženo: {dest_path}")
        else:
            print(f"[!] URL nenačtena jako PDF: {url}")
    except Exception as e:
        print(f"[!] Chyba při stahování: {e}")

def main():
    print("Připojuji se na Chrome DevTools...")
    while True:
        try:
            tabs = requests.get(CHROME_REMOTE_URL).json()
            for tab in tabs:
                if tab.get("type") != "page":
                    continue
                ws_url = tab.get("webSocketDebuggerUrl")
                if not ws_url:
                    continue

                ws = create_connection(ws_url)
                ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
                ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
                ws.send(json.dumps({
                    "id": 3,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "window.location.href"}
                }))

                response = ws.recv()
                data = json.loads(response)

                url = data.get("result", {}).get("result", {}).get("value")
                if url and re.match(REGEX, url):
                    print(f"[MATCH] {url}")
                    download_pdf(url)

                ws.close()
            time.sleep(1)
        except Exception as e:
            print(f"[!] Chyba: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
