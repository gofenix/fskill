"""Exercise the real read CLI against loopback HTTP without external services."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


ROOT = Path(__file__).resolve().parent.parent
ARTICLE = b"""<!doctype html><html><head><title>Local article</title></head>
<body><article><h1>Local article</h1>
<p>The first paragraph contains a stable extraction marker: local-fixture-body.</p>
<p>The second paragraph gives the extractor enough article content to retain.</p>
<p>The final paragraph closes this self-contained test document.</p>
</article></body></html>"""
# Three non-empty Markdown lines with stdlib: title, source, body. This
# reproduces why a reachable page is not necessarily a successful extraction.
SHORT = b"<html><title>Short page</title><body><p>Too short.</p></body></html>"


class Handler(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        self.requests.append(self.path)
        if self.path == "/unavailable":
            self.send_error(503)
            return
        body = SHORT if self.path == "/short" else ARTICLE
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def main():
    with tempfile.TemporaryDirectory(prefix="waza-read-smoke-") as temp:
        scratch = Path(temp)
        # fetch.sh uses curl only for third-party tiers. Prevent those requests
        # even on a regression, and retain their arguments as failure evidence.
        curl_log = scratch / "curl.log"
        stub = scratch / "curl"
        stub.write_text('#!/bin/sh\nprintf "%s\\n" "$@" >> "$CURL_LOG"\nexit 99\n')
        stub.chmod(0o755)
        env = dict(os.environ, PATH=f"{scratch}{os.pathsep}{os.environ['PATH']}",
                   CURL_LOG=str(curl_log))
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        fetch = ["bash", str(ROOT / "skills/read/scripts/fetch.sh")]
        local = [sys.executable, str(ROOT / "skills/read/scripts/fetch_local.py"),
                 "--prefer", "stdlib"]

        def run(command, path, success, marker):
            result = subprocess.run(command + [base + path], env=env,
                                    capture_output=True, text=True, timeout=30)
            assert (result.returncode == 0) == success, result.stderr
            assert marker in result.stderr, result.stderr
            if success:
                assert "local-fixture-body" in result.stdout, result.stdout
                assert base + path in result.stdout, result.stdout
                assert "tier=local status=ok" in result.stderr, result.stderr
            else:
                assert not result.stdout, result.stdout
            assert not curl_log.exists(), (
                "Unexpected third-party request attempt: " + curl_log.read_text()
            )

        try:
            run(fetch, "/article", True, "tier=local status=ok")
            run(fetch + ["--use-proxy"], "/article", True, "tier=local status=ok")
            run(local, "/article", True, "extractor=stdlib")
            run(fetch, "/unavailable", False, "fetch failed:")
            run(local, "/short", False, "produced <4 non-empty lines")
            run(fetch, "/short", False, "tier=local status=fail")
            expected = ["/article"] * 3 + ["/unavailable", "/short", "/short"]
            assert Handler.requests == expected, Handler.requests
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    print("read fetch smoke: ok (6 loopback cases, no third-party requests)")


if __name__ == "__main__":
    main()
