# Bookmark Startseite Add-on Repository

Eine private Bookmark-Startseite für Home Assistant, inspiriert von gethomepage.dev. Das Add-on läuft über Ingress und benötigt keinen zusätzlichen LAN-Port.

## Home Assistant Installation

1. **Einstellungen → Add-ons → Add-on-Store** öffnen.
2. Im Menü **⋮ → Repositories** diese URL hinzufügen:
   `https://github.com/keykeeper1985/bookmark-startseite-addon`
3. Repository aktualisieren, **Bookmark Startseite** installieren und starten.
4. In der Add-on-Konfiguration **In der Seitenleiste anzeigen** aktivieren.

Bookmarks werden unter `/config/bookmark-startseite/bookmarks.json` dauerhaft gespeichert. Die Weboberfläche unterstützt Kategorien, Suche, Hinzufügen, Bearbeiten und Löschen.

Das Add-on-Verzeichnis liegt in `bookmark-startseite/`.
