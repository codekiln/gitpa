"""Exercise source publication choices through the imported sync and both publishers."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_rss import load_episodes
from logseq_page import split_page, properties
from prepare_site import prepare


class SourcePublicationTests(unittest.TestCase):
    def test_source_selection_replaces_downstream_choice_for_feed_and_website(self):
        with tempfile.TemporaryDirectory() as directory:
            source, downstream = Path(directory) / 'source', Path(directory) / 'downstream'
            for graph in (source, downstream):
                (graph / 'pages').mkdir(parents=True)
                (graph / 'logseq').mkdir()
            (source / 'pages/Logseq___Entity___Proxy___Page.md').write_text(
                'entity-proxy-destination-properties:: public\n- # Proxy Page\n')
            (source / 'pages/Logseq___Entity___Podcast___Episode.md').write_text(
                'entity-proxy-destination-properties:: podcast-guid, podcast-published-at\n- # Episode\n')
            (source / 'pages/Logseq___Entity___Podcast___Episode___GitP___A.md').write_text(
                'entity-proxy-source-properties:: public\n- # GitP Alpha Episode\n')
            page = 'GitP/A/Session/Example'
            filename = page.replace('/', '___') + '.md'
            membership = ('logseq-entity:: [[Logseq/Entity/Podcast/Episode/GitP/A]], '
                          '[[Logseq/Entity/Podcast/Episode]]\n')
            body = '- # Test session\n\t- Test description.\n\t- ![Recording](https://example.com/audio.mp3)\n'
            script = ROOT / 'gitp-garden/mise-tasks/logseq/entity/proxy/page/sync'
            def sync(value):
                flag = '' if value is None else f'public:: {value}\n'
                (source / 'pages' / filename).write_text(flag + membership + body)
                subprocess.run([sys.executable, str(script), '--source', str(source),
                                '--destination', str(downstream), '--page', page, '--apply'],
                               check=True, capture_output=True, text=True)
            sync('true')
            target = downstream / 'pages' / filename
            release = 'podcast-guid:: stable\npodcast-published-at:: 2026-01-01T00:00:00Z\n'
            target.write_text(release + target.read_text())
            for index, value in enumerate(('false', 'true', None, 'invalid')):
                with self.subTest(value=value):
                    sync(value)
                    props = properties(split_page(target.read_text())[0])
                    self.assertEqual(props.get('public'), value)
                    self.assertEqual(props['podcast-guid'], 'stable')
                    self.assertEqual(props['podcast-published-at'], '2026-01-01T00:00:00Z')
                    episodes = load_episodes(downstream, probe=lambda _: (100, 'audio/mpeg'))
                    self.assertEqual(bool(episodes), value == 'true')
                    output = Path(directory) / f'site-{index}'
                    prepare(downstream, output)
                    site_props = properties(split_page((output / 'pages' / filename).read_text())[0])
                    self.assertEqual(site_props.get('public') == 'true', value == 'true')


if __name__ == '__main__':
    unittest.main()
