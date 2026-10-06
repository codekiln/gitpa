"""Read Logseq page files: the property block, the body, and page-name paths."""
from __future__ import annotations
import re


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
