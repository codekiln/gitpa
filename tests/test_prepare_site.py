import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_site import prepare

class VisibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'source'
        (self.source / 'pages').mkdir(parents=True)
        self.output = Path(self.tmp.name) / 'site'
        self.name = 'GitP/A/Session/26/09/24-Thu/Asset/Synth/Full/mp3'
        self.asset_file = self.name.replace('/', '___') + '.md'
        (self.source / 'pages' / self.asset_file).write_text('public:: false\n- # Audio\n')
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

if __name__ == '__main__':
    unittest.main()
