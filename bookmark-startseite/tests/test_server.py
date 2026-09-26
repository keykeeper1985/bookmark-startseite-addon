import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import server  # noqa: E402


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        server.DATA_FILE = Path(cls.tempdir.name) / "data" / "bookmarks.json"
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.tempdir.cleanup()

    def setUp(self):
        if server.DATA_FILE.exists():
            server.DATA_FILE.unlink()

    def test_home_page_supports_ingress_base_path(self):
        request = Request(self.base + "/ingress/abc/", headers={"X-Ingress-Path": "/ingress/abc"})
        with urlopen(request) as response:
            page = response.read().decode()
            self.assertEqual(response.status, 200)
        self.assertIn('const BASE_PATH = "/ingress/abc";', page)
        self.assertNotIn("__BASE_PATH_JSON__", page)

    def test_bookmark_create_and_read(self):
        data = {"bookmarks": [{"id": "home", "title": "Home", "url": "https://example.com", "category": "Tools"}]}
        request = Request(self.base + "/api/bookmarks", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request) as response:
            saved = json.load(response)
            self.assertEqual(response.status, 200)
        self.assertEqual(saved, {"ok": True, "count": 1})
        with urlopen(self.base + "/api/bookmarks") as response:
            result = json.load(response)
        self.assertEqual(result["bookmarks"], data["bookmarks"])

    def test_rejects_unsafe_scheme(self):
        data = {"bookmarks": [{"id": "x", "title": "bad", "url": "javascript:alert(1)", "category": "Test"}]}
        request = Request(self.base + "/api/bookmarks", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request)
        self.assertEqual(caught.exception.code, 400)
        self.assertIn("http://", caught.exception.read().decode())

    def test_ingress_prefixed_api_route(self):
        request = Request(self.base + "/ingress/abc/api/bookmarks", headers={"X-Ingress-Path": "/ingress/abc"})
        with urlopen(request) as response:
            self.assertEqual(json.load(response), {"bookmarks": []})


if __name__ == "__main__":
    unittest.main()
