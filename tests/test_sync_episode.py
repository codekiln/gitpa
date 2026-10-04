import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sync_episode import sync

class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source, self.dest = [Path(self.tmp.name) / name for name in ('source', 'dest')]
        for graph in (self.source, self.dest):
            (graph / 'pages').mkdir(parents=True)
        self.source_page = self.source / 'pages/Session.md'
        self.dest_page = self.dest / 'pages/Session.md'
        self.source_page.write_text('tags:: [[Music]]\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n- # Session\n\t- Description.\n')
    def run_sync(self, names=None):
        return sync(self.source, self.dest, names or ['Session'], today='2026-10-04')
    def test_create_then_resync_preserves_destination_properties(self):
        self.run_sync()
        text = self.dest_page.read_text().replace('tags:: [[Music]]', 'tags:: [[Curated]]')
        self.dest_page.write_text('public:: true\npodcast-guid:: stable\n' + text)
        self.source_page.write_text('tags:: [[Changed]]\n- # New body\n')
        self.run_sync()
        result = self.dest_page.read_text()
        self.assertIn('tags:: [[Curated]]', result)
        self.assertIn('public:: true', result)
        self.assertIn('podcast-guid:: stable', result)
        self.assertIn('[[Logseq/Entity/Proxy/Page]]', result)
        self.assertIn('- # New body', result)
        self.assertNotIn('Description.', result)
    def test_collision_aborts_entire_batch(self):
        (self.source / 'pages/Other.md').write_text('- # Other\n')
        (self.dest / 'pages/Other.md').write_text('- # Local page\n')
        with self.assertRaisesRegex(ValueError, 'collision'):
            self.run_sync(['Session', 'Other'])
        self.assertFalse(self.dest_page.exists())
    def test_recursive_embeds_and_asset_copy(self):
        self.source_page.write_text('- # Session\n\t- {{embed [[Asset]]}}\n')
        (self.source / 'pages/Asset.md').write_text('- # Asset\n\t- [Recording](../assets/music/test.mp3)\n\t- {{embed [[Session]]}}\n')
        (self.source / 'assets/music').mkdir(parents=True)
        (self.source / 'assets/music/test.mp3').write_bytes(b'audio')
        self.run_sync()
        self.assertTrue((self.dest / 'pages/Asset.md').exists())
        self.assertEqual((self.dest / 'assets/music/test.mp3').read_bytes(), b'audio')
    def test_session_download_pages_sync_without_following_notes(self):
        self.source_page.write_text("- [[GitP/A/Session/26/09/24-Thu/Asset/Preset/A/mfpz]]\n- [[Music/Log]]\n")
        (self.source / "pages/GitP___A___Session___26___09___24-Thu___Asset___Preset___A___mfpz.md").write_text("- # Patch\n")
        self.run_sync()
        asset = self.dest / "pages/GitP___A___Session___26___09___24-Thu___Asset___Preset___A___mfpz.md"
        self.assertTrue(asset.exists())
        self.assertNotIn("public::", asset.read_text())
    def test_missing_asset_reported(self):
        self.source_page.write_text('- [Absent](../assets/absent.mp3)\n')
        self.assertIn('Missing source asset', '\n'.join(self.run_sync()))
    def test_traversal_rejected_before_write(self):
        self.source_page.write_text('- [Escape](../assets/../../secret)\n')
        with self.assertRaisesRegex(ValueError, 'escapes'):
            self.run_sync()
        self.assertFalse(self.dest_page.exists())
    def test_invalid_name_rejected(self):
        with self.assertRaises(ValueError):
            self.run_sync(['../secret'])
    def test_other_graph_proxy_rejected(self):
        self.dest_page.write_text('logseq-proxy-url:: logseq://graph/other?page=Session\n- # Other\n')
        with self.assertRaisesRegex(ValueError, 'different proxy source'):
            self.run_sync()

if __name__ == '__main__':
    unittest.main()
