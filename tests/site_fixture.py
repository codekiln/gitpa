"""Write the lsg-site.json route list that Gardener produces."""
import json


def write_site(output, pages):
    """Record (route, title) pairs as rendered pages."""
    entries = [{'id': title.lower(), 'kind': 'page', 'title': title, 'url': route}
               for route, title in pages]
    (output / 'lsg-site.json').write_text(
        json.dumps({'apiVersion': 1, 'assets': [], 'pages': entries, 'revision': 'test'}),
        encoding='utf-8')
