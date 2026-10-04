from datetime import datetime
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.build_rss import ATOM, ITUNES, load_episodes, render_feed


class FeedTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.garden = Path(self.directory.name)
        (self.garden / "assets" / "Ceremony" / "2026" / "09" / "25").mkdir(parents=True)
        (self.garden / "pages").mkdir()
        (self.garden / "pages" / "Ceremony___2026___09___25.md").write_text("public:: true\n")
        self.record = self.garden / "assets" / "Ceremony" / "2026" / "09" / "25" / "episode.yml"

    def write_record(self, extra=""):
        self.record.write_text(
            "episode_title: 'Synth & Signal'\n"
            "description: 'Sounds <and> notes'\n"
            "recorded_on: '2026-09-25'\n"
            "published_at: '2026-10-03T12:00:00-04:00'\n"
            "guid: gitpa20260925\n"
            "page: Ceremony/2026/09/25\n"
            "page_url: https://example.com/episode\n"
            "audio_url: https://example.com/audio.mp3\n"
            "audio_length: 12345\n"
            "audio_type: audio/mpeg\n" + extra
        )

    def test_published_episode_renders_valid_feed(self):
        self.write_record()
        episodes = load_episodes(self.garden)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0]["_published_at"], datetime.fromisoformat("2026-10-03T12:00:00-04:00"))
        rss = ET.fromstring(render_feed(episodes))
        self.assertEqual(rss.findtext("channel/item/title"), "Synth & Signal")
        self.assertEqual(rss.findtext("channel/item/description"), "Sounds <and> notes")
        self.assertEqual(rss.find("channel/item/guid").attrib["isPermaLink"], "false")
        self.assertEqual(rss.find("channel/item/enclosure").attrib["length"], "12345")
        self.assertEqual(rss.find("channel/item/enclosure").attrib["type"], "audio/mpeg")
        self.assertEqual(rss.find(f"channel/{{{ATOM}}}link").attrib["href"], "https://codekiln.github.io/gitpa/rss.xml")
        self.assertIsNotNone(rss.find(f"channel/{{{ITUNES}}}image"))

    def test_production_record_without_page_is_not_a_feed_record(self):
        self.record.write_text("episode_title: Ceremony\nepisode_date: '2024-12-04'\n")
        self.assertEqual(load_episodes(self.garden), [])

    def test_missing_public_page_blocks_publication(self):
        self.write_record()
        (self.garden / "pages" / "Ceremony___2026___09___25.md").unlink()
        with self.assertRaisesRegex(ValueError, "episode page is missing"):
            load_episodes(self.garden)

    def test_private_page_is_excluded_without_a_second_switch(self):
        self.write_record()
        page = self.garden / "pages" / "Ceremony___2026___09___25.md"
        page.write_text("public:: false\n- Draft\n")
        self.assertEqual(load_episodes(self.garden), [])
        page.write_text("public:: true\n- Approved\n")
        self.assertEqual(len(load_episodes(self.garden)), 1)

    def test_public_marker_in_body_does_not_publish(self):
        self.write_record()
        page = self.garden / "pages" / "Ceremony___2026___09___25.md"
        page.write_text("- Example\npublic:: true\n")
        self.assertEqual(load_episodes(self.garden), [])

    def test_publication_date_needs_timezone(self):
        self.write_record()
        original = self.record.read_text()
        self.record.write_text(original.replace("2026-10-03T12:00:00-04:00", "2026-10-03T12:00:00"))
        with self.assertRaisesRegex(ValueError, "timezone offset"):
            load_episodes(self.garden)

    def test_duplicate_audio_url_is_rejected(self):
        self.write_record()
        second = self.record.parent.parent / "26" / "episode.yml"
        second.parent.mkdir()
        second.write_text(self.record.read_text().replace("gitpa20260925", "gitpa20260926"))
        with self.assertRaisesRegex(ValueError, "duplicate audio URL"):
            load_episodes(self.garden)


if __name__ == "__main__":
    unittest.main()
