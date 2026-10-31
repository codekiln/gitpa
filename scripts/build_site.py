"""Publish Gitpa with Logseq Gardener and the evaluated Logseq homepage query."""
from __future__ import annotations
import argparse
import json
import html
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata
from urllib.parse import unquote
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from logseq_page import properties, split_page
from prepare_site import prepare
from site_routes import page_route, page_output
from build_rss import ARTWORK_URL, SITE_URL
from audio_chapters import compile_episode

ROOT = Path(__file__).resolve().parents[1]
HOME = 'Ghost in the Patch'
QUERY_PLACEHOLDER = 'GITPA-EVALUATED-HOMEPAGE-QUERY-RESULTS'


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
    # Evaluated rows are presentation, not authored references or search content.
    placeholder = (f'- ## {result["title"][1]}\n\t- {QUERY_PLACEHOLDER}\n'
                   '\t  search-exclude:: true\n')
    text, count = re.subn(pattern, lambda _: placeholder, text)
    if count != 1:
        raise ValueError('Expected one homepage query')
    path.write_text(text, encoding='utf-8')


class PageRoutes:
    """Map rendered page titles to Gardener's page files.

    Gardener lists every generated file in lsg-site.json so build tools need not
    parse its HTML. The All pages table is split across several files and is not
    a complete route list.
    """

    def __init__(self, output=None):
        self.routes, self.titles = {}, {}
        if output is None:
            return
        site = json.loads((output / 'lsg-site.json').read_text(encoding='utf-8'))
        if site.get('apiVersion') != 1:
            raise ValueError(f'Unsupported lsg-site.json apiVersion: {site.get("apiVersion")}')
        for page in site['pages']:
            # Stored pages and generated namespace pages; not the homepage or list routes.
            if page['kind'] in {'page', 'namespace'} and re.fullmatch(r'p-[0-9a-f]+\.html', page['url']):
                self.routes[normalized(page['title'])] = page['url']
                self.titles[page['url']] = page['title']


def install_homepage_query(output, result):
    """Insert validated query rows after Gardener has indexed authored references."""
    query_outline(result)
    parser = PageRoutes(output)
    rows = []
    for item in result['view'][1:]:
        label = item[1][2]
        route = parser.routes.get(normalized(label))
        if not route:
            raise ValueError(f'Query target was not rendered: {label}')
        rows.append(f'<li><a href="{html.escape(route, quote=True)}">{html.escape(label)}</a></li>')
    home_route = parser.routes.get(normalized(HOME))
    if not home_route:
        raise ValueError('Rendered page list does not include the homepage')
    for filename in ['index.html', home_route]:
        path = output / filename
        text = path.read_text(encoding='utf-8')
        bullet = '<a class="bullet" href="#"></a>'
        markers = [(f'<li>{QUERY_PLACEHOLDER}</li>', ''),
                   (f'<li>{bullet}{QUERY_PLACEHOLDER}</li>', bullet)]
        matches = [(marker, prefix) for marker, prefix in markers if marker in text]
        if text.count(QUERY_PLACEHOLDER) != 1 or len(matches) != 1:
            raise ValueError('Expected one rendered homepage query placeholder')
        marker, prefix = matches[0]
        rendered_rows = ''.join(row.replace('<li>', f'<li>{prefix}', 1) for row in rows)
        text = text.replace(marker, rendered_rows)
        # Gardener may add attributes such as class="external-link" to the link.
        rss_link = r'<a\b[^>]*\bhref="https://codekiln\.github\.io/gitpa/rss\.xml"[^>]*>podcast RSS feed</a>'
        if len(re.findall(rss_link, text)) != 1:
            raise ValueError('Expected one podcast RSS feed link')
        text = re.sub(rss_link, lambda match: match[0] + ' <button type="button" class="apple-podcasts-subscribe" data-copy-feed>Copy feed URL</button> <span role="status" data-copy-feed-status></span>', text)
        path.write_text(text, encoding='utf-8')


def legacy_routes(output, graph=None, published_routes=None):
    """Preserve published Logseq hash links, including episode URLs in RSS."""
    if published_routes is None:
        parser = PageRoutes(output)
    else:
        parser = PageRoutes()
        parser.routes = dict(published_routes)
    if normalized(HOME) not in parser.routes:
        raise ValueError('Rendered page list does not include the homepage')
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
    (output / 'legacy-routes.json').write_text(routes, encoding='utf-8')
    script = '''const routes = ROUTES;
const routeRoot = new URL(SITE_BASE, location.origin);
function openLegacyPage() {
  if (!location.hash.startsWith('#/page/')) return;
  let name;
  try { name = decodeURIComponent(location.hash.slice(7)); }
  catch { return; }
  name = name.trim().replace(/^\\/+|\\/+$/g, '').normalize('NFC').toLowerCase();
  if (Object.hasOwn(routes, name)) {
    const target = new URL(routes[name], routeRoot).href;
    if (window.gitpaNavigate) window.gitpaNavigate(target, {replace: true});
    else location.replace(target);
  }
}
window.addEventListener('hashchange', openLegacyPage);
openLegacyPage();
'''.replace('SITE_BASE', json.dumps(urlsplit(SITE_URL).path)).replace('ROUTES', routes)
    (output / 'legacy-routes.js').write_text(script, encoding='utf-8')
    home = output / 'index.html'
    startup = """<script>(()=>{let pending=false;function load(){
if(!location.hash.startsWith('#/page/')||pending)return;pending=true;
const script=document.createElement('script');script.src=new URL('legacy-routes.js',new URL(SITE_BASE,location.origin)).href;
script.onerror=()=>{pending=false;script.remove()};document.head.append(script)}
window.addEventListener('hashchange',load);load()})();</script>""".replace(
        'SITE_BASE', json.dumps(urlsplit(SITE_URL).path))
    home.write_text(home.read_text(encoding='utf-8').replace(
        '</head>', startup + '</head>'), encoding='utf-8')


def public_pages(graph):
    """Keep explicit publication choices before applying namespace selection."""
    names = []
    for path in sorted((graph / 'pages').glob('*.md')):
        leading, _ = split_page(path.read_text(encoding='utf-8'))
        props = properties(leading)
        if props.get('public') == 'true':
            names.append(path.stem.replace('___', '/'))
        else:
            # Every stored page outside Gitpa's explicit publication list stays
            # withheld, even when an included namespace would select it.
            # Keep only its identity so the renderer cannot recreate it as an
            # ancestor collection; no source body or aliases reach that marker.
            title = None
            for line in path.read_text(encoding='utf-8').splitlines():
                match = re.fullmatch(r'([A-Za-z][A-Za-z0-9-]*):: (.*)', line)
                if not match:
                    break
                if match[1].lower() == 'title':
                    title = match[2]
            marker = 'public:: false\n'
            if title:
                marker += f'title:: {title}\n'
            path.write_text(marker, encoding='utf-8')
    return names


def compile_episode_pages(graph):
    episodes = {}
    for path in (graph / 'pages').glob('*.md'):
        text = path.read_text(encoding='utf-8')
        leading, _ = split_page(text)
        props = properties(leading)
        if (props.get('public') != 'true'
                or '[[Logseq/Entity/Podcast/Episode]]' not in props.get('logseq-entity', '')):
            continue
        try:
            text, recording = compile_episode(text)
        except ValueError as error:
            raise ValueError(f'{path.name}: {error}') from error
        path.write_text(text, encoding='utf-8')
        episodes[normalized(path.stem.replace('___', '/'))] = recording
    return episodes


def install_episode_player(output, episodes):
    """Install persistent navigation everywhere and identify playable episodes."""
    parser = PageRoutes(output)
    base = urlsplit(SITE_URL).path
    for name, recording in episodes.items():
        route = parser.routes.get(name)
        if not route:
            raise ValueError(f'Published episode was not rendered: {name}')
        path = output / route
        text = path.read_text(encoding='utf-8')
        sources = re.findall(r'<audio\b[^>]*\bsrc="([^"]+)"', text)
        if len(sources) != 1 or html.unescape(sources[0]) != recording:
            raise ValueError(f'Episode player needs exactly one full recording: {name}')
        canonical = base + page_route(parser.titles[route])
        metadata = (f'<meta name="gitpa-episode" content="{html.escape(recording, quote=True)}">'
                    f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">')
        path.write_text(text.replace('</head>', metadata + '</head>'), encoding='utf-8')
    additions = (f'<link rel="stylesheet" href="{base}player.css">'
                 f'<script type="module" src="{base}bootstrap.js"></script>')
    for path in output.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('</head>', additions + '</head>'), encoding='utf-8')
    for filename in ['bootstrap.js', 'player.js', 'player.css', 'navigation.js']:
        shutil.copyfile(ROOT / 'site' / filename, output / filename)


def package_pages(output):
    """Give rendered pages namespace URLs while retaining hash-file compatibility."""
    parser = PageRoutes(output)
    base = urlsplit(SITE_URL).path
    destinations, claims, directories = {}, {}, {}
    for route, title in parser.titles.items():
        path = page_output(title)
        claim = unicodedata.normalize('NFC', str(path)).casefold()
        if claim in claims:
            raise ValueError(f'Public page path collision: {title} and {claims[claim]}')
        claims[claim] = title
        destination = output / path
        for parent in path.parents:
            if parent == Path('.'):
                continue
            key = unicodedata.normalize('NFC', str(parent)).casefold()
            if key in directories and directories[key] != str(parent):
                raise ValueError(f'Public page directory collision: {title}')
            directories[key] = str(parent)
            if (output / parent).is_file():
                raise ValueError(f'Public page path collides with existing output: {title}')
        if path.parts[0].casefold() in {'assets', 'index.html', 'pages.html', 'custom.css',
                                       'legacy-routes.js', 'legacy-routes.json', 'player.js', 'player.css', 'navigation.js', 'rss.xml', '.nojekyll'}:
            raise ValueError(f'Public page path collides with asset namespace: {title}')
        if destination.exists():
            raise ValueError(f'Public page path collides with existing output: {title}')
        destinations[route] = (destination, page_route(title))

    for claim in claims.keys() & directories.keys():
        raise ValueError(f'Public page file/directory collision: {claims[claim]}')

    def rewrite(text):
        def attribute(match):
            value = html.unescape(match[2])
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith(('/', '#')):
                return match[0]
            path = parsed.path
            if path in destinations:
                path = base + destinations[path][1]
            elif path == 'index.html':
                path = base
            elif path:
                path = base + path
            else:
                return match[0]
            value = urlunsplit(('', '', path, parsed.query, parsed.fragment))
            return f'{match[1]}="{html.escape(value, quote=True)}"'
        return re.sub(r'\b(href|src)="([^"]*)"', attribute, text)

    for path in list(output.glob('*.html')):
        text = rewrite(path.read_text(encoding='utf-8'))
        path.write_text(text, encoding='utf-8')
        if path.name in destinations:
            destination, _ = destinations[path.name]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding='utf-8')
    return {normalized(title): page_route(title) for title in parser.titles.values()}


def publish_feed(source, output, feed=None):
    """Retain subscribed artwork URLs and require every feed link to exist."""
    artwork = 'assets/gitp/logo/gitp_logo_raw_fly.JPG'
    artwork_source = source / artwork
    if not artwork_source.is_file() or not artwork_source.resolve().is_relative_to((source / 'assets').resolve()):
        raise ValueError('Podcast artwork is missing or outside graph assets')
    artwork_output = output / artwork
    artwork_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artwork_source, artwork_output)
    content = (feed or ROOT / 'rss.xml').read_bytes()
    root = ET.fromstring(content)
    for item in root.findall('./channel/item'):
        url = item.findtext('link', '')
        if not url.startswith(SITE_URL):
            raise ValueError(f'Podcast episode is outside the published site: {url}')
        route = url[len(SITE_URL):]
        title = unquote(route.rstrip('/'))
        if route != page_route(title) or not (output / page_output(title)).is_file():
            raise ValueError(f'Podcast episode page is missing: {url}')
    if root.findtext('./channel/image/url') != ARTWORK_URL:
        raise ValueError('Podcast artwork URL does not match the compatibility asset')
    (output / 'rss.xml').write_bytes(content)


def publish(source, output, renderer, search=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Website output must be separate from the source graph')
    if output.exists():
        raise ValueError('Website output already exists')
    with tempfile.TemporaryDirectory(prefix='gitpa-publication-') as temporary:
        temporary = Path(temporary)
        started = time.perf_counter()
        graph = prepare(source, temporary / 'graph')
        print(f'Prepare graph: {time.perf_counter() - started:.2f}s', flush=True)
        query = temporary / 'homepage.json'
        started = time.perf_counter()
        subprocess.run(['nbb-logseq', str(ROOT / 'scripts/check_homepage.cljs'),
                        str(graph), str(query), '--prepared'], cwd=ROOT, check=True)
        print(f'Validate homepage query: {time.perf_counter() - started:.2f}s', flush=True)
        query_result = json.loads(query.read_text(encoding='utf-8'))
        prepare_homepage(graph, query_result)
        episodes = compile_episode_pages(graph)
        args = [str(renderer), 'publish', '--graph', str(graph), '--output', str(output),
                '--filename-format', 'triple-lowbar', '--homepage', HOME,
                '--stylesheet', str(ROOT / 'site/theme.css'), '--format', 'json']
        if search:
            args.append('--search')
        # Match the existing Logseq publishing policy: explicitly public pages.
        # Asset visibility and selected episode notes were resolved by prepare.
        for name in public_pages(graph):
            args.extend(['--include', name])
        started = time.perf_counter()
        subprocess.run(args, check=True)
        print(f'Render garden: {time.perf_counter() - started:.2f}s', flush=True)
        started = time.perf_counter()
        install_homepage_query(output, query_result)
        install_episode_player(output, episodes)
        routes = package_pages(output)
        legacy_routes(output, graph, published_routes=routes)
        publish_feed(source, output)
        (output / '.nojekyll').touch()
        print(f'Package site: {time.perf_counter() - started:.2f}s', flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'gitp-garden')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--search', action='store_true', help='Export shared static search data')
    args = parser.parse_args()
    try:
        print(publish(args.source, args.output, args.renderer, search=args.search))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
