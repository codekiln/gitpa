import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from link_asset_mounts import LinkError, link

MOUNTS = '''[mounts.garden]
path   = "assets/.remote/garden"
public = "https://example.com/garden"
source = "github.com/example/garden"
'''


class LinkTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.garden = self.root / 'gitp-garden'
        self.garden.mkdir()
        (self.garden / 'asset-mounts.toml').write_text(MOUNTS)
        self.source = self.root / 'source'
        self.files = self.source / 'assets/.remote/garden'
        self.files.mkdir(parents=True)
        (self.files / 'Image.png').write_text('png')
        self.link_path = self.garden / 'assets/.remote/garden'

    def locate(self, address):
        self.assertEqual(address, 'github.com/example/garden')
        return self.source

    def test_links_borrowed_mount_to_source_checkout(self):
        self.assertEqual(link(self.garden, self.locate), [f'garden: linked {self.link_path} to {self.files}'])
        self.assertEqual((self.link_path / 'Image.png').read_text(), 'png')

    def test_leaves_existing_link_alone(self):
        link(self.garden, self.locate)
        self.assertIn('already links', link(self.garden, self.locate)[0])

    def test_stops_on_folder_in_the_way(self):
        self.link_path.mkdir(parents=True)
        with self.assertRaisesRegex(LinkError, 'is not a link'):
            link(self.garden, self.locate)

    def test_stops_when_source_has_no_mount_folder(self):
        (self.files / 'Image.png').unlink()
        self.files.rmdir()
        with self.assertRaisesRegex(LinkError, 'asset:fetch'):
            link(self.garden, self.locate)

    def test_skips_owned_mounts(self):
        (self.garden / 'asset-mounts.toml').write_text('[mounts.own]\npath = "assets/.remote/own"\nbucket = "b"\ndvc = "d"\n')
        self.assertEqual(link(self.garden, self.locate), [])

    def test_garden_without_mount_file_links_nothing(self):
        (self.garden / 'asset-mounts.toml').unlink()
        self.assertEqual(link(self.garden, self.locate), [])


if __name__ == '__main__':
    unittest.main()
