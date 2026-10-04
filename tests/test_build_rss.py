import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_rss import load_episodes, render_feed, audio_metadata

class FeedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.garden = Path(self.tmp.name)
        (self.garden / 'pages').mkdir()
        self.page = self.garden / 'pages/GitP___A___Session___26___09___24-Thu.md'
        self.asset = self.garden / 'pages/GitP___A___Session___26___09___24-Thu___Asset___Synth___Full___mp3.md'
        self.asset.write_text('public:: true\n- # Recording\n\t- ![Listen](https://example.org/audio.mp3)\n')
        self.body = '- # A session\n\t- Music from a patch.\n\t- {{embed [[GitP/A/Session/26/09/24-Thu/Asset/Synth/Full/mp3]]}}\n'
        self.props = 'public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\npodcast-guid:: stable\npodcast-published-at:: 2026-10-04T12:00:00-04:00\n'
        self.page.write_text(self.props + self.body)
        self.probe = Mock(return_value=(1234, 'audio/mpeg'))
    def load(self):
        return load_episodes(self.garden, self.probe)
    def test_body_supplies_copy_and_asset_supplies_audio(self):
        episode = self.load()[0]
        self.assertEqual(episode['description'], 'Music from a patch.')
        self.assertEqual(episode['audio_url'], 'https://example.org/audio.mp3')
        self.assertIn(b'length="1234"', render_feed([episode]))
    def test_draft_not_probed(self):
        self.page.write_text(self.props.replace('public:: true', 'public:: false') + self.body)
        self.assertEqual(self.load(), [])
        self.probe.assert_not_called()
    def test_body_public_marker_cannot_publish(self):
        self.page.write_text(self.props.replace('public:: true\n', '') + self.body + '\t- public:: true\n')
        self.assertEqual(self.load(), [])
    def test_public_episode_requires_feed_identity(self):
        self.page.write_text('public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n' + self.body)
        with self.assertRaisesRegex(ValueError, "podcast-guid"):
            self.load()
    def test_partial_identity_fails(self):
        self.page.write_text(self.props.replace('podcast-guid:: stable\n', '') + self.body)
        with self.assertRaisesRegex(ValueError, 'podcast-guid'):
            self.load()
    def test_timezone_required(self):
        self.page.write_text(self.props.replace('T12:00:00-04:00', 'T12:00:00') + self.body)
        with self.assertRaisesRegex(ValueError, 'timezone'):
            self.load()
    def test_duplicate_guid_fails(self):
        (self.garden / 'pages/Other.md').write_text(self.props + self.body)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.load()
    def test_broken_asset_fails(self):
        self.asset.unlink()
        with self.assertRaises(FileNotFoundError):
            self.load()
    @patch('build_rss.urlopen')
    def test_head_metadata_validation(self, opener):
        response = Mock()
        response.headers = {'Content-Length': '99', 'Content-Type': 'audio/mpeg'}
        opener.return_value.__enter__.return_value = response
        self.assertEqual(audio_metadata('https://example.org/a.mp3'), (99, 'audio/mpeg'))
        self.assertEqual(opener.call_args[0][0].method, 'HEAD')
        response.headers['Content-Type'] = 'text/html'
        with self.assertRaises(ValueError):
            audio_metadata('https://example.org/a.mp3')

if __name__ == '__main__':
    unittest.main()
