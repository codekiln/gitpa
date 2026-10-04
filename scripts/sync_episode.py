"""Mirror episode pages and their embedded asset pages from a Logseq garden."""
from __future__ import annotations
import argparse
from datetime import date
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote, unquote

PROXY_KEYS = ('logseq-proxy-url', 'logseq-proxy-codeforge-url', 'logseq-proxy-last-sync-date')
ROOT = Path(__file__).resolve().parents[1]

def split_page(text):
    lines = text.splitlines(keepends=True)
    count = 0
    for line in lines:
        if not re.match(r'^[a-z][a-z0-9-]*:: ', line):
            break
        count += 1
    return lines[:count], ''.join(lines[count:])

def properties(lines):
    return dict(line.rstrip('\n').split(':: ', 1) for line in lines)

def page_path(garden, name):
    if not name or any(part in ('', '.', '..') for part in name.split('/')) or any(c in name for c in '\\\n\r\x00') or '___' in name:
        raise ValueError(f'Invalid page name: {name!r}')
    path = garden / 'pages' / (name.replace('/', '___') + '.md')
    if not path.resolve().is_relative_to((garden / 'pages').resolve()):
        raise ValueError(f'Page escapes garden: {name}')
    return path

def sync(source, destination, names, graph='logseq-encode-garden', forge='https://github.com/codekiln/logseq-encode-garden/blob/main', today=None):
    """Validate the whole batch before replacing any destination files."""
    source, destination = Path(source), Path(destination)
    today = today or date.today().isoformat()
    pending = list(names)
    changes = {}
    reports = []
    visited = set()
    while pending:
        name = pending.pop(0)
        if name in visited:
            continue
        visited.add(name)
        src, dest = page_path(source, name), page_path(destination, name)
        src_lines, body = split_page(src.read_text(encoding='utf-8'))
        source_props = properties(src_lines)
        if dest.exists():
            dest_lines, _ = split_page(dest.read_text(encoding='utf-8'))
            props = properties(dest_lines)
            expected = f'logseq://graph/{quote(graph, safe="")}?page={quote(name, safe="")}'
            if props.get('logseq-proxy-url') != expected:
                raise ValueError(f'Page collision or different proxy source: {dest}')
            lines = [line for line in dest_lines if line.split(':: ', 1)[0] not in PROXY_KEYS]
            mode = 'resync'
        else:
            lines = [line for line in src_lines if line.split(':: ', 1)[0] not in PROXY_KEYS]
            entities = source_props.get('logseq-entity', '')
            marker = '[[Logseq/Entity/Proxy/Page]]'
            if marker not in entities:
                entities = f'{entities}, {marker}' if entities else marker
            lines = [line for line in lines if not line.startswith('logseq-entity:: ')]
            lines.append(f'logseq-entity:: {entities}\n')
            mode = 'create'
        proxy = {
            'logseq-proxy-url': f'logseq://graph/{quote(graph, safe="")}?page={quote(name, safe="")}',
            'logseq-proxy-codeforge-url': f'{forge}/pages/{quote(src.name, safe="")}',
            'logseq-proxy-last-sync-date': f'[[{today}]]',
        }
        lines = [line if line.endswith('\n') else line + '\n' for line in lines]
        lines.extend(f'{key}:: {value}\n' for key, value in proxy.items())
        changes[dest] = (''.join(lines) + body).encode()
        pending.extend(re.findall(r'\{\{embed\s+\[\[([^\]]+)\]\]\s*\}\}', body))
        # Session download links also need their asset-page bodies on the site.
        pending.extend(link for link in re.findall(r'\[\[([^\]]+)\]\]', body) if link.startswith('GitP/A/Session/') and '/Asset/' in link)
        assets = []
        for relative in re.findall(r'\]\((\.\./assets/[^)]+)\)', body):
            relative = unquote(relative.split(' "', 1)[0])
            asset = (src.parent / relative).resolve()
            if not asset.is_relative_to((source / 'assets').resolve()):
                raise ValueError(f'Asset escapes garden: {relative}')
            target = destination / 'assets' / asset.relative_to((source / 'assets').resolve())
            if not target.resolve().is_relative_to((destination / 'assets').resolve()):
                raise ValueError(f'Asset destination escapes garden: {target}')
            if asset.is_file():
                changes[target] = asset.read_bytes()
                assets.append(str(target))
            else:
                reports.append(f'Missing source asset: {asset}')
        reports.append(f'{mode}: {src} -> {dest}; {proxy}; assets: {assets}')
    temporary = []
    try:
        for target, content in changes.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, path = tempfile.mkstemp(dir=target.parent, prefix='.proxy-')
            with os.fdopen(fd, 'wb') as handle:
                handle.write(content)
            temporary.append((Path(path), target))
        for path, target in temporary:
            path.replace(target)
    finally:
        for path, _ in temporary:
            path.unlink(missing_ok=True)
    return reports

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Source garden root')
    parser.add_argument('--destination', type=Path, default=ROOT / 'gitp-garden')
    parser.add_argument('pages', nargs='+', help='Exact logical page names')
    args = parser.parse_args()
    try:
        for report in sync(args.source, args.destination, args.pages):
            print(report)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')

if __name__ == '__main__':
    main()
