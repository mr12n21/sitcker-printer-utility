import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_FOLDER = r"C:\Users\petr\Downloads"
UPLOAD_URL = "http://192.168.0.25:5000/upload"
EXPECTED_FILENAME = "Účet pokoje.xlsx"

class XLSHandler(FileSystemEventHandler):
    def process_file(self, path):
        filename = os.path.basename(path)
        if filename.lower() == EXPECTED_FILENAME.lower():
            print(f"Nový cílový soubor: {path}")
            time.sleep(1)  # počkej, až se dokončí zápis

            try:
                with open(path, 'rb') as f:
                    files = {"file": (filename, f)}
                    response = requests.post(UPLOAD_URL, files=files)
                    if response.ok:
                        print("Soubor úspěšně odeslán")
                    else:
                        print(f"Chyba při odesílání: {response.status_code} {response.text}")
            except Exception as e:
                print(f"Chyba při čtení/odesílání: {e}")
            finally:
                try:
                    os.remove(path)
                    print(f"Soubor smazán: {path}")
                except Exception as e:
                    print(f"Nepodařilo se smazat soubor: {e}")
        else:
            print(f"Ignorován soubor: {filename}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_file(event.dest_path)

if __name__ == "__main__":
    observer = Observer()
    event_handler = XLSHandler()
    observer.schedule(event_handler, path=WATCHED_FOLDER, recursive=False)
    observer.start()
    print(f"Sledování složky: {WATCHED_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
