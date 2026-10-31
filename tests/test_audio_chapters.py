from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audio_chapters import compile_episode, timestamp_seconds
from build_site import install_episode_player

FULL = 'https://example.com/recording.mp3'
HEADER = f'- # Episode\n\t- ![Full recording]({FULL})\n\t- ## Chapters\n'


class AudioChapterTests(unittest.TestCase):
    def test_timestamp_forms_are_strict(self):
        for value, expected in [('0', 0), ('882', 882), ('14:42', 882), ('90:00', 5400), ('1:02:03', 3723)]:
            self.assertEqual(timestamp_seconds(value), expected)
        for value in ['', '-1', '1.5', '14:2', '1:60', '1:2:03', '1:60:03', '1:00:60', ' 2', '2 extra']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                timestamp_seconds(value)

    def test_macro_and_existing_heading_ranges_seek_full_recording(self):
        original = HEADER + '\t\t- ### {{audio-timestamp 14:42}} Adapters\n\t\t- ### 00:00–03:30 · Opening\n'
        text, recording = compile_episode(original)
        self.assertEqual(recording, FULL)
        self.assertIn(f'### [14:42]({FULL}#t=882) Adapters', text)
        self.assertIn(f'### [00:00]({FULL}#t=0)–03:30 · Opening', text)
        self.assertIn('{{audio-timestamp', original)
        self.assertNotIn('{{audio-timestamp', text)

    def test_integer_macro_gets_readable_time_and_spaces_indent_works(self):
        original = HEADER.replace('\t', '  ') + '    - ### {{audio-timestamp 882}} Adapters\n'
        text, _ = compile_episode(original)
        self.assertIn(f'[14:42]({FULL}#t=882)', text)

    def test_subheading_timestamps_seek_and_preserve_parent_chapter_media_scope(self):
        original = HEADER + ('\t\t- ### 00:00 Opening\n'
            '\t\t\t- #### 03:07 Nested [[Link]]\n'
            '\t\t\t\t- ##### 04:12–05:00 Detail\n'
            '\t\t\t\t\t- ###### 1:02:03 Deep detail\n'
            '\t\t\t- ![Waveform](https://example.com/recording___0000-0540.png)\n'
            '\t\t- #### 06:01 Sibling\n')
        text, _ = compile_episode(original)
        for heading, value, seconds in [('####', '03:07', 187), ('#####', '04:12', 252),
                                         ('######', '1:02:03', 3723), ('####', '06:01', 361)]:
            self.assertIn(f'{heading} [{value}]({FULL}#t={seconds})', text)
        self.assertIn('–05:00 Detail', text)
        self.assertNotIn('recording___0000-0540.png', text)

    def test_published_halloween_episode_subheading_timestamp(self):
        episode = Path(__file__).resolve().parents[1] / 'gitp-garden/pages/GitP___A___Session___26___10___29-Thu.md'
        text, recording = compile_episode(episode.read_text())
        self.assertIn(f'#### [03:07]({recording}#t=187) secondo strato', text)

    def test_fenced_and_inline_code_stays_literal(self):
        for fence in ['~~~', '```']:
            example = (f'\t\t- {fence}markdown\n'
                       f'\t\t  - {fence}\n'
                       '\t- ![Literal recording](https://example.com/sample.mp3)\n'
                       '\t\t  - ### 14:42 Literal heading\n'
                       '\t\t  {{audio-timestamp nope}}\n'
                       '\t\t  {{audio-timestamp 62}}\n'
                       f'\t\t  {fence}\n')
            inline = '\t\t- `{{audio-timestamp nope}}` and ``{{audio-timestamp 62}}`` with {{audio-timestamp 62}}\n'
            text, _ = compile_episode(HEADER + example + inline)
            self.assertIn(example, text)
            self.assertIn('`{{audio-timestamp nope}}` and ``{{audio-timestamp 62}}``', text)
            self.assertIn(f'with [1:02]({FULL}#t=62)', text)

    def test_only_matching_derived_chapter_media_are_removed_and_notes_survive(self):
        original = HEADER + ('\t\t- ### 14:42 Adapters\n'
                    '\t\t\t- ![Waveform](https://example.com/recording___1442-2418.png)\n'
                    '\t\t\t\t- ![Chapter](https://example.com/recording___1442-2418.mp3)\n'
                    '\t\t\t\t\t- A nested observation\n'
                    '\t\t\t\t\t  note:: Keep this\n'
                    '\t\t\t\t- ![Unrelated art](https://example.com/artwork.png)\n'
                    '\t\t\t- ![Other recording](https://elsewhere.com/recording___1442-2418.mp3)\n'
                    '\t- ## Other media\n'
                    '\t\t- ![Outside chapter](https://example.com/recording___1442-2418.png)\n')
        text, _ = compile_episode(original)
        chapter = text.split('\t- ## Other media')[0]
        self.assertNotIn('https://example.com/recording___1442-2418.mp3', chapter)
        self.assertNotIn('https://example.com/recording___1442-2418.png', chapter)
        self.assertIn('\t\t\t- A nested observation\n\t\t\t  note:: Keep this', text)
        self.assertIn('\t\t\t- ![Unrelated art]', text)
        self.assertIn('https://elsewhere.com/recording___1442-2418.mp3', text)
        self.assertIn('![Outside chapter]', text)

    def test_macro_requires_one_full_recording_and_invalid_macro_fails(self):
        for text in ['- ### {{audio-timestamp 10}} Start\n',
                     HEADER + '\t\t- ### {{audio-timestamp 9:99}} Bad\n',
                     HEADER + '\t\t- ### {{audio-timestamp}} Bad\n',
                     HEADER + '\t\t- ### {{audio-timestamp 10 Bad\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                compile_episode(text)

    def test_obsolete_waveform_instructions_change_only_in_prepared_text(self):
        original = HEADER + '\t- Chapter waveforms show synth above commentary; each chapter player combines both.\n'
        text, _ = compile_episode(original)
        self.assertIn('Select a chapter timestamp', text)
        self.assertIn('Chapter waveforms', original)

    def test_shell_loads_everywhere_but_only_episodes_have_recording_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'pages.html').write_text('<head></head><body><a href="p-abc.html">Episode</a><a href="p-def.html">Asset</a></body>')
            (root / 'p-abc.html').write_text(f'<head></head><body><audio src="{FULL}"></audio></body>')
            (root / 'p-def.html').write_text(f'<head></head><body><audio src="{FULL}"></audio></body>')
            install_episode_player(root, {'episode': FULL})
            text = (root / 'p-abc.html').read_text()
            self.assertIn('/gitpa/player.js', text)
            self.assertIn('/gitpa/player.css', text)
            self.assertIn('player.js', (root / 'p-def.html').read_text())
            self.assertIn('player.js', (root / 'pages.html').read_text())
            self.assertIn('name="gitpa-episode"', text)
            self.assertIn('rel="canonical" href="/gitpa/Episode/"', text)
            self.assertNotIn('name="gitpa-episode"', (root / 'p-def.html').read_text())
            self.assertEqual(text.count('<audio'), 1)
            self.assertTrue((root / 'player.js').is_file())
            (root / 'p-abc.html').write_text(f'<head></head><audio src="{FULL}"></audio><audio src="{FULL}"></audio>')
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                install_episode_player(root, {'episode': FULL})


if __name__ == '__main__':
    unittest.main()
