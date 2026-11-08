"""Serve a generated Gitpa site with the throwaway marginalia artwork."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        name = self.path.split('?')[0]
        if name == '/gitpa/prototype-marginalia.js' or name == '/gitpa/prototype-marginalia.css':
            filename = 'marginalia.js' if name.endswith('.js') else 'marginalia.css'
            data = (HERE / filename).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript' if name.endswith('.js') else 'text/css')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir(): path = path / 'index.html'
        if path.suffix == '.html' and path.is_file():
            import io
            data = path.read_bytes().replace(b'</body>', b'<link rel="stylesheet" href="/gitpa/prototype-marginalia.css"><script type="module" src="/gitpa/prototype-marginalia.js"></script></body>')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return io.BytesIO(data)
        return super().send_head()

    def copyfile(self, source, outputfile):
        super().copyfile(source, outputfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('parent', help='Directory containing the generated gitpa/ site')
    parser.add_argument('--port', type=int, default=8767)
    args = parser.parse_args()
    import os
    os.chdir(args.parent)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
