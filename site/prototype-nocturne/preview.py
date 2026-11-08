#!/usr/bin/env python3
"""PROTOTYPE: serve a built Gitpa site with the Nocturne artwork injected."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent

class Preview(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split('?', 1)[0] in ('/__nocturne__/nocturne.js', '/__nocturne__/nocturne.css'):
            path = HERE / self.path.split('?', 1)[0].rsplit('/', 1)[-1]
            data = path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript' if path.suffix == '.js' else 'text/css')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / 'index.html'
        if path.suffix != '.html' or not path.is_file():
            return super().send_head()
        import io
        data = path.read_text(encoding='utf-8').replace('</head>',
            '<link rel="stylesheet" href="/__nocturne__/nocturne.css">'
            '<script type="module" src="/__nocturne__/nocturne.js"></script></head>').encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        return io.BytesIO(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', help='parent directory of the generated gitpa folder')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    print(f'Preview: http://localhost:{args.port}/gitpa/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Preview, directory=args.directory)).serve_forever()
