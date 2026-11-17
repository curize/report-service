import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

import server


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.httpd = server.make_server(0, self.tmp.name, quiet=True)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def call(self, path, body=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_health_ok(self):
        status, body = self.call("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_health_reports_version(self):
        self.assertEqual(self.call("/health")[1]["version"], server.VERSION)

    def test_empty_report(self):
        status, body = self.call("/report")
        self.assertEqual((status, body["count"]), (200, 0))

    def test_post_record_increases_count(self):
        status, body = self.call("/records", {"name": "a", "value": 10})
        self.assertEqual((status, body["count"]), (201, 1))
        self.assertEqual(self.call("/report")[1]["total"], 10)

    def test_records_list(self):
        self.call("/records", {"name": "a", "value": 1})
        self.assertEqual(self.call("/records")[1], [{"name": "a", "value": 1}])

    def test_records_persist_after_restart(self):
        self.call("/records", {"name": "a", "value": 1})
        self.assertEqual(len(server.read_records(self.tmp.name)), 1)

    def test_invalid_value_is_rejected(self):
        self.assertEqual(self.call("/records", {"name": "a", "value": "x"})[0], 400)

    def test_blank_name_is_rejected(self):
        self.assertEqual(self.call("/records", {"name": " ", "value": 1})[0], 400)

    def test_bad_json_is_rejected(self):
        self.assertEqual(self.call("/records", b"not json")[0], 400)

    def test_unknown_route_returns_404(self):
        self.assertEqual(self.call("/nope")[0], 404)


if __name__ == "__main__":
    unittest.main()
