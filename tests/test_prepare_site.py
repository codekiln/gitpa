import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_site import prepare, listener_body

class VisibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'source'
        (self.source / 'pages').mkdir(parents=True)
        self.output = Path(self.tmp.name) / 'site'
        self.name = 'GitP/A/Session/26/09/24-Thu/Asset/Synth/Full/mp3'
        self.asset_file = self.name.replace('/', '___') + '.md'
        (self.source / 'pages' / self.asset_file).write_text('public:: false\n- # Audio\n\t- ![Recording](https://example.com/audio.mp3)\n')
    def session(self, name, public):
        (self.source / 'pages' / f'{name}.md').write_text(f'public:: {str(public).lower()}\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n- # Session\n\t- {{{{embed [[{self.name}]]}}}}\n')
    def asset(self):
        return (self.output / 'pages' / self.asset_file).read_text()
    def test_public_episode_exposes_asset_in_generated_graph_only(self):
        self.session('Public', True)
        prepare(self.source, self.output)
        self.assertIn('public:: true', self.asset())
        self.assertIn('public:: false', (self.source / 'pages' / self.asset_file).read_text())
    def test_draft_hides_previously_public_asset(self):
        self.session('Draft', False)
        (self.source / 'pages' / self.asset_file).write_text('public:: true\n- # Audio\n')
        prepare(self.source, self.output)
        self.assertIn('public:: false', self.asset())
    def test_shared_asset_visible_if_any_parent_public(self):
        self.session('Draft', False)
        self.session('Public', True)
        prepare(self.source, self.output)
        self.assertIn('public:: true', self.asset())
    def test_download_links_expose_assets(self):
        self.session('Public', True)
        session = self.source / 'pages/Public.md'
        session.write_text(session.read_text().replace('{{embed ', '').replace('}}', ''))
        prepare(self.source, self.output)
        self.assertIn('public:: true', self.asset())
    def test_missing_asset_aborts_before_copy(self):
        self.session('Public', True)
        (self.source / 'pages' / self.asset_file).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing linked asset'):
            prepare(self.source, self.output)
        self.assertFalse(self.output.exists())
    def test_output_inside_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separate'):
            prepare(self.source, self.source / 'site')

class PresentationTests(unittest.TestCase):
    def test_media_and_downloads_use_direct_links(self):
        root = 'GitP/A/Session/24/11/19-Tue/Asset/'
        names = [root + 'Synth/Full/mp3', root + 'Artwork/Overview/gif', root + 'Preset/A/mfpz', root + 'MIDI/Microfreak/mid']
        pages = {name: ([], f'- ![Media](https://example.com/file.{name.split("/")[-1]})\n') for name in names}
        body = ''.join(f'- {{{{embed [[{name}]]}}}}\n' for name in names)
        rendered = listener_body('Episode', body, pages)
        self.assertIn('![Media](https://example.com/file.mp3)', rendered)
        self.assertIn('![Media](https://example.com/file.gif)', rendered)
        self.assertIn('[MicroFreak preset A](https://example.com/file.mfpz)', rendered)
        self.assertIn('[Microfreak MIDI](https://example.com/file.mid)', rendered)
        self.assertNotIn('{{embed', rendered)
    def test_only_selected_notes_survive(self):
        body = '- # Episode\n\t- ## Notes\n\t\t- Private idea\n\t- ## Files\n\t\t- Download\n'
        self.assertNotIn('Private idea', listener_body('Episode', body, {}))
        self.assertIn('Download', listener_body('Episode', body, {}))
        body = body.replace('## Notes\n', '## Notes\n\t  public:: true\n')
        rendered = listener_body('Episode', body, {})
        self.assertIn('Private idea', rendered)
        self.assertNotIn('public::', rendered)
    def test_excluded_notes_do_not_resolve_embeds(self):
        body = '- # Episode\n\t- ## Notes\n\t\t- {{embed [[Missing/Page]]}}\n'
        self.assertEqual('- # Episode\n', listener_body('Episode', body, {}))
    def test_proxy_properties_removed_from_generated_episode(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            path = source / 'pages/Episode.md'
            original = 'public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\npodcast-published-at:: 2026-01-01T00:00:00Z\nlogseq-proxy-url:: logseq://graph/source\n- # Episode\n'
            path.write_text(original)
            prepare(source, output)
            self.assertNotIn('logseq-proxy-url', (output / 'pages/Episode.md').read_text())
            self.assertEqual(original, path.read_text())

if __name__ == '__main__':
    unittest.main()
