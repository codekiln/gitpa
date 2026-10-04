"""Import a garden episode handoff into an unpublished front-of-house draft."""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ("audio_url", "audio_length", "audio_type")
REQUIRED = ("recorded_on", "episode_title", "description")


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate handoff field: {key}")
        result[key] = value
    return result


def validate_handoff(data: object) -> tuple[dict, date]:
    if not isinstance(data, dict):
        raise ValueError("Handoff must be a JSON object")
    extra = set(data) - set(REQUIRED + MEDIA)
    if extra:
        raise ValueError(f"Unsupported handoff fields: {', '.join(sorted(extra))}")
    for name in REQUIRED:
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"{name} must be a nonempty string")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["recorded_on"]):
        raise ValueError("recorded_on must use YYYY-MM-DD")
    day = date.fromisoformat(data["recorded_on"])
    if "\n" in data["episode_title"] or "\r" in data["episode_title"]:
        raise ValueError("episode_title must be a single line")
    supplied = [name in data for name in MEDIA]
    if any(supplied) and not all(supplied):
        raise ValueError("Supply audio_url, audio_length and audio_type together")
    if all(supplied):
        if not isinstance(data["audio_url"], str):
            raise ValueError("audio_url must be a permanent HTTPS URL")
        parsed = urlparse(data["audio_url"])
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or any(c.isspace() for c in data["audio_url"])):
            raise ValueError("audio_url must be a permanent HTTPS URL without credentials")
        # Validate malformed ports as well as malformed hosts.
        parsed.port
        if type(data["audio_length"]) is not int or data["audio_length"] <= 0:
            raise ValueError("audio_length must be a positive integer")
        if data["audio_type"] != "audio/mpeg":
            raise ValueError("audio_type must be audio/mpeg")
    return data, day


def page_path(garden: Path, name: object) -> Path:
    if (not isinstance(name, str) or not name or "\\" in name or name.startswith("/")
            or any(part in {"", ".", ".."} for part in name.split("/"))
            or any(c in name for c in "\n\r\0") or "___" in name):
        raise ValueError("Existing episode has an invalid page name")
    path = garden / "pages" / (name.replace("/", "___") + ".md")
    # Symlinked page paths must stay in the front garden.
    if not path.resolve().is_relative_to((garden / "pages").resolve()):
        raise ValueError("Episode page escapes the front garden")
    return path


def write_batch(changes: dict[Path, bytes], originals: dict[Path, bytes | None]) -> None:
    staged = {}
    committed = []
    try:
        for path, content in changes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".episode-import-", delete=False) as file:
                staged[path] = Path(file.name)
                file.write(content)
        for path, temporary in staged.items():
            current = path.read_bytes() if path.exists() else None
            if current != originals[path]:
                raise ValueError(f"Episode changed during import: {path}")
            os.replace(temporary, path)
            committed.append(path)
    except Exception:
        for path in reversed(committed):
            if originals[path] is None:
                path.unlink()
            else:
                path.write_bytes(originals[path])
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def import_episode(handoff: Path, root: Path = ROOT) -> tuple[Path, Path]:
    data, day = validate_handoff(json.loads(handoff.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys))
    garden = root / "gitp-garden"
    record_path = garden / "assets" / "Ceremony" / f"{day:%Y}" / f"{day:%m}" / f"{day:%d}" / "episode.yml"
    if not record_path.resolve().is_relative_to((garden / "assets").resolve()):
        raise ValueError("Episode record escapes the front garden")
    original_record = record_path.read_bytes() if record_path.exists() else None
    if original_record is None:
        record = {"published": False, "episode_title": data["episode_title"],
                  "description": data["description"], "recorded_on": day.isoformat(),
                  "page": f"Ceremony/{day:%Y/%m/%d}"}
        record.update({name: data[name] for name in MEDIA if name in data})
        new_record = yaml.safe_dump(record, sort_keys=False, allow_unicode=True).encode()
    else:
        record = yaml.safe_load(original_record.decode())
        if not isinstance(record, dict):
            raise ValueError("Existing episode record must be a YAML mapping")
        if str(record.get("recorded_on")) != day.isoformat():
            raise ValueError("Existing episode has a conflicting recorded_on date")
        additions = {}
        for name in MEDIA:
            if name not in data:
                continue
            if name in record and (type(record[name]) is not type(data[name]) or record[name] != data[name]):
                raise ValueError(f"Existing episode has conflicting {name}")
            if name not in record:
                additions[name] = data[name]
        # Preserve the existing text, comments, editorial copy and publication identity.
        new_record = original_record
        if additions:
            new_record = original_record.rstrip(b"\n") + b"\n" + yaml.safe_dump(additions, sort_keys=False).encode()
            record.update(additions)
    # Check the combined YAML before committing appended enclosure fields.
    if yaml.safe_load(new_record.decode()) != record:
        raise ValueError("Combined episode record does not match the intended metadata")
    page = page_path(garden, record.get("page"))
    original_page = page.read_bytes() if page.exists() else None
    changes = {}
    originals = {record_path: original_record, page: original_page}
    if new_record != original_record:
        changes[record_path] = new_record
    if original_page is None:
        if record.get("published") is True:
            raise ValueError("Published episode page is missing; restore the reviewed page before importing")
        title = record.get("episode_title", data["episode_title"])
        description = record.get("description", data["description"])
        if not isinstance(title, str) or not title.strip() or not isinstance(description, str) or not description.strip():
            raise ValueError("Existing episode needs title and description before creating a page")
        # Each prose paragraph stays inside its Logseq block.
        title = " ".join(title.splitlines())
        description = " ".join(description.splitlines())
        changes[page] = (f"public:: false\ndate-created:: [[{day:%Y-%m-%d %a}]]\n"
                         f"type:: [[Podcast/Episode]]\n- # {title}\n\t- {description}\n").encode()
    write_batch(changes, originals)
    return record_path, page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path, help="Episode handoff JSON from the knowledge garden")
    args = parser.parse_args()
    try:
        record, page = import_episode(args.handoff)
    except (ValueError, OSError, yaml.YAMLError) as error:
        parser.error(str(error))
    print(f"Episode record: {record}\nDraft page: {page}")


if __name__ == "__main__":
    main()
