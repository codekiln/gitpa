"""Readable public page URLs shared by website packaging and the podcast feed."""
from pathlib import Path
from urllib.parse import quote


def page_parts(title):
    parts = title.split('/')
    if (not title or any(part in ('', '.', '..') or part != part.strip() for part in parts)
            or '\\' in title
            or any(ord(char) < 32 or ord(char) == 127 for char in title)):
        raise ValueError(f'Unsafe public page title: {title!r}')
    return parts


def page_route(title):
    return '/'.join(quote(part, safe='') for part in page_parts(title)) + '/'


def page_output(title):
    return Path(*page_parts(title)) / 'index.html'
