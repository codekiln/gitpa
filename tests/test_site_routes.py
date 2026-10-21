import html
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_site import package_pages, publish_feed, legacy_routes
from build_rss import ARTWORK_URL, SITE_URL
from site_routes import page_route, page_output


class PublicRoutesTests(unittest.TestCase):
    def test_namespaces_encode_each_segment_once(self):
        self.assertEqual(page_route('GitP/A/Session/26/10/20-Tue'), 'GitP/A/Session/26/10/20-Tue/')
        self.assertEqual(page_route('Microfreak/Preset/104 Wait...'), 'Microfreak/Preset/104%20Wait.../')
        title = 'Guide/Café + questions?# %2F'
        self.assertEqual(page_route(title), 'Guide/Caf%C3%A9%20%2B%20questions%3F%23%20%252F/')
        self.assertEqual(str(page_output(title)), title + '/index.html')
        for title in ['', '/Root', 'Root/', 'Root//Child', '../Root', 'Root/../Child', 'Root/./Child', 'Root\\Child']:
            with self.subTest(title=title), self.assertRaises(ValueError):
                page_route(title)

    def fixture(self, root, titles):
        links = []
        for i, title in enumerate(titles):
            route = f'p-{i:016x}.html'
            links.append(f'<a href="{route}">{html.escape(title)}</a>')
            (root / route).write_text('<head><link href="custom.css"></head><body>'
                                     f'<a href="{route}#block-abc">Self</a><a href="index.html">Home</a>'
                                     '<img src="assets/image.jpg"><audio src="https://example.com/audio.mp3"></audio></body>')
        (root / 'pages.html').write_text(''.join(links))
        (root / 'index.html').write_text('<head></head>' + ''.join(links))

    def test_packaging_preserves_titles_fragments_media_and_hash_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            title = 'GitP/A/Session/26/10/20-Tue'
            self.fixture(root, ['Ghost in the Patch', title])
            routes = package_pages(root)
            page = (root / page_output(title)).read_text()
            self.assertIn('/gitpa/GitP/A/Session/26/10/20-Tue/#block-abc', page)
            self.assertIn('href="/gitpa/custom.css"', page)
            self.assertIn('src="/gitpa/assets/image.jpg"', page)
            self.assertIn('src="https://example.com/audio.mp3"', page)
            self.assertEqual(page, (root / 'p-0000000000000001.html').read_text())
            legacy_routes(root, published_routes=routes)
            self.assertIn('GitP/A/Session/26/10/20-Tue/', (root / 'legacy-routes.js').read_text())
            self.assertNotIn('legacy-routes.js', (root / page_output(title)).read_text())

    def test_packaging_rejects_collisions_before_rewriting(self):
        for titles in [['index.html'], ['assets/Page'], ['legacy-routes.js'],
                       ['Guide/Café', 'Guide/Cafe\u0301'], ['Guide/A', 'guide/B'],
                       ['Guide', 'Guide/index.html/Child'], ['Guide/index.html/Child', 'Guide']]:
            with self.subTest(titles=titles), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, titles)
                before = (root / 'index.html').read_text()
                with self.assertRaises(ValueError):
                    package_pages(root)
                self.assertEqual(before, (root / 'index.html').read_text())

    def test_feed_targets_and_subscribed_artwork_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'source', root / 'output'
            artwork = source / 'assets/gitp/logo/gitp_logo_raw_fly.JPG'
            artwork.parent.mkdir(parents=True)
            artwork.write_bytes(b'jpeg fixture')
            output.mkdir()
            title = 'GitP/A/Session/26/10/20-Tue'
            page = output / page_output(title)
            page.parent.mkdir(parents=True)
            page.write_text('Episode')
            feed = root / 'feed.xml'
            feed.write_text(f'<rss><channel><image><url>{ARTWORK_URL}</url></image>'
                            f'<item><link>{SITE_URL + page_route(title)}</link></item></channel></rss>')
            publish_feed(source, output, feed)
            self.assertEqual((output / 'assets/gitp/logo/gitp_logo_raw_fly.JPG').read_bytes(), b'jpeg fixture')
            self.assertEqual((output / 'rss.xml').read_bytes(), feed.read_bytes())
            page.unlink()
            with self.assertRaisesRegex(ValueError, 'page is missing'):
                publish_feed(source, output, feed)


if __name__ == '__main__':
    unittest.main()
