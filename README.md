# sitcker-printer-utility
utility for sticker printer to minimize user activity



🔁 Upravený app.py s HTTP POST odesláním PDF

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
UPLOAD_URL = config.get("upload_url", "http://192.168.1.127:5000/upload")

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

🔧 Upravený config.json

Přidej klíč upload_url:

{
  "regex": "https://.*\\.pdf$",
  "chrome_remote_url": "http://localhost:9222/json",
  "upload_url": "http://192.168.1.127:5000/upload",
  "history_file": "db.csv"
}

✅ Jak to spustit
🐧 Linux:

    Aktivuj virtuální prostředí (pokud máš):

source venv/bin/activate

Spusť skript:

    python3 app.py

    Volitelně: přidej do cronu nebo systemd service, pokud chceš spouštět při startu systému.

🪟 Windows:

    Aktivuj virtuální prostředí:

.\venv\Scripts\activate

Spusť skript:

    python app.py

    Volitelně: můžeš použít Naplánované úlohy (Task Scheduler) pro automatické spouštění skriptu při startu systému.

✅ Jak vypadá POST požadavek (Postman schema)

    URL: http://192.168.1.127:5000/upload

    Method: POST

    Body → form-data:

        Key: file

        Type: File

        Value: *.pdf

🔍 Ověření výsledku v kódu

Ověřujeme, že resp.status_code == 200. Můžeš si to v případě potřeby rozšířit o např.:

if resp.status_code == 200 and "success" in resp.text:

Chceš k tomu i jednoduchý Flask server, který by ten /upload endpoint přijal a PDF někam ukládal?
You said:
a jak mam spustit ten browser aby se na nej python pripojil
ChatGPT said:

Skvělé, ptáš se správně. Aby Python skript (app.py) mohl získávat otevřené URL z prohlížeče, musí být spuštěný Chrome nebo Chromium s povoleným Remote Debugging módem.
🧠 Co to znamená?

Python skript přistupuje na http://localhost:9222/json a získává informace o otevřených panelech pomocí Chrome DevTools Protocol. To je možné pouze tehdy, pokud Chrome/Chromium běží s tímto parametrem:

--remote-debugging-port=9222

🐧 Linux – jak spustit Chrome/Chromium s tímto parametrem:
1. Chromium:

chromium --remote-debugging-port=9222

2. Google Chrome:

google-chrome --remote-debugging-port=9222

🪟 Windows – jak spustit Chrome s tímto parametrem:
1. Otevři CMD nebo PowerShell
2. Spusť Chrome takto:

start chrome --remote-debugging-port=9222

    Pokud to nefunguje, zkus plnou cestu:

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

🧪 Jak ověřit, že to funguje?

Otevři prohlížeč a zadej:

http://localhost:9222/json

Měl bys vidět JSON s informacemi o otevřených tabech (např. URL, titulky, atd.).
✅ Poznámky

    Můžeš otevřít více URL ručně v prohlížeči a Python skript je najde, pokud budou odpovídat regexu.

    Port 9222 můžeš změnit v config.json i v parametru --remote-debugging-port.

🧠 Tip pro pohodlí (Linux)

Pokud chceš spouštět Chromium s tímto parametrem častěji, vytvoř si alias:

alias debug-chromium="chromium --remote-debugging-port=9222"

Chceš i skript nebo .desktop soubor pro snadné spouštění prohlížeče s tímto parametrem?
You said:
jake reqirimens musim poslat
ChatGPT said:

Abys mohl úspěšně odesílat PDF přes HTTP request z tvého Python skriptu na server (např. na http://192.168.1.127:5000/upload), musíš:
✅ 1. Mít server, který přijímá POST /upload (např. Flask aplikaci):

from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename.endswith('.pdf'):
        filepath = f"./received/{file.filename}"
        file.save(filepath)
        return {'status': 'ok', 'filename': file.filename}, 200
    return {'status': 'error', 'message': 'Invalid file'}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    Tato aplikace vytvoří endpoint /upload na portu 5000.

✅ 2. Upravit tvůj Python skript tak, aby místo stahování PDF odesílal soubor přes POST:

def send_pdf(url, destination):
    try:
        r = requests.get(url)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/pdf"):
            files = {'file': (Path(url).name, r.content, 'application/pdf')}
            response = requests.post(destination, files=files)
            if response.status_code == 200:
                print(f"[UPLOAD OK] {url} -> {destination}")
                with open(HISTORY_FILE, "a", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([url])
            else:
                print(f"[UPLOAD FAIL] {url} -> {destination} (status {response.status_code})")
        else:
            print(f"[!] Nejedná se o PDF: {url}")
    except Exception as e:
        print(f"[!] Chyba při odesílání: {e}")

A pak v main() volat:

send_pdf(url, "http://192.168.1.127:5000/upload")

✅ 3. Co musí být v requestu (jak to vypadá jako v Postmanu)?

POST /upload HTTP/1.1
Host: 192.168.1.127:5000
Content-Type: multipart/form-data; boundary=...
Content-Length: ...

----WebKitFormBoundary...
Content-Disposition: form-data; name="file"; filename="example.pdf"
Content-Type: application/pdf

... (PDF file binary content) ...
----WebKitFormBoundary...

✅ 4. Instalace potřebných Python knihoven (requirements):

Pokud používáš requests, vytvoř requirements.txt:

requests

Pokud běžíš i Flask server:

Flask

Pak nainstaluj:

pip install -r requirements.txt

Chceš, abych ti upravil celý tvůj skript app.py, aby místo stahování odesílal PDF pomocí POST requestu?
You said:
marek@fedora:~/Documents/GitHub/sitcker-printer-utility$ pip install request
Defaulting to user installation because normal site-packages is not writeable
ERROR: Could not find a version that satisfies the requirement request (from versions: none)
ERROR: No matching distribution found for request
marek@fedora:~/Documents/GitHub/sitcker-printer-utility$ 
ChatGPT said:

Chyba je v tom, že jsi napsal špatně název knihovny. Správný název je:

requests

Ne request (bez „s“).
✅ Oprava:

Spusť:

pip install requests

📌 Poznámka:

    requests je jedna z nejpoužívanějších knihoven v Pythonu pro HTTP komunikaci (GET, POST atd.).

    Pokud používáš virtual environment (např. venv), doporučuji jej aktivovat před instalací:

source venv/bin/activate
pip install requests

Chceš, abych ti připravil celý přepsaný app.py, který místo stahování bude odesílat PDF jako HTTP POST?