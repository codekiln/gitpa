"""Build the podcast feed from public Logseq episode proxies."""

from __future__ import annotations

import argparse
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import re
from html import escape

from logseq_page import split_page, properties, page_path
from site_routes import page_route
from prepare_site import selected_body
import asset_mounts
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
GARDEN = ROOT / "gitp-garden"
OUTPUT = ROOT / "rss.xml"
SITE_URL = "https://codekiln.github.io/gitpa/"
FEED_URL = SITE_URL + "rss.xml"
ARTWORK_URL = SITE_URL + "assets/gitp/logo/gitp_logo_raw_fly.JPG"
ITUNES = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ATOM = "http://www.w3.org/2005/Atom"

ET.register_namespace("itunes", ITUNES)
ET.register_namespace("atom", ATOM)


def required(record: dict, name: str, path: Path) -> str:
    value = record.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: {name} must be a nonempty string")
    return value.strip()


def https_url(record: dict, name: str, path: Path) -> str:
    value = required(record, name, path)
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{path}: {name} must be an HTTPS URL")
    if parsed.username or parsed.password:
        raise ValueError(f"{path}: {name} cannot contain credentials")
    return value


def audio_metadata(url: str) -> tuple[int, str]:
    with urlopen(Request(url, method="HEAD"), timeout=30) as response:
        length = int(response.headers.get("Content-Length", "0"))
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
        if length <= 0 or content_type != "audio/mpeg":
            raise ValueError(f"{url}: expected a nonempty public audio/mpeg file")
        return length, content_type


def plain(text: str) -> str:
    """Logseq inline markup as listener text.

    A labelled link or web link keeps its label, code keeps its text, a
    page link keeps the last part of the page name, and emphasis markers
    are dropped.
    """
    text = re.sub(r"\[([^\]]*)\]\(\[\[[^\]]+\]\]\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", lambda link: link[1].rsplit("/", 1)[-1], text)
    return re.sub(r"(\*\*|\*)(\S(?:.*?\S)?)\1", r"\2", text)


def outline(body: str) -> list[tuple[int, str]]:
    """Return each block of a Logseq outline as its depth and text.

    A block's continuation lines join its text on new lines; block properties
    are left out. An unbulleted first line, such as a page's opening heading,
    is a block at depth 0.
    """
    blocks: list[list] = []
    for line in body.splitlines():
        bullet = re.match(r"^(\t*)- ?(.*)$", line)
        if bullet:
            blocks.append([len(bullet[1]), bullet[2].strip()])
        elif not line.strip() or re.match(r"^\s*[a-z][a-z0-9-]*:: ", line):
            continue
        elif blocks:
            blocks[-1][1] += "\n" + line.strip()
        else:
            blocks.append([0, line.strip()])
    return [(depth, text) for depth, text in blocks]


def page_embed(text: str) -> str | None:
    """The page an embed block shows, unless it is an asset page."""
    embed = re.fullmatch(r"\{\{embed\s+\[\[([^\]]+)\]\]\s*\}\}", text)
    return embed[1] if embed and "/Asset/" not in embed[1] else None


def paragraph(text: str) -> bool:
    return bool(text) and not re.match(r"#+ ", text) and not text.startswith(("![", "{{embed"))


def link_name(name: str) -> str:
    return name.rsplit("/", 1)[-1]


def inline_html(text: str, public_url) -> str:
    """Logseq inline markup as feed HTML.

    A page link becomes a link to its page on the website when that page is
    public there, and plain text otherwise. Web links keep their targets;
    emphasis and code markers are dropped.
    """
    token = re.compile(
        r"\[([^\]]*)\]\(\[\[([^\]]+)\]\]\)"   # [label]([[Page]])
        r"|\[([^\]]*)\]\((https?://[^)\s]+)\)"    # [label](https://...)
        r"|\[\[([^\]]+)\]\]"                      # [[Page]]
        r"|`([^`]*)`"                                   # `code`
        r"|(\*\*|\*)(\S(?:.*?\S)?)\7"            # *emphasis*
    )
    out, last = [], 0

    def page(label: str, name: str) -> str:
        url = public_url(name)
        return f'<a href="{escape(url)}">{escape(label)}</a>' if url else escape(label)

    for match in token.finditer(text):
        out.append(escape(text[last:match.start()]))
        if match[2]:
            out.append(page(match[1], match[2]))
        elif match[4]:
            out.append(f'<a href="{escape(match[4])}">{escape(match[3])}</a>')
        elif match[5]:
            out.append(page(link_name(match[5]), match[5]))
        elif match[6] is not None:
            out.append(escape(match[6]))
        else:
            out.append(escape(match[8]))
        last = match.end()
    out.append(escape(text[last:]))
    return "\n".join(line.strip() for line in "".join(out).split("\n"))


def section_blocks(blocks: list[tuple[int, str]], start: int, embedded) -> list[str]:
    """The text blocks beneath the block at start, with embeds expanded."""
    texts = []
    for depth, text in blocks[start + 1:]:
        if depth <= blocks[start][0]:
            break
        name = page_embed(text)
        if name:
            texts.extend(t for _, t in outline(embedded(name)) if paragraph(t))
            continue
        text = re.sub(r"^#+ ", "", text)
        if text and not text.startswith(("![", "{{")):
            texts.append(text)
    return texts


def episode_copy(body: str, path: Path, embedded=lambda name: "", public_url=lambda name: None) -> tuple[str, str, str]:
    """Return the H1 title and the episode notes as plain text and HTML.

    The notes are the whole Ceremonial Annotations section under the H1.
    Without that section, they are the first paragraph directly under the
    H1, or else the first paragraph directly under the earliest section
    heading. An embedded page, such as a ceremony's poem, supplies its own
    paragraphs; media embeds are skipped. Unpublished Notes sections are
    removed first so they never reach the feed.
    """
    blocks = outline(selected_body(body))

    def copy(title: str, texts: list[str]) -> tuple[str, str, str]:
        return (plain(title), "\n\n".join(plain(t) for t in texts),
                "".join(f"<p>{line}</p>" for t in texts
                        for line in inline_html(t, public_url).split("\n") if line))

    for index, (depth, text) in enumerate(blocks):
        match = re.match(r"^# (.+)$", text)
        if depth != 0 or not match:
            continue
        for offset, (child_depth, child) in enumerate(blocks[index + 1:], index + 1):
            if child_depth == 0:
                break
            if child_depth == 1 and re.fullmatch(r"## Ceremonial Annotations", child):
                texts = section_blocks(blocks, offset, embedded)
                if texts:
                    return copy(match[1], texts)
        under_heading = False
        for child_depth, child in blocks[index + 1:]:
            if child_depth == 0:
                break
            if child_depth == 1:
                under_heading = bool(re.match(r"#+ ", child))
            elif not (under_heading and child_depth == 2):
                continue
            name = page_embed(child)
            if name:
                child = next((text for _, text in outline(embedded(name)) if paragraph(text)), "")
            if paragraph(child):
                return copy(match[1], [child])
        break
    raise ValueError(f"{path}: expected an H1 followed by the episode description")


NOTES_LIMIT = 4000
NOTES_TAGS = {"p", "a", "ul", "ol", "li"}


def check_notes(html: str, text: str, path: Path) -> None:
    """Keep show notes inside what every podcast app documents accepting.

    Apple Podcasts allows p, ol, ul, li and a in an episode description and
    Spotify allows those too, with https links only; the Podcast Standards
    Project limits the description to 4000 characters. The plain-text summary
    carries no markup.
    """
    for tag in re.finditer(r"<(/?)([A-Za-z][A-Za-z0-9]*)([^>]*)>", html):
        name, attributes = tag[2].lower(), tag[3]
        if name not in NOTES_TAGS:
            raise ValueError(f"{path}: show notes use <{name}>, outside {sorted(NOTES_TAGS)}")
        if tag[1] or name != "a":
            if attributes.strip():
                raise ValueError(f"{path}: show notes give <{tag[1]}{name}> attributes")
        elif not re.fullmatch(r' href="https://[^"\s]+"', attributes):
            raise ValueError(f"{path}: show-notes link is not a single https href: {tag[0]}")
    if re.search(r"<[A-Za-z/!]", text):
        raise ValueError(f"{path}: plain-text summary contains markup")
    for label, value in (("show notes", html), ("summary", text)):
        if len(value) > NOTES_LIMIT:
            raise ValueError(f"{path}: {label} run to {len(value)} characters, over {NOTES_LIMIT}")


def load_episodes(garden: Path = GARDEN, probe=audio_metadata) -> list[dict]:
    episodes = []
    guids, audio_urls = set(), set()
    mounts = asset_mounts.load(garden)

    def read_with_public_links(path: Path) -> str:
        return asset_mounts.public_links(path.read_text(encoding="utf-8"), mounts, path.stem.replace("___", "/"))

    def public_url(name: str) -> str | None:
        try:
            target = page_path(garden, name)
        except ValueError:
            return None
        if not target.is_file():
            return None
        props = properties(split_page(target.read_text(encoding="utf-8"))[0])
        if props.get("public") != "true":
            return None
        return SITE_URL + page_route(props.get("title", name))

    for path in sorted((garden / "pages").glob("*.md")):
        lines, body = split_page(read_with_public_links(path))
        props = properties(lines)
        if props.get("public") != "true":
            continue
        if "[[Logseq/Entity/Podcast/Episode]]" not in props.get("logseq-entity", ""):
            continue
        guid = required(props, "podcast-guid", path)
        published = datetime.fromisoformat(required(props, "podcast-published-at", path))
        if published.tzinfo is None or published.utcoffset() is None:
            raise ValueError(f"{path}: podcast-published-at needs a timezone offset")
        title, description, description_html = episode_copy(
            body, path, lambda name: split_page(read_with_public_links(page_path(garden, name)))[1],
            public_url,
        )
        check_notes(description_html, description, path)
        # The episode recording is a direct child of its title. Chapter
        # players sit deeper in the outline and do not become RSS enclosures.
        recording_blocks = "\n".join(
            line for line in body.splitlines() if line.startswith("\t- ")
        )
        embeds = re.findall(r"\{\{embed\s+\[\[([^\]]+)\]\]\s*\}\}", recording_blocks)
        audio = re.findall(r"!\[[^\]]*\]\((https://[^)]+\.mp3)\)", recording_blocks)
        for name in embeds:
            asset_path = page_path(garden, name)
            _, asset_body = split_page(read_with_public_links(asset_path))
            audio.extend(re.findall(r"!\[[^\]]*\]\((https://[^)]+\.mp3)\)", asset_body))
        if len(audio) != 1:
            raise ValueError(f"{path}: expected one MP3 recording link")
        url = https_url({"audio_url": audio[0]}, "audio_url", path)
        if urlparse(url).query or urlparse(url).fragment:
            raise ValueError(f"{path}: audio URL must be permanent")
        if guid in guids or url in audio_urls:
            raise ValueError(f"{path}: duplicate GUID or audio URL")
        guids.add(guid)
        audio_urls.add(url)
        length, content_type = probe(url)
        page_name = path.stem.replace("___", "/")
        episodes.append({
            "episode_title": title, "description": description,
            "description_html": description_html,
            "guid": guid, "_published_at": published,
            "page_url": SITE_URL + page_route(props.get('title', page_name)),
            "audio_url": url, "audio_length": length, "audio_type": content_type,
        })
    return sorted(episodes, key=lambda episode: episode["_published_at"], reverse=True)


def render_feed(episodes: list[dict]) -> bytes:
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    def add(parent: ET.Element, tag: str, value: str) -> None:
        ET.SubElement(parent, tag).text = value

    add(channel, "title", "Ghost in the Patch")
    add(channel, "link", SITE_URL)
    ET.SubElement(channel, f"{{{ATOM}}}link", {"href": FEED_URL, "rel": "self", "type": "application/rss+xml"})
    add(channel, "language", "en-us")
    add(channel, "description", "Synth animism. Live-patching, learning, and listening for ghosts in the machine.")
    add(channel, f"{{{ITUNES}}}author", "Codekiln")
    add(channel, f"{{{ITUNES}}}summary", "Synth animism. Live-patching, learning, and listening for ghosts in the machine.")
    add(channel, f"{{{ITUNES}}}type", "episodic")
    add(channel, f"{{{ITUNES}}}explicit", "no")
    ET.SubElement(channel, f"{{{ITUNES}}}category", {"text": "Music"})
    ET.SubElement(channel, f"{{{ITUNES}}}image", {"href": ARTWORK_URL})
    image = ET.SubElement(channel, "image")
    add(image, "url", ARTWORK_URL)
    add(image, "title", "Ghost in the Patch")
    add(image, "link", SITE_URL)
    owner = ET.SubElement(channel, f"{{{ITUNES}}}owner")
    add(owner, f"{{{ITUNES}}}name", "Codekiln")
    add(owner, f"{{{ITUNES}}}email", "codekiln@pm.me")

    for episode in episodes:
        item = ET.SubElement(channel, "item")
        add(item, "title", episode["episode_title"])
        add(item, "link", episode["page_url"])
        add(item, "description", episode.get("description_html") or episode["description"])
        add(item, f"{{{ITUNES}}}author", "Codekiln")
        add(item, f"{{{ITUNES}}}summary", episode["description"])
        add(item, "pubDate", format_datetime(episode["_published_at"]))
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = episode["guid"]
        ET.SubElement(item, "enclosure", {
            "url": episode["audio_url"],
            "length": str(episode["audio_length"]),
            "type": episode["audio_type"],
        })

    ET.indent(rss)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="utf-8") + b"\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if rss.xml differs from episode pages")
    args = parser.parse_args()
    episodes = load_episodes()
    if not episodes:
        parser.error("no published episodes found")
    result = render_feed(episodes)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != result:
            parser.error("rss.xml is out of date; run mise run rss:build")
    else:
        OUTPUT.write_bytes(result)
        print(f"Wrote {OUTPUT} with {len(episodes)} episode(s)")


if __name__ == "__main__":
    main()
