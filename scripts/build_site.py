"""Publish Gitpa with Logseq Gardener."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from urllib.parse import unquote
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from logseq_page import page_name, properties, split_page
from prepare_site import prepare
from site_routes import page_route, page_output
from build_rss import ARTWORK_URL, SITE_URL
from audio_chapters import compile_episode

ROOT = Path(__file__).resolve().parents[1]
HOME = 'Ghost in the Patch'
# Gitpa's own browser plugin, which lsg's plugin host runs beside the podcast-episode
# and sequence-header plugins that gitp-garden/logseq/config.edn turns on.
PLUGINS = ['illuminated-initials']


def normalized(name):
    return unicodedata.normalize('NFC', name.strip().strip('/')).lower()


class PageRoutes:
    """Map rendered page titles to Gardener's readable page routes.

    Gardener lists every generated page in lsg-site.json so build tools need not
    parse its HTML. The All pages table is split across several files and is not
    a complete route list.
    """

    def __init__(self, output):
        self.output, self.routes = output, {}
        site = json.loads((output / 'lsg-site.json').read_text(encoding='utf-8'))
        if site.get('apiVersion') != 1:
            raise ValueError(f'Unsupported lsg-site.json apiVersion: {site.get("apiVersion")}')
        for page in site['pages']:
            # Stored pages and generated namespace pages; not the homepage or list routes.
            if page['kind'] in {'page', 'namespace'}:
                self.routes[normalized(page['title'])] = page['url']

    def file(self, route):
        """The file of a route: a folder route's index.html, or a root file such as
        the p-<digest>.html that keeps a title Gardener cannot turn into folders."""
        if route.endswith('/'):
            return self.output / unquote(route) / 'index.html'
        return self.output / route


def install_copy_feed(output):
    """Add the Copy feed URL button beside the homepage's podcast RSS feed link."""
    parser = PageRoutes(output)
    home_route = parser.routes.get(normalized(HOME))
    if not home_route:
        raise ValueError('Rendered page list does not include the homepage')
    for path in [output / 'index.html', parser.file(home_route)]:
        text = path.read_text(encoding='utf-8')
        # Gardener may add attributes such as class="external-link" to the link.
        rss_link = r'<a\b[^>]*\bhref="https://codekiln\.github\.io/gitpa/rss\.xml"[^>]*>podcast RSS feed</a>'
        if len(re.findall(rss_link, text)) != 1:
            raise ValueError('Expected one podcast RSS feed link')
        text = re.sub(rss_link, lambda match: match[0] + ' <button type="button" class="apple-podcasts-subscribe" data-copy-feed>Copy feed URL</button> <span role="status" data-copy-feed-status></span>', text)
        if text.count('</head>') != 1:
            raise ValueError('Expected one head on the homepage')
        script = f'<script type="module" src="{urlsplit(SITE_URL).path}copy-feed.js"></script>'
        path.write_text(text.replace('</head>', script + '</head>'), encoding='utf-8')
    shutil.copyfile(ROOT / 'site/copy-feed.js', output / 'copy-feed.js')


def public_pages(graph):
    """Keep explicit publication choices before applying namespace selection."""
    names = []
    for path in sorted((graph / 'pages').glob('*.md')):
        leading, _ = split_page(path.read_text(encoding='utf-8'))
        props = properties(leading)
        if props.get('public') == 'true':
            names.append(page_name(path))
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
    for path in (graph / 'pages').glob('*.md'):
        text = path.read_text(encoding='utf-8')
        leading, _ = split_page(text)
        props = properties(leading)
        if (props.get('public') != 'true'
                or '[[Logseq/Entity/Podcast/Episode]]' not in props.get('logseq-entity', '')):
            continue
        try:
            text, _ = compile_episode(text)
        except ValueError as error:
            raise ValueError(f'{path.name}: {error}') from error
        path.write_text(text, encoding='utf-8')


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


def check_property_names(diagnostics):
    """Fail on each block that shows Logseq's "Invalid property names" warning."""
    rejected = [line for line in diagnostics.splitlines() if 'Invalid property names: ' in line]
    if rejected:
        raise ValueError('Logseq rejects these property names:\n' + '\n'.join(rejected))


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
        compile_episode_pages(graph)
        args = [str(renderer), 'publish', '--graph', str(graph), '--output', str(output),
                '--filename-format', 'triple-lowbar', '--homepage', HOME,
                '--stylesheet', str(ROOT / 'site/theme.css'), '--format', 'json',
                # Pages live in folders named by their titles, and old p-<digest>.html
                # and #/page/<name> links redirect to them.
                '--readable-urls', '--redirect-old-urls']
        if search:
            args.append('--search')
        for plugin in PLUGINS:
            args.extend(['--plugin', str(ROOT / 'site' / f'{plugin}.lsg-plugin.json')])
        # Match the existing Logseq publishing policy: explicitly public pages.
        # Asset visibility and selected episode notes were resolved by prepare.
        names = public_pages(graph)
        for name in names:
            args.extend(['--include', name])
        started = time.perf_counter()
        rendered = subprocess.run(args, stderr=subprocess.PIPE, text=True)
        sys.stderr.write(rendered.stderr)
        rendered.check_returncode()
        check_property_names(rendered.stderr)
        print(f'Render garden: {time.perf_counter() - started:.2f}s', flush=True)
        started = time.perf_counter()
        install_copy_feed(output)
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
