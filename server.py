"""Místní prohlížení galerie, pouze se standardní knihovnou Pythonu 3."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import mimetypes
import sys
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / 'obrázky'
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.pdf'}


class GalleryHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        path = unquote(urlsplit(self.path).path)
        if path == '/galerie.json':
            try:
                items = [
                    {'name': p.name, 'version': str(p.stat().st_mtime_ns)}
                    for p in IMAGES.iterdir()
                    if not p.is_symlink() and p.is_file() and p.suffix.lower() in EXTENSIONS
                ]
                body = json.dumps(items, ensure_ascii=False).encode('utf-8')
            except OSError:
                self.send_error(500, 'Cannot read image folder')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)
            return
        if path in ('/', '/index.html'):
            file = ROOT / 'index.html'
        elif path.startswith('/obrázky/'):
            name = path[len('/obrázky/'):]
            file = IMAGES / name
            if not name or '/' in name or '\\' in name or file.suffix.lower() not in EXTENSIONS:
                self.send_error(404)
                return
        else:
            self.send_error(404)
            return
        if file.is_symlink() or not file.is_file():
            self.send_error(404)
            return
        try:
            with file.open('rb') as stream:
                size = file.stat().st_size
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(size))
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                if not head:
                    while chunk := stream.read(256 * 1024):
                        self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == '__main__':
    IMAGES.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), GalleryHandler)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Galerie běží: {url}', flush=True)
    print('Vkládejte fotografie a PDF do složky obrázky. Toto okno nechte otevřené.')
    print('Ukončení: Ctrl+C.')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
