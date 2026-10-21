"""Publish Gitpa with Logseq Gardener and the evaluated Logseq homepage query."""
from __future__ import annotations
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata
from urllib.parse import unquote

from logseq_page import properties, split_page
from prepare_site import prepare

ROOT = Path(__file__).resolve().parents[1]
HOME = 'Ghost in the Patch'


def normalized(name):
    return unicodedata.normalize('NFC', name.strip().strip('/')).lower()


def query_outline(result):
    """Translate the evaluated homepage view into ordinary Logseq blocks."""
    title, view = result['title'], result['view']
    if not (isinstance(title, list) and len(title) == 2 and title[0] == 'h2'
            and isinstance(title[1], str)):
        raise ValueError('Expected an h2 query title')
    if not (isinstance(view, list) and view and view[0] == 'ul'):
        raise ValueError('Expected a list from the homepage query view')
    lines = [f'- ## {title[1]}']
    for item in view[1:]:
        if not (isinstance(item, list) and len(item) == 2 and item[0] == 'li'):
            raise ValueError('Expected a query list item')
        link = item[1]
        if not (isinstance(link, list) and len(link) == 3 and link[0] == 'a'
                and isinstance(link[1], dict) and isinstance(link[2], str)):
            raise ValueError('Expected a query page link')
        href = link[1].get('href', '')
        if not href.startswith('#/page/'):
            raise ValueError('Expected a Logseq page route')
        name = unquote(href[len('#/page/'):])
        if any(c in name + link[2] for c in '\n\r[]|'):
            raise ValueError('Invalid query page link')
        if normalized(name) != normalized(link[2]):
            raise ValueError('Expected the original page name as query link label')
        lines.append(f'\t- [[{link[2]}]]')
    return '\n'.join(lines) + '\n'


def prepare_homepage(graph, result):
    path = graph / 'pages' / f'{HOME}.md'
    text = path.read_text(encoding='utf-8')
    # The original query stays in the checked-in garden. Only the temporary
    # publication graph receives its evaluated result.
    pattern = r'(?ms)^- query-table::.*?^  #\+END_QUERY\s*$'
    outline = query_outline(result)
    visible = set()
    for page in (graph / 'pages').glob('*.md'):
        leading, _ = split_page(page.read_text(encoding='utf-8'))
        if properties(leading).get('public') == 'true':
            visible.add(normalized(page.stem.replace('___', '/')))
    for target in re.findall(r'\[\[([^\]]+)\]\]', outline):
        if normalized(target) not in visible:
            raise ValueError(f'Homepage query target is missing or unpublished: {target}')
    text, count = re.subn(pattern, lambda _: outline, text)
    if count != 1:
        raise ValueError('Expected one homepage query')
    path.write_text(text, encoding='utf-8')


class PageRoutes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.routes, self.href, self.label = {}, None, ''

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if re.fullmatch(r'p-[0-9a-f]+\.html', href):
                self.href, self.label = href, ''

    def handle_data(self, data):
        if self.href:
            self.label += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.href:
            self.routes[normalized(self.label)] = self.href
            self.href = None


def legacy_routes(output, graph=None):
    """Preserve published Logseq hash links, including episode URLs in RSS."""
    parser = PageRoutes()
    parser.feed((output / 'pages.html').read_text(encoding='utf-8'))
    if normalized(HOME) not in parser.routes:
        raise ValueError('Rendered all-pages index does not include the homepage')
    if graph:
        claims = {name: {route} for name, route in parser.routes.items()}
        for page in (graph / 'pages').glob('*.md'):
            route = parser.routes.get(normalized(page.stem.replace('___', '/')))
            if not route:
                continue
            leading, _ = split_page(page.read_text(encoding='utf-8'))
            aliases = properties(leading).get('alias', '')
            # Match the garden's direct page-ref and comma-separated plain aliases.
            for match in re.finditer(r'\s*(?:\[\[([^\]]+)\]\]|([^,]+))\s*(?:,|$)', aliases):
                alias = (match[1] or match[2]).strip()
                if alias:
                    claims.setdefault(normalized(alias), set()).add(route)
        parser.routes = {name: next(iter(routes)) for name, routes in claims.items()
                         if len(routes) == 1}
    routes = json.dumps(parser.routes, ensure_ascii=True).replace('<', '\\u003c')
    script = '''const routes = ROUTES;
function openLegacyPage() {
  if (!location.hash.startsWith('#/page/')) return;
  let name;
  try { name = decodeURIComponent(location.hash.slice(7)); }
  catch { return; }
  name = name.trim().replace(/^\\/+|\\/+$/g, '').normalize('NFC').toLowerCase();
  if (Object.hasOwn(routes, name)) {
    location.replace(new URL(routes[name], document.baseURI).href);
  }
}
window.addEventListener('hashchange', openLegacyPage);
openLegacyPage();
'''.replace('ROUTES', routes)
    (output / 'legacy-routes.js').write_text(script, encoding='utf-8')
    home = output / 'index.html'
    home.write_text(home.read_text(encoding='utf-8').replace(
        '</head>', '<script src="legacy-routes.js" defer></script></head>'), encoding='utf-8')


def public_pages(graph):
    """Keep explicit publication choices before applying namespace selection."""
    names = []
    for path in sorted((graph / 'pages').glob('*.md')):
        leading, _ = split_page(path.read_text(encoding='utf-8'))
        if properties(leading).get('public') == 'true':
            names.append(path.stem.replace('___', '/'))
        else:
            path.unlink()
    return names


def publish(source, output, renderer):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Website output must be separate from the source graph')
    if output.exists():
        raise ValueError('Website output already exists')
    with tempfile.TemporaryDirectory(prefix='gitpa-publication-') as temporary:
        temporary = Path(temporary)
        graph = prepare(source, temporary / 'graph')
        query = temporary / 'homepage.json'
        subprocess.run(['nbb-logseq', str(ROOT / 'scripts/check_homepage.cljs'),
                        str(source), str(query)], cwd=ROOT, check=True)
        prepare_homepage(graph, json.loads(query.read_text(encoding='utf-8')))
        args = [str(renderer), 'publish', '--graph', str(graph), '--output', str(output),
                '--filename-format', 'triple-lowbar', '--homepage', HOME,
                '--stylesheet', str(ROOT / 'site/theme.css'), '--format', 'json']
        # Match the existing Logseq publishing policy: explicitly public pages.
        # Asset visibility and selected episode notes were resolved by prepare.
        for name in public_pages(graph):
            args.extend(['--include', name])
        subprocess.run(args, check=True)
        legacy_routes(output, graph)
        (output / 'rss.xml').write_bytes((ROOT / 'rss.xml').read_bytes())
        (output / '.nojekyll').touch()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'gitp-garden')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--renderer', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(publish(args.source, args.output, args.renderer))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
