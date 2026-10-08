import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sync_namespace import select

class NamespaceDiscoveryTests(unittest.TestCase):
    def test_new_descendants_and_graph_wide_logical_pages_are_discovered(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'pages').mkdir(); (root / 'journals').mkdir()
            (root / 'pages/Instrument.md').write_text('- [[Instrument/Guide]]\n')
            (root / 'pages/Instrument___Guide.md').write_text('logseq-entity:: [[Logseq/Entity/Book/Section]]\n- Guide\n')
            (root / 'pages/Logseq___Entity___Book___Section.md').write_text('- [[Logseq/Frontmatter/up]]\n')
            (root / 'pages/Logseq___Entity___Book.md').write_text('- Book\n')
            (root / 'pages/Logseq___Frontmatter___up.md').write_text('- Parent\n')
            (root / 'journals/2026_10_08.md').write_text('- [[Instrument/Missing]]\n')
            _, selected, missing, _ = select(root, 'Instrument')
            self.assertIn('Logseq/Entity/Book', selected)
            self.assertIn('Logseq/Frontmatter/up', selected)
            self.assertEqual(['Instrument/Missing'], missing)
            (root / 'pages/Instrument___New.md').write_text('- New\n')
            self.assertIn('Instrument/New', select(root, 'Instrument')[1])
    def test_similar_prefix_is_not_imported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'pages').mkdir()
            (root / 'pages/Instrument.md').write_text('- [[Instrumental/Unrelated]]\n')
            (root / 'pages/Instrumental___Unrelated.md').write_text('- unrelated\n')
            self.assertEqual({'Instrument'}, select(root, 'Instrument')[1])
    def test_missing_root_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root / 'pages').mkdir()
            with self.assertRaisesRegex(ValueError, 'root'):
                select(root, 'Missing')
