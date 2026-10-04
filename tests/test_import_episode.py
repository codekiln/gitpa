import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.import_episode import import_episode


class ImportEpisodeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.handoff = self.root / 'handoff.json'
        self.data = {'recorded_on': '2026-09-24', 'episode_title': 'A synth session',
                     'description': 'FM: "bells" and a Launchpad.'}
        self.record = self.root / 'gitp-garden/assets/Ceremony/2026/09/24/episode.yml'
        self.page = self.root / 'gitp-garden/pages/Ceremony___2026___09___24.md'

    def run_import(self):
        self.handoff.write_text(json.dumps(self.data))
        return import_episode(self.handoff, self.root)

    def media(self):
        self.data.update(audio_url='https://example.com/episode.mp3', audio_length=1234,
                         audio_type='audio/mpeg')

    def test_creates_unpublished_record_and_valid_lfm(self):
        self.data['description'] += '\n- More listening notes.'
        self.run_import()
        record = yaml.safe_load(self.record.read_text())
        self.assertNotIn('published', record)
        self.assertEqual(record['description'], self.data['description'])
        self.assertNotIn('guid', record)
        self.assertIn('public:: false', self.page.read_text())
        self.assertNotIn('\n\n', self.page.read_text())
        self.assertNotIn('\n- More listening notes.', self.page.read_text())

    def test_repeat_preserves_front_copy_page_and_publication_identity(self):
        self.run_import()
        self.record.write_text("# Human note\nepisode_title: Final title\n"
                               "description: Final copy\nrecorded_on: '2026-09-24'\n"
                               "guid: permanent-guid\npublished_at: '2026-10-01T12:00:00-04:00'\n"
                               "page: Custom/Episode\npage_url: https://example.com/episode\n")
        custom = self.root / 'gitp-garden/pages/Custom___Episode.md'
        custom.write_text('public:: true\n- My edited episode page\n')
        original_record = self.record.read_bytes()
        original_page = custom.read_bytes()
        self.data['description'] = 'New source description'
        self.run_import()
        self.assertEqual(self.record.read_bytes(), original_record)
        self.assertEqual(custom.read_bytes(), original_page)

    def test_adds_verified_media_without_rewriting_comments_or_copy(self):
        self.run_import()
        original = '# My comment\n' + self.record.read_text()
        self.record.write_text(original)
        self.media()
        self.run_import()
        self.assertTrue(self.record.read_text().startswith(original))
        record = yaml.safe_load(self.record.read_text())
        self.assertEqual(record['audio_length'], 1234)
        unchanged = self.record.read_bytes()
        self.run_import()
        self.assertEqual(self.record.read_bytes(), unchanged)

    def test_conflicting_media_rejected_before_missing_page_is_created(self):
        self.media()
        self.run_import()
        self.page.unlink()
        original = self.record.read_bytes()
        for name, value in [('audio_url', 'https://example.com/new.mp3'),
                            ('audio_length', 999), ('audio_type', 'audio/wav')]:
            with self.subTest(name=name):
                old = self.data[name]
                self.data[name] = value
                with self.assertRaises(ValueError):
                    self.run_import()
                self.assertEqual(self.record.read_bytes(), original)
                self.assertFalse(self.page.exists())
                self.data[name] = old

    def test_validation_failure_creates_no_output(self):
        for update in [{'published': True}, {'guid': 'override'}, {'page': '../../escape'},
                       {'recorded_on': '2026-02-30'}, {'recorded_on': '2026-9-24'},
                       {'episode_title': 'Title\n- Injected block'}, {'description': ''},
                       {'audio_url': 'https://example.com/a.mp3'}]:
            with self.subTest(update=update):
                original = self.data.copy()
                self.data.update(update)
                with self.assertRaises(ValueError):
                    self.run_import()
                self.assertFalse(self.record.exists())
                self.assertFalse(self.page.exists())
                self.data = original

    def test_invalid_enclosure_creates_no_output(self):
        self.media()
        for name, value in [('audio_length', True), ('audio_length', 0), ('audio_type', 'text/plain'),
                            ('audio_url', 'http://example.com/a.mp3'),
                            ('audio_url', ('https://' + 'fixture-user' + ':' + 'fixture-pass' + '@example.com/a.mp3')),
                            ('audio_url', 'https://example.com/a.mp3?token=temporary'),
                            ('audio_url', 'https://example.com:bad/a.mp3')]:
            with self.subTest(name=name, value=value):
                old = self.data[name]
                self.data[name] = value
                with self.assertRaises(ValueError):
                    self.run_import()
                self.assertFalse(self.record.exists())
                self.data[name] = old

    def test_conflicting_recording_date_preserves_existing_files(self):
        self.run_import()
        self.record.write_text(self.record.read_text().replace('2026-09-24', '2026-09-25'))
        before = self.record.read_bytes()
        with self.assertRaises(ValueError):
            self.run_import()
        self.assertEqual(self.record.read_bytes(), before)

    def test_invalid_existing_page_does_not_append_media(self):
        self.run_import()
        self.record.write_text(self.record.read_text().replace('Ceremony/2026/09/24', '../escape'))
        before = self.record.read_bytes()
        self.media()
        with self.assertRaises(ValueError):
            self.run_import()
        self.assertEqual(self.record.read_bytes(), before)

    def test_published_missing_page_does_not_gain_a_private_draft(self):
        self.run_import()
        self.record.write_text(self.record.read_text() + 'guid: existing-episode\n')
        self.page.unlink()
        self.media()
        before = self.record.read_bytes()
        with self.assertRaises(ValueError):
            self.run_import()
        self.assertEqual(self.record.read_bytes(), before)
        self.assertFalse(self.page.exists())

    def test_duplicate_json_key_rejected(self):
        self.handoff.write_text('{"recorded_on":"2026-09-24","recorded_on":"2026-09-25"}')
        with self.assertRaises(ValueError):
            import_episode(self.handoff, self.root)
        self.assertFalse(self.record.exists())

    def test_second_write_failure_rolls_back_first(self):
        original_replace = os.replace
        def fail_page(source, target):
            if target == self.page:
                raise OSError('Simulated page write failure')
            return original_replace(source, target)
        with patch('scripts.import_episode.os.replace', side_effect=fail_page):
            with self.assertRaises(OSError):
                self.run_import()
        self.assertFalse(self.record.exists())
        self.assertFalse(self.page.exists())
        self.assertEqual(list(self.root.rglob('.episode-import-*')), [])


if __name__ == '__main__':
    unittest.main()
