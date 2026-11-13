import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_site import prepare, listener_body, publication_properties

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
    def mount(self, public=True):
        line = 'public = "https://example.org/bucket"\n' if public else 'bucket = "bucket"\ndvc = "garden"\n'
        (self.source / 'asset-mounts.toml').write_text('[mounts.garden]\npath = "assets/.remote/garden"\n'
                                                       + ('source = "github.com/example/garden"\n' if public else '') + line)
    def test_mounted_links_publish_public_urls(self):
        self.mount()
        self.session('Public', True)
        (self.source / 'pages' / self.asset_file).write_text('public:: false\n- # Audio\n\t- ![Recording](../assets/.remote/garden/Full-mp3.mp3)\n')
        (self.source / 'journals').mkdir()
        (self.source / 'journals/2026_11_13.md').write_text('- ![Gate](<../assets/.remote/garden/Gate cv.png>)\n')
        (self.source / 'assets/.remote/garden').mkdir(parents=True)
        (self.source / 'assets/.remote/garden/Full-mp3.mp3').write_text('local copy')
        (self.source / 'assets/logo.png').write_text('logo')
        prepare(self.source, self.output)
        self.assertIn('![Recording](https://example.org/bucket/Full-mp3.mp3)', self.asset())
        self.assertIn('![Recording](https://example.org/bucket/Full-mp3.mp3)', (self.output / 'pages/Public.md').read_text())
        self.assertIn('(<https://example.org/bucket/Gate%20cv.png>)', (self.output / 'journals/2026_11_13.md').read_text())
        self.assertIn('../assets/.remote/garden/Full-mp3.mp3', (self.source / 'pages' / self.asset_file).read_text())
        self.assertFalse((self.output / 'assets/.remote').exists())
        self.assertTrue((self.output / 'assets/logo.png').exists())
    def test_link_into_private_or_undeclared_mount_aborts_before_copy(self):
        self.session('Public', True)
        (self.source / 'pages' / self.asset_file).write_text('public:: false\n- # Audio\n\t- ![Recording](../assets/.remote/garden/Full-mp3.mp3)\n')
        with self.assertRaisesRegex(ValueError, f'{self.name} links garden/Full-mp3.mp3.*declares no mounts.garden'):
            prepare(self.source, self.output)
        self.mount(public=False)
        with self.assertRaisesRegex(ValueError, 'mounts.garden has no public URL'):
            prepare(self.source, self.output)
        self.assertFalse(self.output.exists())
    def test_output_inside_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separate'):
            prepare(self.source, self.source / 'site')

class PresentationTests(unittest.TestCase):
    def test_proxy_removal_preserves_commas_in_entity_page_names(self):
        for value in ['[[Type,Name]], [[Logseq/Entity/Proxy/Page]]',
                      '[[Logseq/Entity/Proxy/Page]], [[Type,Name]]',
                      '[[Type,Name]], [[Logseq/Entity/Proxy/Page]], [[Other,Type]]']:
            result = publication_properties([f'logseq-entity:: {value}\n'])[0]
            self.assertIn('[[Type,Name]]', result)
            self.assertNotIn('Proxy/Page', result)
            if 'Other' in value:
                self.assertIn('[[Other,Type]]', result)

    def test_publication_properties_hide_proxy_bookkeeping_for_all_page_kinds(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            originals = {}
            for name in ['Preset', 'Definition', 'GitP___A___Session___Test___Asset___Preset___mfpz']:
                original = ('tags:: [[Music]], [[Presets]]\npublic:: true\n'
                            'logseq-entity:: [[Preset]], [[Logseq/Entity/Proxy/Page]]\n'
                            'logseq-proxy-url:: logseq://graph/source\n'
                            'logseq-proxy-codeforge-url:: https://example.com/source\n'
                            'logseq-proxy-last-sync-date:: 2026-10-24\n'
                            'preset-category:: [[Bass]]\nprev:: [[Previous]]\n'
                            'preset-synth-file:: https://example.com/preset.mfpz\n'
                            'initialized:: false\n- # Preset\n')
                path = source / 'pages' / f'{name}.md'
                path.write_text(original)
                originals[path] = original
            prepare(source, output)
            for path, original in originals.items():
                published = (output / 'pages' / path.name).read_text()
                self.assertNotIn('logseq-proxy-', published)
                self.assertNotIn('[[Logseq/Entity/Proxy/Page]]', published)
                self.assertIn('logseq-entity:: [[Preset]]\n', published)
                self.assertIn('tags:: [[Music]], [[Presets]]\n', published)
                self.assertIn('preset-category:: [[Bass]]\nprev:: [[Previous]]\n', published)
                self.assertIn('preset-synth-file:: https://example.com/preset.mfpz\n', published)
                self.assertIn('initialized:: false\n', published)
                self.assertEqual(original, path.read_text())

    def test_collapse_state_survives_preparation_without_exposing_private_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            path = source / 'pages/Episode.md'
            original = ('public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n'
                        '- # Episode\n\t- ![Recording](https://example.com/full.mp3)\n'
                        '\t- Dialogue\n\t  collapsed:: true\n\t  id:: private-editor-id\n'
                        '\t\t- Transcript\n\t- Expanded\n\t  collapsed:: false\n'
                        '\t\t- Visible note\n\t- ## Notes\n\t  collapsed:: true\n'
                        '\t\t- Private idea\n\t- ## Files\n\t\t- Download\n')
            path.write_text(original)
            prepare(source, output)
            rendered = (output / 'pages/Episode.md').read_text().split('- # Episode', 1)[1]
            self.assertIn('Dialogue\n\t  collapsed:: true\n', rendered)
            self.assertIn('Expanded\n\t  collapsed:: false\n', rendered)
            self.assertIn('Transcript', rendered)
            self.assertIn('Visible note', rendered)
            self.assertIn('Download', rendered)
            self.assertNotIn('Private idea', rendered)
            self.assertNotIn('id::', rendered)
            self.assertNotIn('public::', rendered)
            self.assertEqual(original, path.read_text())

    def test_episode_sequence_properties_survive_but_private_metadata_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            path = source / 'pages/Episode.md'
            original = ('public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n'
                        'prev:: [[Previous]]\nnext:: [[Next]]\nprivate-production-note:: secret\n'
                        '- # Episode\n')
            path.write_text(original)
            prepare(source, output)
            published = (output / 'pages/Episode.md').read_text()
            self.assertIn('prev:: [[Previous]]\nnext:: [[Next]]\n', published)
            self.assertNotIn('secret', published)
            self.assertEqual(original, path.read_text())

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
    def test_hidden_notes_do_not_publish_unused_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            name = 'GitP/A/Session/Test/Asset/Synth/Full/mp3'
            asset = source / 'pages' / (name.replace('/', '___') + '.md')
            asset.write_text('- ![Recording](https://example.com/test.mp3)\n')
            (source / 'pages/Episode.md').write_text('public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\n- # Episode\n\t- ## Notes\n\t\t- {{embed [[' + name + ']]}}\n')
            prepare(source, output)
            self.assertTrue((output / 'pages' / asset.name).read_text().startswith('public:: false\n'))
    def test_invalid_publication_aborts_before_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            (source / 'pages/Episode.md').write_text('public:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\npodcast-published-at:: 2026-01-01\n- # Episode\n')
            with self.assertRaisesRegex(ValueError, 'timezone'):
                prepare(source, output)
            self.assertFalse(output.exists())
    def test_proxy_properties_removed_from_generated_episode(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            path = source / 'pages/Episode.md'
            original = 'tags:: [[Music]]\npublic:: true\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\npodcast-published-at:: 2026-01-01T00:00:00Z\nlogseq-proxy-url:: logseq://graph/source\n- # Episode\n'
            path.write_text(original)
            prepare(source, output)
            self.assertNotIn('logseq-proxy-url', (output / 'pages/Episode.md').read_text())
            self.assertTrue((output / 'pages/Episode.md').read_text().startswith('tags:: [[Music]]\n'))
            self.assertEqual(original, path.read_text())

class BookNextTests(unittest.TestCase):
    def published(self, pages):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source', Path(directory) / 'output'
            (source / 'pages').mkdir(parents=True)
            for name, text in pages.items():
                (source / 'pages' / f'{name}.md').write_text(text)
            prepare(source, output)
            return {name: (output / 'pages' / f'{name}.md').read_text() for name in pages}
    def section(self, level, up, extra=''):
        return f'public:: true\nlogseq-entity:: [[Logseq/Entity/Book/Section/Level {level}]]\nup:: [[{up}]]\n{extra}- # Section\n'
    def pages(self):
        return {
            'B': 'public:: true\nlogseq-entity:: [[Logseq/Entity/Book]]\n- # Book\n',
            'B___1': self.section(1, 'B', 'next:: [[B/2]]\n'),
            'B___2': self.section(1, 'B', 'prev:: [[B/1]]\n'),
            'B___2___a': self.section(2, 'B/2', 'next:: [[B/2/b]]\n'),
            'B___2___b': self.section(2, 'B/2', 'prev:: [[B/2/a]]\n'),
        }
    def test_last_section_inherits_next_from_nearest_ancestor(self):
        pages = self.pages()
        pages['B___2'] = self.section(1, 'B', 'prev:: [[B/1]]\nnext:: [[B/3]]\n')
        pages['B___3'] = self.section(1, 'B')
        published = self.published(pages)
        self.assertIn('next:: [[B/3]]\n', published['B___2___b'])
        self.assertIn('prev:: [[B/2/a]]\n', published['B___2___b'])
    def test_climbs_several_levels(self):
        pages = self.pages()
        pages['B___1___x'] = self.section(2, 'B/1')
        pages['B___1___x___y'] = self.section(3, 'B/1/x')
        self.assertIn('next:: [[B/2]]\n', self.published(pages)['B___1___x___y'])
    def test_own_next_is_unchanged(self):
        published = self.published(self.pages())
        self.assertEqual(self.pages()['B___2___a'], published['B___2___a'])
    def test_final_page_of_book_has_no_next(self):
        published = self.published(self.pages())
        self.assertNotIn('next::', published['B___2___b'])
        self.assertNotIn('next::', published['B___2'])
        self.assertEqual(self.pages()['B'], published['B'])

if __name__ == '__main__':
    unittest.main()
