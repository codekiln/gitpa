"""Compile published episode timestamps against one complete recording."""
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

MACRO = re.compile(r'\{\{audio-timestamp\s+([^{}]+?)\s*\}\}')
HEADING = re.compile(r'^(\s*)- ### (.+)$')
LEGACY_TIME = re.compile(r'^(\d+:\d{2}(?::\d{2})?)(?=\s|[–—-]|$)')
MEDIA = re.compile(r'^\s*- !\[([^\]]*)\]\((https://[^)]+)\)\s*$')


def code_lines(lines):
    literal, fence = set(), None
    for index, line in enumerate(lines):
        match = re.match(r'^\s*(?:-\s*)?(`{3,}|~{3,})(.*)$', line.rstrip('\n'))
        if fence:
            literal.add(index)
            closing = re.match(r'^\s*(`{3,}|~{3,})\s*$', line.rstrip('\n'))
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= len(fence):
                fence = None
        elif match:
            literal.add(index)
            fence = match[1]
    return literal


def outside_inline_code(line, transform):
    """Keep inline code spans literal while compiling surrounding prose."""
    result, position = [], 0
    for opening in re.finditer(r'`+', line):
        if opening.start() < position:
            continue
        closing = re.search(r'(?<!`)' + re.escape(opening[0]) + r'(?!`)', line[opening.end():])
        if not closing:
            continue
        end = opening.end() + closing.end()
        result.extend([transform(line[position:opening.start()]), line[opening.start():end]])
        position = end
    result.append(transform(line[position:]))
    return ''.join(result)


def timestamp_label(value):
    seconds = timestamp_seconds(value)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f'{hours}:{minutes:02}:{seconds:02}' if hours else f'{minutes}:{seconds:02}'


def timestamp_seconds(value):
    """Accept integer seconds, M:SS, or H:MM:SS; reject partial times."""
    if re.fullmatch(r'[0-9]+', value):
        return int(value)
    parts = value.split(':')
    if (len(parts) not in (2, 3) or not re.fullmatch(r'[0-9]+', parts[0])
            or any(not re.fullmatch(r'[0-5][0-9]', part) for part in parts[1:])):
        raise ValueError(f'Invalid audio timestamp: {value!r}')
    return int(parts[0]) * (60 if len(parts) == 2 else 3600) + sum(
        int(part) * (60 if len(parts) == 3 and i == 0 else 1)
        for i, part in enumerate(parts[1:]))


def recording_fragment(recording, value):
    parsed = urlsplit(recording)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query,
                       f't={timestamp_seconds(value)}'))


def generated_chapter_media(url, recording):
    """Recognize only derivatives of this exact full-recording filename."""
    media, full = urlsplit(url), urlsplit(recording)
    stem = full.path.rsplit('.', 1)[0]
    return (media.scheme == full.scheme and media.netloc == full.netloc
            and not media.query and not media.fragment
            and re.fullmatch(re.escape(stem) + r'___[0-9]{4,}-[0-9]{4,}\.(?:png|mp3)', media.path) is not None)


def compile_episode(text):
    """Return temporary publication text and its full recording URL.

    Chapter derivatives are removed only beneath a timestamped H3. Any notes
    nested under a removed media item move up with the retained outline.
    """
    lines = text.splitlines(keepends=True)
    literals = code_lines(lines)
    indents = sorted({len(re.match(r'^\s*', line)[0].expandtabs(4))
                      for index, line in enumerate(lines)
                      if index not in literals and re.match(r'^\s*- ', line)})
    unit = min((b - a for a, b in zip(indents, indents[1:]) if b > a), default=4)
    recordings = []
    for index, line in enumerate(lines):
        if index in literals:
            continue
        media = MEDIA.fullmatch(line.rstrip('\n'))
        indent = len(re.match(r'^\s*', line)[0].expandtabs(4))
        if media and indent == unit:
            if urlsplit(media[2]).path.lower().endswith(('.mp3', '.wav', '.ogg')):
                recordings.append(media[2])
    if len(recordings) != 1:
        raise ValueError('A published episode needs one full recording directly beneath its title')
    recording = recordings[0]
    result, chapter_indent, removed = [], None, []
    last_block_removed = False
    for index, line in enumerate(lines):
        prefix = re.match(r'^[\t ]*', line)[0]
        indent = len(prefix.expandtabs(4))
        literal = index in literals
        is_block = not literal and re.match(r'^\s*- ', line) is not None
        if is_block:
            removed = [level for level in removed if level < indent]
            if chapter_indent is not None and indent <= chapter_indent:
                chapter_indent = None
        heading = None if literal else HEADING.match(line.rstrip('\n'))
        if heading:
            content = heading[2]
            time = LEGACY_TIME.match(content)
            if content.startswith('{{audio-timestamp'):
                chapter_indent = indent
            elif time:
                chapter_indent = indent
                value = time[1]
                link = f'[{value}]({recording_fragment(recording, value)})'
                line = line.replace(content, link + content[len(value):], 1)
        media = None if literal else MEDIA.fullmatch(line.rstrip('\n'))
        if chapter_indent is not None and indent > chapter_indent and media:
            if generated_chapter_media(media[2], recording):
                removed.append(indent)
                last_block_removed = True
                continue
        # Properties of removed media do not belong to the surviving parent.
        if not literal and last_block_removed and re.match(r'^\s+[a-z][a-z0-9-]*:: ', line):
            continue
        if is_block:
            last_block_removed = False
        def compile_prose(prose):
            prose = prose.replace('Chapter waveforms show synth above commentary; each chapter player combines both.',
                                  'Select a chapter timestamp to play from that point in the full recording.')
            prose = MACRO.sub(lambda match: f'[{timestamp_label(match[1])}]({recording_fragment(recording, match[1])})', prose)
            if '{{audio-timestamp' in prose:
                raise ValueError('Malformed audio-timestamp macro')
            return prose
        if not literal:
            line = outside_inline_code(line, compile_prose)
        if removed:
            remaining = max(0, indent - len(removed) * unit)
            if '\t' in prefix:
                line = '\t' * (remaining // 4) + ' ' * (remaining % 4) + line[len(prefix):]
            else:
                line = ' ' * remaining + line[len(prefix):]
        result.append(line)
    return ''.join(result), recording
