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
            (root / 'pages/Logseq___Entity___Book.md').write_text('- [[Logseq/Entity/Book/Frontmatter/title]]\n')
            (root / 'pages/Logseq___Entity___Book___Frontmatter___title.md').write_text('- Title\n')
            (root / 'pages/Logseq___Frontmatter___up.md').write_text('- Parent\n')
            (root / 'journals/2026_10_08.md').write_text('- [[Instrument/Missing]]\n')
            _, selected, missing, _ = select(root, 'Instrument')
            self.assertIn('Logseq/Entity/Book', selected)
            self.assertIn('Logseq/Entity/Book/Frontmatter/title', selected)
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

class NamespacePlannerTests(unittest.TestCase):
    def fixture(self, root):
        import shutil
        source, dest = root / 'source', root / 'destination'
        for graph in (source, dest):
            (graph / 'pages').mkdir(parents=True); (graph / 'logseq').mkdir()
        library=source/'mise-tasks/logseq/entity/proxy/page/lib';library.mkdir(parents=True)
        bundled=Path(__file__).resolve().parents[1]/'gitp-garden/mise-tasks/logseq/entity/proxy/page/lib'
        for name in ('core.py','task_imports.py'):
            shutil.copyfile(bundled/name,library/name)
        (source/'pages/Instrument___Guide%3A question%3F.md').write_text('- Encoded heading\n')
        (source/'mise-tasks/fixture').write_text('original task\n'); (source/'mise-tasks/fixture').chmod(0o755)
        content={
            'Instrument': 'logseq-entity:: [[Logseq/Entity/Book]]\n- Instrument\n',
            'Logseq___Entity___Book': 'entity-tasks:: [[Task]]\n- Book\n',
            'Logseq___Entity___Proxy___Page': 'entity-proxy-destination-properties:: public\n- Proxy\n',
            'Task': 'task-owner:: source\ntask-config-root:: .\nsource-link:: https://example.com/task\ntask-entrypoint:: mise-tasks/fixture\ntask-name:: fixture\ntask-files:: {"mise-tasks/fixture":"mise-tasks/fixture"}\n- Task\n'}
        for name,text in content.items(): (source/'pages'/f'{name}.md').write_text(text)
        return source,dest
    def test_repeat_and_local_task_conflict_are_atomic(self):
        from sync_namespace import plan_namespace
        with tempfile.TemporaryDirectory() as folder:
            source,dest=self.fixture(Path(folder))
            core,plan,_=plan_namespace(source,dest,'Instrument');core.apply_plan(plan)
            self.assertTrue((dest/'pages/Instrument___Guide%3A question%3F.md').is_file())
            page=dest/'pages/Instrument.md'
            page.write_text(page.read_text().replace('public:: true','public:: false'))
            before={str(p):p.read_bytes() for p in dest.rglob('*') if p.is_file()}
            core,repeat,_=plan_namespace(source,dest,'Instrument');core.apply_plan(repeat)
            self.assertEqual(before,{str(p):p.read_bytes() for p in dest.rglob('*') if p.is_file()})
            (dest/'mise-tasks/fixture').write_text('local task edit\n')
            (source/'pages/Instrument___New.md').write_text('- New\n')
            with self.assertRaisesRegex(ValueError,'edit|conflict'):
                plan_namespace(source,dest,'Instrument')
            self.assertFalse((dest/'pages/Instrument___New.md').exists())
    def test_page_collision_rejects_the_batch(self):
        from sync_namespace import plan_namespace
        with tempfile.TemporaryDirectory() as folder:
            source,dest=self.fixture(Path(folder))
            (source/'pages/Instrument___New.md').write_text('- source\n')
            (dest/'pages/Instrument___New.md').write_text('- local\n')
            with self.assertRaisesRegex(ValueError,'proxy|collision'):
                plan_namespace(source,dest,'Instrument')
            self.assertFalse((dest/'pages/Instrument.md').exists())
