import html
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from site_fixture import write_site
from build_site import PageRoutes, publish_feed
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

    def test_page_routes_read_readable_urls_and_skip_old_url_redirects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            title = 'GitP/A/Session/26/10/20-Tue'
            write_site(root, [(page_route(title), title), ('p-00000000000000aa.html', 'Guide/A\\B')])
            for path in [root / page_output(title), root / 'p-00000000000000aa.html',
                         root / 'p-00000000000000bb.html', root / 'index.html', root / 'pages.html']:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<head></head>')
            routes = PageRoutes(root)
            self.assertEqual(routes.routes['gitp/a/session/26/10/20-tue'], page_route(title))
            self.assertEqual(routes.file(page_route(title)), root / page_output(title))
            # p-00000000000000bb.html is a redirect to an old address, not a page.
            self.assertEqual(routes.documents(), sorted([
                root / page_output(title), root / 'p-00000000000000aa.html',
                root / 'index.html', root / 'pages.html']))

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
