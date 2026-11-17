"""Дымовые и приёмочные проверки развёрнутого сервиса.

Использование:
    python scripts/acceptance.py http://localhost:8207 [--closed-port 8090] [--log deployment-log.txt]
"""
import argparse
import datetime
import json
import socket
import sys
import time
import urllib.error
import urllib.request


def call(base, path, body=None):
    data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
    req = urllib.request.Request(base + path, data=data, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--closed-port", type=int, help="порт, который должен быть закрыт (старый)")
    ap.add_argument("--log", help="дописывать результат в файл")
    args = ap.parse_args()
    lines = []

    def out(text):
        line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {text}"
        print(line)
        lines.append(line)

    failed = 0

    def check(name, ok, detail=""):
        nonlocal failed
        out(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}".rstrip())
        failed += 0 if ok else 1

    out(f"target: {args.base}")
    try:
        s, b = call(args.base, "/health")
        check("1 health returns 200 and status ok", s == 200 and b.get("status") == "ok", f"version={b.get('version')}")
        s, before = call(args.base, "/report")
        check("2 report returns count", s == 200 and "count" in before, f"count={before.get('count')}")
        name = f"acceptance-{int(time.time())}"
        s, b = call(args.base, "/records", {"name": name, "value": 5})
        check("3 create record returns 201", s == 201, f"count={b.get('count')}")
        s, recs = call(args.base, "/records")
        check("4 created record is readable", s == 200 and any(r["name"] == name for r in recs))
        s, b = call(args.base, "/records", {"name": "bad", "value": "abc"})
        check("5 negative: invalid value rejected with 400", s == 400, f"error={b.get('error')}")
        s, b = call(args.base, "/no-such-route")
        check("6 negative: unknown route returns 404", s == 404)
    except (urllib.error.URLError, OSError) as exc:
        check("service reachable", False, str(exc))

    if args.closed_port:
        sock = socket.socket()
        sock.settimeout(2)
        refused = sock.connect_ex(("127.0.0.1", args.closed_port)) != 0
        sock.close()
        check(f"7 old port {args.closed_port} is closed", refused)

    out("RESULT: " + ("ALL CHECKS PASSED" if failed == 0 else f"{failed} CHECK(S) FAILED"))
    if args.log:
        with open(args.log, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
