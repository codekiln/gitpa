import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from site_fixture import write_site
from build_site import legacy_routes, prepare_homepage, public_pages, query_outline, install_homepage_query, QUERY_PLACEHOLDER


class HomepageTests(unittest.TestCase):
    def result(self):
        return {'title': ['h2', 'Recent Ceremonies'], 'view': ['ul',
                ['li', ['a', {'href': '#/page/gitp%2Fa%2Fsession%2Fnewest'}, 'GitP/A/Session/Newest']],
                ['li', ['a', {'href': '#/page/gitp%2Fa%2Fsession%2Folder'}, 'GitP/A/Session/Older']]]}

    def test_view_order_labels_and_targets_are_preserved(self):
        self.assertEqual(query_outline(self.result()),
                         '- ## Recent Ceremonies\n'
                         '\t- [[GitP/A/Session/Newest]]\n'
                         '\t- [[GitP/A/Session/Older]]\n')

    def test_unexpected_view_fails_instead_of_silently_changing_results(self):
        result = self.result()
        result['view'][1][1][1]['href'] = 'https://example.com/'
        with self.assertRaisesRegex(ValueError, 'page route'):
            query_outline(result)

    def test_replaces_query_only_in_prepared_copy(self):
        original = Path(__file__).resolve().parents[1] / 'gitp-garden/pages/Ghost in the Patch.md'
        before = original.read_text()
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory)
            (graph / 'pages').mkdir()
            home = graph / 'pages/Ghost in the Patch.md'
            home.write_text(before)
            for name in ['Newest', 'Older']:
                (graph / 'pages' / f'GitP___A___Session___{name}.md').write_text('public:: true\n- Episode\n')
            prepare_homepage(graph, self.result())
            after = home.read_text()
            self.assertNotIn('#+BEGIN_QUERY', after)
            self.assertIn('- ## Recent Ceremonies', after)
            self.assertIn(QUERY_PLACEHOLDER, after)
            self.assertIn(f'\t- {QUERY_PLACEHOLDER}\n\t  search-exclude:: true\n', after)
            self.assertNotIn('[[GitP/A/Session/Newest]]', after)
            self.assertNotIn('[[GitP/A/Session/Older]]', after)
            self.assertIn('gitp_logo_raw_fly.JPG', after)
            self.assertIn('https://codekiln.github.io/gitpa/rss.xml', after)
            self.assertEqual(original.read_text(), before)

    def test_evaluated_rows_are_inserted_only_after_authored_reference_indexing(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_site(output, [('p-aaa.html', 'Ghost in the Patch'),
                                ('p-bbb.html', 'GitP/A/Session/Newest'),
                                ('p-ccc.html', 'GitP/A/Session/Older')])
            for name in ['index.html', 'p-aaa.html']:
                (output / name).write_text('<main><a class="external-link" target="_blank" rel="noopener noreferrer" '
                                           f'href="https://codekiln.github.io/gitpa/rss.xml">podcast RSS feed</a><ul><li>{QUERY_PLACEHOLDER}</li></ul></main>')
            install_homepage_query(output, self.result())
            text = (output / 'index.html').read_text()
            self.assertIn('<a href="p-bbb.html">GitP/A/Session/Newest</a>', text)
            self.assertLess(text.index('Newest'), text.index('Older'))
            self.assertIn('data-copy-feed>Copy feed URL</button>', text)
            self.assertNotIn(QUERY_PLACEHOLDER, text)
            self.assertEqual(text, (output / 'p-aaa.html').read_text())
            with self.assertRaisesRegex(ValueError, 'placeholder'):
                install_homepage_query(output, self.result())

    def test_query_rows_preserve_shared_outline_bullets(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_site(output, [('p-aaa.html', 'Ghost in the Patch'),
                                ('p-bbb.html', 'GitP/A/Session/Newest'),
                                ('p-ccc.html', 'GitP/A/Session/Older')])
            bullet = '<a class="bullet" href="#"></a>'
            for name in ['index.html', 'p-aaa.html']:
                (output / name).write_text(f'<a href="https://codekiln.github.io/gitpa/rss.xml">podcast RSS feed</a><ul class="outline"><li>{bullet}{QUERY_PLACEHOLDER}</li></ul>')
            install_homepage_query(output, self.result())
            text = (output / 'index.html').read_text()
            self.assertEqual(text.count(bullet), 2)
            self.assertIn(f'<li>{bullet}<a href="p-bbb.html">', text)
            self.assertNotIn(QUERY_PLACEHOLDER, text)

    def test_query_result_changes_change_publication(self):
        result = self.result()
        before = query_outline(result)
        result['view'] = ['ul', result['view'][2]]
        after = query_outline(result)
        self.assertIn('Newest', before)
        self.assertNotIn('Newest', after)
        self.assertIn('Older', after)

    def test_query_cannot_publish_missing_or_private_target(self):
        for publication in [None, 'false']:
            with self.subTest(publication=publication), tempfile.TemporaryDirectory() as directory:
                graph = Path(directory)
                (graph / 'pages').mkdir()
                home = graph / 'pages/Ghost in the Patch.md'
                home.write_text('- query-table:: false\n  #+BEGIN_QUERY\n  {}\n  #+END_QUERY\n')
                if publication:
                    (graph / 'pages/GitP___A___Session___Newest.md').write_text(f'public:: {publication}\n- Private\n')
                with self.assertRaisesRegex(ValueError, 'missing or unpublished'):
                    prepare_homepage(graph, self.result())

    def test_legacy_routes_are_derived_only_from_published_index(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<head></head><body>Home</body>')
            write_site(output, [('p-abc.html', 'Ghost in the Patch'),
                                ('p-def.html', 'GitP/A/Session/Newest')])
            legacy_routes(output)
            script = (output / 'legacy-routes.js').read_text()
            self.assertIn('"gitp/a/session/newest": "p-def.html"', script)
            self.assertNotIn('private', script)
            self.assertIn('decodeURIComponent', script)
            self.assertIn('legacy-routes.js', (output / 'index.html').read_text())
            self.assertNotIn('src="legacy-routes.js"', (output / 'index.html').read_text())
            self.assertIn('window.gitpaNavigate(target, {replace: true})', script)
            self.assertIn('else location.replace(target)', script)

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

    def test_legacy_aliases_require_a_published_unambiguous_page(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            graph = output / 'graph'
            (graph / 'pages').mkdir(parents=True)
            (output / 'index.html').write_text('<head></head>')
            write_site(output, [('p-abc.html', 'Ghost in the Patch'), ('p-def.html', 'Episode')])
            (graph / 'pages/Episode.md').write_text('alias:: [[Recording]], Shared\n- Episode\n')
            (graph / 'pages/Ghost in the Patch.md').write_text('alias:: Shared\n- Home\n')
            (graph / 'pages/Private.md').write_text('alias:: Secret\n- Private\n')
            legacy_routes(output, graph)
            script = (output / 'legacy-routes.js').read_text()
            self.assertIn('"recording": "p-def.html"', script)
            self.assertNotIn('"shared":', script)
            self.assertNotIn('"secret":', script)


if __name__ == '__main__':
    unittest.main()
