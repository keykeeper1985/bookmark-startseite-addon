# Bookmark Startseite (Home Assistant Add-on)

Eine kleine, responsive Bookmark-Startseite im Stil eines aufgeräumten Homepage-Dashboards. Die App läuft als Home-Assistant-Add-on und wird über Ingress geöffnet; es muss kein zusätzlicher Port im LAN freigegeben werden.

## Funktionen

- Bookmarks nach frei benennbaren Bereichen gruppieren
- Suche über Titel, URL und Bereich
- Bookmarks direkt in der Oberfläche hinzufügen, bearbeiten und löschen
- Persistenz unter `/config/bookmark-startseite/bookmarks.json`
- Responsive Darstellung, keine externen Schriftarten, Skripte oder Favicon-Dienste
- Ingress-Basispfad wird unterstützt

## Installation in Home Assistant

1. Den Ordner `bookmark-startseite` in den Add-on-Ordner deines Home-Assistant-Systems kopieren (typischerweise `/addons/bookmark-startseite`).
2. In **Einstellungen → Add-ons** den lokalen Add-on-Store neu laden.
3. **Bookmark Startseite** öffnen, installieren und starten.
4. **In der Seitenleiste anzeigen** aktivieren und **Bookmarks** öffnen.

Dieses Verzeichnis enthält die lokale Add-on-Quelle. Zum Installieren muss es auf den Home-Assistant-Host kopiert oder in ein Add-on-Repository aufgenommen werden; der aktuelle Zugriff auf HA-Entitäten erlaubt keine Dateiinstallation auf dem Host.

## Entwicklung / Tests

Der Server verwendet ausschließlich Python-Standardbibliothek. Lokal starten:

```sh
BOOKMARKS_FILE=./data/bookmarks.json PORT=8099 python3 app/server.py
```

Tests aus dem Projektordner:

```sh
python3 -m unittest discover -s tests -v
```
