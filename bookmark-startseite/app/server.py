#!/usr/bin/env python3
"""Small ingress-aware HTTP server for the Bookmark Startseite add-on."""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "static" / "index.html"
DATA_FILE = Path(os.environ.get("BOOKMARKS_FILE", "./data/bookmarks.json"))
PORT = int(os.environ.get("PORT", "8099"))
DATA_LOCK = threading.Lock()
MAX_BODY = 1_000_000


def read_bookmarks() -> list[dict[str, str]]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Bookmark-Datei muss eine Liste enthalten")
    return data


def validate_bookmarks(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("bookmarks muss eine Liste sein")
    if len(value) > 500:
        raise ValueError("Maximal 500 Bookmarks sind erlaubt")

    result: list[dict[str, str]] = []
    ids: set[str] = set()
    for entry in value:
        if not isinstance(entry, dict):
            raise ValueError("Jeder Bookmark muss ein Objekt sein")
        fields = {key: str(entry.get(key, "")).strip() for key in ("id", "title", "url", "category")}
        if not all(fields.values()):
            raise ValueError("id, title, url und category dürfen nicht leer sein")
        if len(fields["id"]) > 100 or len(fields["title"]) > 120 or len(fields["url"]) > 2048 or len(fields["category"]) > 80:
            raise ValueError("Ein Bookmark-Feld überschreitet die erlaubte Länge")
        parsed = urlsplit(fields["url"])
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("URLs müssen mit http:// oder https:// beginnen")
        if fields["id"] in ids:
            raise ValueError("Bookmark-IDs müssen eindeutig sein")
        ids.add(fields["id"])
        result.append(fields)
    return result


def write_bookmarks(bookmarks: list[dict[str, str]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(bookmarks, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(DATA_FILE)


class Handler(BaseHTTPRequestHandler):
    server_version = "BookmarkStartseite/0.1"

    def route_path(self) -> str:
        path = urlsplit(self.path).path
        ingress_path = self.headers.get("X-Ingress-Path", "").rstrip("/")
        if ingress_path and (path == ingress_path or path.startswith(ingress_path + "/")):
            path = path[len(ingress_path):] or "/"
        return path

    def ingress_path(self) -> str:
        return self.headers.get("X-Ingress-Path", "").rstrip("/")

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = self.route_path()
        if path == "/api/bookmarks":
            try:
                with DATA_LOCK:
                    bookmarks = read_bookmarks()
            except (OSError, ValueError, json.JSONDecodeError) as error:
                self.send_json({"error": str(error)}, 500)
                return
            self.send_json({"bookmarks": bookmarks})
            return
        if path != "/":
            self.send_json({"error": "Not found"}, 404)
            return
        try:
            page = INDEX_FILE.read_text(encoding="utf-8")
        except OSError as error:
            self.send_json({"error": str(error)}, 500)
            return
        page = page.replace("__BASE_PATH_JSON__", json.dumps(self.ingress_path()))
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.route_path() != "/api/bookmarks":
            self.send_json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > MAX_BODY:
                raise ValueError("Anfrage ist zu groß")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or "bookmarks" not in payload:
                raise ValueError("Erwartet wird ein Objekt mit bookmarks-Liste")
            bookmarks = validate_bookmarks(payload["bookmarks"])
            with DATA_LOCK:
                write_bookmarks(bookmarks)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as error:
            self.send_json({"error": str(error)}, 400)
            return
        except OSError as error:
            self.send_json({"error": str(error)}, 500)
            return
        self.send_json({"ok": True, "count": len(bookmarks)})

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Bookmark Startseite listening on 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
