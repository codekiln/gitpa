"""Build the podcast feed from public Logseq episode proxies."""

from __future__ import annotations

import argparse
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
import re

from sync_episode import split_page, properties, page_path
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


def load_episodes(garden: Path = GARDEN, probe=audio_metadata) -> list[dict]:
    episodes = []
    guids, audio_urls = set(), set()
    for path in sorted((garden / "pages").glob("*.md")):
        lines, body = split_page(path.read_text(encoding="utf-8"))
        props = properties(lines)
        if props.get("public") != "true":
            continue
        if "[[Logseq/Entity/Podcast/Episode]]" not in props.get("logseq-entity", ""):
            continue
        guid = required(props, "podcast-guid", path)
        published = datetime.fromisoformat(required(props, "podcast-published-at", path))
        if published.tzinfo is None or published.utcoffset() is None:
            raise ValueError(f"{path}: podcast-published-at needs a timezone offset")
        heading = re.search(r"^- # ([^\n]+)\n\t- ([^\n]+)", body, re.MULTILINE)
        if not heading:
            raise ValueError(f"{path}: expected an H1 followed by the episode description")
        embeds = re.findall(r"\{\{embed\s+\[\[([^\]]+)\]\]\s*\}\}", body)
        audio = []
        for name in embeds:
            asset_path = page_path(garden, name)
            _, asset_body = split_page(asset_path.read_text(encoding="utf-8"))
            audio.extend(re.findall(r"!\[[^\]]*\]\((https://[^)]+\.mp3)\)", asset_body))
        if len(audio) != 1:
            raise ValueError(f"{path}: expected one embedded MP3 asset page")
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
            "episode_title": heading[1], "description": heading[2],
            "guid": guid, "_published_at": published,
            "page_url": SITE_URL + "#/page/" + quote(page_name, safe=""),
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
        add(item, "description", episode["description"])
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
