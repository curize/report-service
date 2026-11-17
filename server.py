"""HTTP-сервис отчётов (практическая работа № 5, вариант 7)."""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import report

VERSION = "1.0.1"
DEFAULT_PORT = 8080
_lock = threading.Lock()


def get_port(env=None):
    """Порт берётся из переменной окружения PORT (по умолчанию 8080)."""
    env = os.environ if env is None else env
    raw = env.get("PORT", str(DEFAULT_PORT))
    try:
        port = int(raw)
    except ValueError:
        raise ValueError(f"PORT must be an integer, got {raw!r}")
    if not 1 <= port <= 65535:
        raise ValueError(f"PORT out of range: {port}")
    return port


def data_path(data_dir):
    return os.path.join(data_dir, "data.json")


def read_records(data_dir):
    path = data_path(data_dir)
    if not os.path.exists(path):
        return []
    return report.load_data(path)


def write_records(data_dir, records):
    os.makedirs(data_dir, exist_ok=True)
    part = data_path(data_dir) + ".part"
    with open(part, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    os.replace(part, data_path(data_dir))


def make_handler(data_dir, quiet=False):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ReportService/" + VERSION

        def log_message(self, fmt, *args):
            if not quiet:
                sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))
                sys.stdout.flush()

        def _send(self, code, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok", "version": VERSION})
            elif self.path == "/report":
                with _lock:
                    records = read_records(data_dir)
                self._send(200, report.build_report(records))
            elif self.path == "/records":
                with _lock:
                    records = read_records(data_dir)
                self._send(200, records)
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/records":
                self._send(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                record = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(record, dict) or not str(record.get("name", "")).strip():
                    raise ValueError("record must contain non-empty 'name'")
                report.build_report([record])
            except (ValueError, UnicodeDecodeError) as exc:
                self._send(400, {"error": str(exc)})
                return
            with _lock:
                records = read_records(data_dir)
                records.append({"name": record["name"], "value": record["value"]})
                write_records(data_dir, records)
            self._send(201, {"count": len(records)})

    return Handler


def make_server(port, data_dir, quiet=False):
    return ThreadingHTTPServer(("0.0.0.0", port), make_handler(data_dir, quiet))


def main():
    data_dir = os.environ.get("DATA_DIR", "data")
    try:
        port = get_port()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    server = make_server(port, data_dir)
    print(f"report-service {VERSION} listening on port {port}, data dir: {data_dir}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
