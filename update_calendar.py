import requests
from ics import Calendar
import re
import html

# Konfiguration
SOURCE_URL = "https://www.postgarage.at/events.ics"
OUTPUT_FILE = "grz_postgarage.ical"

def clean_text(text):
    if not text:
        return ""
    
    # 1. HTML-Tags entfernen (z.B. <p>, <br>)
    # Wir ersetzen <br> und </p> zuerst durch echte Zeilenumbrüche
    text = re.sub(r'<(br|/p|/div)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. HTML-Entities umwandeln (z.B. &nbsp; zu Leerzeichen, &amp; zu &)
    text = html.unescape(text)
    
    # 3. "Wilde" Formatierung glätten
    # Mehrfache Leerzeichen durch eines ersetzen
    text = re.sub(r' [ ]+', ' ', text)
    # Mehr als zwei Zeilenumbrüche hintereinander auf zwei reduzieren
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def process_calendar():
    # 1. Datei herunterladen
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    
    # 2. Kalender parsen
    calendar = Calendar(response.text)
    
    # 3. Bearbeitungs-Logik
    for event in calendar.events:
        # Location-Korrektur (wie gehabt)
        if event.location and re.search(r'\d+(st|nd|rd|th)', event.location, re.IGNORECASE):
            event.location = "Postgarage"
        elif not event.location or event.location.strip() in [",", ""]:
            event.location = "Postgarage"

        # NEU: Description-Bereinigung
        if event.description:
            event.description = clean_text(event.description)
            
        # NEU: Auch den Titel (Summary) säubern, falls dort Entities landen
        if event.name:
            event.name = html.unescape(event.name).strip()

    # 4. Datei speichern
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    process_calendar()
