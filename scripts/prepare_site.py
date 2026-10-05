"""Prepare a website graph with asset visibility derived from public episodes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse
from sync_episode import split_page, properties, page_path

ROOT = Path(__file__).resolve().parents[1]

def asset_links(body):
    return [name for name in re.findall(r'\[\[([^\]]+)\]\]', body) if name.startswith('GitP/A/Session/') and '/Asset/' in name]

def selected_body(body):
    """Select the note sections marked for publication."""
    lines = body.splitlines(keepends=True)
    result, skipping, section_indent = [], False, 0
    index = 0
    while index < len(lines):
        line = lines[index]
        heading = re.match(r'^(\s*)- ## (Notes|Production notes)\s*$', line)
        if heading:
            section_indent = len(heading[1])
            selected = index + 1 < len(lines) and lines[index + 1].strip() == 'public:: true'
            skipping = not selected
            if selected:
                result.append(line)
                index += 2
                continue
        elif skipping and line.strip() and len(line) - len(line.lstrip()) <= section_indent:
            skipping = False
        if not skipping and not re.match(r'^\s*(?:id|collapsed|public)::', line):
            result.append(line)
        index += 1
    return ''.join(result)

def listener_body(name, body, pages):
    """Resolve the selected recording, artwork, and download embeds."""
    def embed(match):
        asset_name = match[1]
        if '/Asset/' not in asset_name:
            raise ValueError(f'Unsupported episode embed: {asset_name}')
        _, asset_body = pages[asset_name]
        links = re.findall(r'!?\[([^\]]*)\]\((https://[^)]+)\)', asset_body)
        if len(links) != 1:
            raise ValueError(f'Expected one public media URL: {asset_name}')
        label, url = links[0]
        extension = Path(urlparse(url).path).suffix.lower()
        if extension in {'.mp3', '.gif', '.png', '.jpg', '.jpeg', '.webp'}:
            return f'![{label}]({url})'
        parts = asset_name.split('/Asset/', 1)[1].split('/')
        label = f'MicroFreak preset {parts[1]}' if parts[0] == 'Preset' else f'{parts[1]} MIDI' if parts[0] == 'MIDI' else label
        return f'[{label}]({url})'
    return re.sub(r'\{\{embed\s+\[\[([^\]]+)\]\]\s*\}\}', embed, selected_body(body))


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
            pending.extend(asset_links(selected_body(body)))
    visible = set()
    while pending:
        name = pending.pop()
        if name in visible:
            continue
        if name not in pages:
            raise ValueError(f'Missing linked asset page: {name}')
        visible.add(name)
        pending.extend(asset_links(pages[name][1]))
    rendered = {name: listener_body(name, body, pages) for name, (lines, body) in pages.items()
                if properties(lines).get('public') == 'true' and '[[Logseq/Entity/Podcast/Episode]]' in properties(lines).get('logseq-entity', '')}
    shutil.copytree(source, output)
    for name, (lines, body) in pages.items():
        if name in rendered:
            keep = {'public', 'logseq-entity', 'podcast-published-at'}
            lines = [line for line in lines if line.split('::', 1)[0] in keep]
            published = properties(lines).get('podcast-published-at')
            if published:
                date = datetime.fromisoformat(published)
                if date.utcoffset() is None:
                    raise ValueError(f'Missing publication timezone: {name}')
                utc = date.astimezone(timezone.utc).isoformat()
                lines = [f'podcast-published-at:: {utc}\n' if line.startswith('podcast-published-at::') else line for line in lines]
            page_path(output, name).write_text(''.join(lines) + rendered[name], encoding='utf-8')
            continue
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
