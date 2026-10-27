#!/usr/bin/env python3
"""Harness-only static server (L2-D): serves byte-identical public/notepad.html
at / on 127.0.0.1:3000 after the dev server crashed mid-session.
Does NOT modify any app file; read-only file serving."""
import http.server, socketserver, os, sys

ROOT = "/home/z/my-project/public"

class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        if p in ("/", ""):
            return os.path.join(ROOT, "notepad.html")
        return os.path.join(ROOT, os.path.normpath(p).lstrip("/"))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    with S(("127.0.0.1", port), H) as httpd:
        httpd.serve_forever()
