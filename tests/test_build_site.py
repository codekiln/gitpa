import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from site_fixture import write_site
from build_site import public_pages, install_copy_feed, PLUGINS, check_property_names


class HomepageTests(unittest.TestCase):
    def test_copy_feed_button_follows_the_feed_link_on_both_homepage_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_site(output, [('p-aaa.html', 'Ghost in the Patch')])
            rows = '<ul><li><a href="p-bbb.html">GitP/A/Session/Newest</a></li></ul>'
            for name in ['index.html', 'p-aaa.html']:
                (output / name).write_text('<head></head><main><a class="external-link" target="_blank" rel="noopener noreferrer" '
                                           f'href="https://codekiln.github.io/gitpa/rss.xml">podcast RSS feed</a>{rows}</main>')
            install_copy_feed(output)
            text = (output / 'index.html').read_text()
            self.assertIn('podcast RSS feed</a> <button type="button" class="apple-podcasts-subscribe" data-copy-feed>Copy feed URL</button>', text)
            self.assertIn('<script type="module" src="/gitpa/copy-feed.js"></script></head>', text)
            # lsg renders the homepage query; this step leaves its rows alone.
            self.assertIn(rows, text)
            self.assertTrue((output / 'copy-feed.js').is_file())
            self.assertEqual(text, (output / 'p-aaa.html').read_text())

    def test_missing_feed_link_fails_the_build(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_site(output, [('p-aaa.html', 'Ghost in the Patch')])
            for name in ['index.html', 'p-aaa.html']:
                (output / name).write_text('<head></head><main></main>')
            with self.assertRaisesRegex(ValueError, 'podcast RSS feed link'):
                install_copy_feed(output)


class PublicationTests(unittest.TestCase):
    def test_public_parent_never_exposes_unmarked_child(self):
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory)
            (graph / 'pages').mkdir()
            fixtures = {'Notes': 'public:: true\n- Public\n',
                        'Notes___Private': '- PRIVATE CONTENT\n',
                        'Notes___Private___Visible': 'public:: true\n- Public grandchild\n'}
            for name, content in fixtures.items():
                (graph / 'pages' / f'{name}.md').write_text(content)
            self.assertEqual(public_pages(graph), ['Notes', 'Notes/Private/Visible'])
            self.assertEqual((graph / 'pages/Notes___Private.md').read_text(), 'public:: false\n')
            self.assertTrue((graph / 'pages/Notes___Private___Visible.md').exists())

    def test_public_page_names_decode_file_name_characters(self):
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory)
            (graph / 'pages').mkdir()
            (graph / 'pages/Recorder___Q___How do I monitor%3F.md').write_text('public:: true\n- Answer\n')
            self.assertEqual(public_pages(graph), ['Recorder/Q/How do I monitor?'])

    def test_private_ancestor_identity_survives_without_body_or_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory)
            (graph / 'pages').mkdir()
            private = graph / 'pages/Hidden.md'
            private.write_text('Public:: false\nTitle:: Root/Hidden\nalias:: PrivateAlias\n- Secret contents\n')
            (graph / 'pages/Root___Hidden___Visible.md').write_text('public:: true\n- Public\n')
            self.assertEqual(public_pages(graph), ['Root/Hidden/Visible'])
            self.assertEqual(private.read_text(), 'public:: false\ntitle:: Root/Hidden\n')
            nested = graph / 'pages/Nested.md'
            nested.write_text('- Secret\n  public:: false\n')
            public_pages(graph)
            self.assertEqual(nested.read_text(), 'public:: false\n')


class PluginTests(unittest.TestCase):
    def test_each_gitpa_plugin_manifest_names_its_module_and_id(self):
        site = Path(__file__).resolve().parents[1] / 'site'
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                manifest = json.loads((site / f'{plugin}.lsg-plugin.json').read_text())
                self.assertEqual(manifest['id'], plugin)
                module = (site / manifest['module']).read_text()
                self.assertIn(f"id: '{plugin}',", module)
                for stylesheet in manifest.get('styles', []):
                    self.assertTrue((site / stylesheet).is_file())


class PropertyNameTests(unittest.TestCase):
    def test_a_rejected_property_name_fails_the_build(self):
        diagnostics = ('pages/A.md: Unresolved or excluded page reference: B\n'
                       'pages/Logseq___Entity___Asset.md: Invalid property names: `logseq-entity\n')
        with self.assertRaisesRegex(ValueError, r'Logseq___Entity___Asset\.md: Invalid property names: `logseq-entity'):
            check_property_names(diagnostics)

    def test_other_diagnostics_leave_the_build_alone(self):
        check_property_names('pages/A.md: Unresolved or excluded page reference: B\n')


if __name__ == '__main__':
    unittest.main()
