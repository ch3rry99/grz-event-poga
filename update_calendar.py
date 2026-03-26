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
    
    # 1. HTML-Tags intelligent ersetzen
    # Block-Elemente durch Zeilenumbrüche ersetzen, damit Text nicht zusammenklebt
    text = re.sub(r'<(br|p|div|li|tr|h[1-6])[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Alle restlichen Tags entfernen
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. HTML-Entities umwandeln (&nbsp;, &amp;, etc.)
    text = html.unescape(text)
    
    # 3. Fehlende Leerzeichen nach Satzzeichen korrigieren
    # Wenn ein Satzzeichen direkt von einem Großbuchstaben gefolgt wird (z.B. Graz!L.A.)
    text = re.sub(r'([!.?])([A-Z])', r'\1 \2', text)
    
    # 4. "Wüste" aus Leerzeilen und Leerzeichen säubern
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped: # Nur Zeilen behalten, die Inhalt haben
            # Mehrfache Leerzeichen innerhalb der Zeile reduzieren
            cleaned_lines.append(re.sub(r'\s+', ' ', stripped))
    
    # 5. Text wieder zusammenfügen (mit max. einem Leerzeichen zwischen Absätzen)
    text = '\n'.join(cleaned_lines)
    
    # 6. Letzter Schliff: Doppelte Zeilenumbrüche begrenzen
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def process_calendar():
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    
    # Wichtig: Dekodierung explizit auf UTF-8 setzen
    calendar = Calendar(response.text)
    
    for event in calendar.events:
        # Location-Korrektur
        if event.location and re.search(r'\d+(st|nd|rd|th)', event.location, re.IGNORECASE):
            event.location = "Postgarage"
        elif not event.location or event.location.strip() in [",", ""]:
            event.location = "Postgarage"

        # Description-Bereinigung mit der neuen Logik
        if event.description:
            event.description = clean_text(event.description)
            
        if event.name:
            event.name = html.unescape(event.name).strip()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Wir schreiben den Kalender-Inhalt direkt
        f.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    process_calendar()
