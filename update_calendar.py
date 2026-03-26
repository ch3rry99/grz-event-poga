import requests
from ics import Calendar
import re

# Konfiguration
SOURCE_URL = "https://www.postgarage.at/events.ics"
OUTPUT_FILE = "grz_postgarage.ical"

def process_calendar():
    # 1. Datei herunterladen
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    
    # 2. Kalender parsen
    calendar = Calendar(response.text)
    
    # 3. Bearbeitungs-Logik: Location-Korrektur
    for event in calendar.events:
        # Falls die Location Begriffe wie "1st", "2nd" etc. enthält
        if event.location and re.search(r'\d+(st|nd|rd|th)', event.location, re.IGNORECASE):
            event.location = "Postgarage"
        # Optional: Falls die Location komplett leer ist oder nur ein Komma enthält
        elif not event.location or event.location.strip() in [",", ""]:
            event.location = "Postgarage"

    # 4. Datei speichern
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    process_calendar()
