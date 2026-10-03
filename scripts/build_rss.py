"""Build the published podcast feed from episode.yml records."""

from __future__ import annotations

import argparse
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import yaml


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


def load_episodes(garden: Path = GARDEN) -> list[dict]:
    episodes = []
    guids = set()
    audio_urls = set()
    for path in sorted((garden / "assets").rglob("episode.yml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError(f"{path}: expected a YAML mapping")
        if record.get("published") is not True:
            continue

        for name in ("episode_title", "description", "recorded_on", "guid", "page"):
            required(record, name, path)
        for name in ("audio_url", "page_url"):
            https_url(record, name, path)
        if urlparse(record["audio_url"]).query or urlparse(record["audio_url"]).fragment:
            raise ValueError(f"{path}: audio_url must be a permanent public URL")
        if record.get("audio_type") != "audio/mpeg":
            raise ValueError(f"{path}: audio_type must be audio/mpeg")
        if type(record.get("audio_length")) is not int or record["audio_length"] <= 0:
            raise ValueError(f"{path}: audio_length must be a positive integer")
        try:
            datetime.strptime(record["recorded_on"], "%Y-%m-%d")
            published_at = datetime.fromisoformat(required(record, "published_at", path))
        except ValueError as error:
            raise ValueError(f"{path}: invalid recording or publication date: {error}") from error
        if published_at.tzinfo is None or published_at.utcoffset() is None:
            raise ValueError(f"{path}: published_at needs a timezone offset")

        page_name = record["page"]
        if page_name.startswith("/") or ".." in page_name.split("/"):
            raise ValueError(f"{path}: invalid page name")
        page_path = garden / "pages" / (page_name.replace("/", "___") + ".md")
        if not page_path.is_file() or "public:: true" not in page_path.read_text(encoding="utf-8").splitlines()[:5]:
            raise ValueError(f"{path}: public episode page is missing: {page_path}")
        if record["guid"] in guids:
            raise ValueError(f"{path}: duplicate GUID {record['guid']}")
        if record["audio_url"] in audio_urls:
            raise ValueError(f"{path}: duplicate audio URL {record['audio_url']}")
        guids.add(record["guid"])
        audio_urls.add(record["audio_url"])
        record["_published_at"] = published_at
        episodes.append(record)

    episodes.sort(key=lambda episode: episode["_published_at"], reverse=True)
    return episodes


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
    parser.add_argument("--check", action="store_true", help="Fail if rss.xml differs from episode records")
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
