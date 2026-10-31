import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import app


class QuietHandler(app.APIHandler):
    def log_message(self, fmt, *args):
        pass


class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        app.DATA_FILE = Path(cls.tmpdir.name) / "messages.json"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmpdir.cleanup()

    def setUp(self):
        app.DATA_FILE.unlink(missing_ok=True)

    def request(self, method, path, body=None):
        data = None
        headers = {}
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data,
                                     headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_health_returns_active(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")

    def test_messages_empty_at_start(self):
        status, body = self.request("GET", "/messages")
        self.assertEqual(status, 200)
        self.assertEqual(body["total"], 0)

    def test_post_valid_message_is_saved(self):
        status, body = self.request("POST", "/messages", {"message": "halo"})
        self.assertEqual(status, 201)
        self.assertEqual(body["message"]["message"], "halo")
        status, body = self.request("GET", "/messages")
        self.assertEqual(body["total"], 1)

    def test_post_empty_message_returns_400(self):
        status, body = self.request("POST", "/messages", {"message": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "message must not be empty")

    def test_post_500_characters_is_allowed(self):
        status, _ = self.request("POST", "/messages", {"message": "a" * 500})
        self.assertEqual(status, 201)

    def test_post_501_characters_returns_400(self):
        status, body = self.request("POST", "/messages", {"message": "a" * 501})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "message must be 500 characters or fewer")

    def test_post_invalid_json_returns_400(self):
        status, body = self.request("POST", "/messages", b"bukan json")
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Invalid JSON request body")

    def test_delete_existing_message(self):
        self.request("POST", "/messages", {"message": "hapus saya"})
        status, body = self.request("DELETE", "/messages?index=0")
        self.assertEqual(status, 200)
        self.assertEqual(body["removed"]["message"], "hapus saya")
        _, body = self.request("GET", "/messages")
        self.assertEqual(body["total"], 0)

    def test_delete_missing_index_returns_404(self):
        status, _ = self.request("DELETE", "/messages?index=99")
        self.assertEqual(status, 404)

    def test_delete_non_integer_index_returns_400(self):
        status, _ = self.request("DELETE", "/messages?index=abc")
        self.assertEqual(status, 400)

    def test_unknown_path_returns_404(self):
        status, body = self.request("GET", "/halaman-asal")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "Endpoint not found")


if __name__ == "__main__":
    unittest.main()
