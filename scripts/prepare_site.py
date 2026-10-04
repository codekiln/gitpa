"""Prepare a website graph with asset visibility derived from public episodes."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil
from sync_episode import split_page, properties, page_path

ROOT = Path(__file__).resolve().parents[1]

def asset_links(body):
    return [name for name in re.findall(r'\[\[([^\]]+)\]\]', body) if name.startswith('GitP/A/Session/') and '/Asset/' in name]

def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Website output must be separate from the source graph')
    if output.exists():
        raise ValueError(f'Website output already exists: {output}')
    pages = {}
    pending = []
    for path in (source / 'pages').glob('*.md'):
        lines, body = split_page(path.read_text(encoding='utf-8'))
        props = properties(lines)
        name = path.stem.replace('___', '/')
        pages[name] = (lines, body)
        if props.get('public') == 'true' and '[[Logseq/Entity/Podcast/Episode]]' in props.get('logseq-entity', ''):
            pending.extend(asset_links(body))
    visible = set()
    while pending:
        name = pending.pop()
        if name in visible:
            continue
        if name not in pages:
            raise ValueError(f'Missing linked asset page: {name}')
        visible.add(name)
        pending.extend(asset_links(pages[name][1]))
    shutil.copytree(source, output)
    for name, (lines, body) in pages.items():
        if not name.startswith('GitP/A/Session/') or '/Asset/' not in name:
            continue
        lines = [line for line in lines if not line.startswith('public:: ')]
        lines.insert(0, f'public:: {str(name in visible).lower()}\n')
        page_path(output, name).write_text(''.join(lines) + body, encoding='utf-8')
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'gitp-garden')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(prepare(args.source, args.output))
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')

if __name__ == '__main__':
    main()
