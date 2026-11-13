"""Ableton Set pages reach Gardener's ableton-set plugin with what it reads.

The plugin ships inside lsg and draws the track view; its own tests cover the view. These
tests cover Gitpa's side: preparation keeps the Set's embeds, the entity types and the
settings under each track's heading, a track that is not public stays out, and the
checked-in Set pages publish every track they embed.
"""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import public_pages
from logseq_page import page_name, properties, split_page
from prepare_site import prepare

SET_TYPE = '[[Logseq/Entity/Ableton/Set]]'
TRACK_TYPES = ('[[Logseq/Entity/Ableton/Track/Group]]', '[[Logseq/Entity/Ableton/Track/Track]]')
EMBED = re.compile(r'\{\{embed \[\[([^\]]+)\]\]\}\}')
PROXY = ('logseq-proxy-url:: logseq://graph/source?page=x\n'
         'logseq-proxy-codeforge-url:: https://example.org/x.md\n'
         'logseq-proxy-last-sync-date:: [[2026-11-13]]\n')
# A Set with a group, a track inside the group and a track outside any group.
PAGES = {
    'Show/Set': ('Set', True, '- # Evening Set\n  live-version:: 11.3.43\n  tempo:: 96\n  time-signature:: 4/4\n'
                 '\t- {{embed [[Show/Set/Track/Synths]]}}\n\t- {{embed [[Show/Set/Track/Commentary]]}}\n'
                 '\t- {{embed [[Show/Set/Track/Draft]]}}\n'),
    'Show/Set/Track/Synths': ('Track/Group', True, '- # Synths\n  type:: group\n  audio-to:: AudioOut/Master\n'
                              '\t- {{embed [[Show/Set/Track/Synths/MicroFreak MIDI]]}}\n'),
    'Show/Set/Track/Synths/MicroFreak MIDI': (
        'Track/Track', True, '- # MicroFreak MIDI\n  type:: midi\n  midi-from:: MidiIn/External.Dev:Launchpad Pro MK3/0\n'
        '  midi-to:: MidiOut/External.Dev:Arturia MicroFreak/0\n  midi-channel:: 1\n  monitor:: auto\n  arm:: true\n'
        '\t- Carries the sequencer\'s notes.\n'),
    'Show/Set/Track/Commentary': (
        'Track/Track', True, '- # Commentary\n  type:: audio\n  audio-from:: AudioIn/External/S0\n'
        '  audio-to:: AudioOut/Master\n  monitor:: off\n  arm:: false\n  devices:: Compressor, EQ Eight, Limiter\n'),
    'Show/Set/Track/Draft': ('Track/Track', False, '- # DRAFT_TRACK\n  type:: audio\n'),
}


def write_page(graph, name, entity, public, body):
    release = f'logseq-entity:: [[Logseq/Entity/Ableton/{entity}]], [[Logseq/Entity/Proxy/Page]]\n'
    if public:
        release += 'public:: true\n'
    (graph / 'pages' / (name.replace('/', '___') + '.md')).write_text(release + PROXY + '\n' + body, encoding='utf-8')


class PreparedSetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        source = Path(self.tmp.name) / 'source'
        (source / 'pages').mkdir(parents=True)
        for name, (entity, public, body) in PAGES.items():
            write_page(source, name, entity, public, body)
        self.graph = prepare(source, Path(self.tmp.name) / 'graph')
        self.public = public_pages(self.graph)

    def page(self, name):
        return (self.graph / 'pages' / (name.replace('/', '___') + '.md')).read_text(encoding='utf-8')

    def test_set_group_and_tracks_are_selected_for_publication(self):
        self.assertEqual(sorted(self.public), [
            'Show/Set', 'Show/Set/Track/Commentary', 'Show/Set/Track/Synths',
            'Show/Set/Track/Synths/MicroFreak MIDI'])

    def test_prepared_pages_keep_what_the_plugin_reads(self):
        for name, (entity, public, body) in PAGES.items():
            if not public:
                continue
            release, prepared = split_page(self.page(name))
            # The entity type, without the proxy marker and bookkeeping.
            self.assertEqual(properties(release), {
                'logseq-entity': f'[[Logseq/Entity/Ableton/{entity}]]', 'public': 'true'}, name)
            # The heading, its settings and the embeds, as written.
            self.assertEqual(prepared.lstrip('\n'), body, name)

    def test_track_that_is_not_public_is_withheld(self):
        self.assertEqual(self.page('Show/Set/Track/Draft'), 'public:: false\n')
        for path in (self.graph / 'pages').glob('*.md'):
            if page_name(path) != 'Show/Set/Track/Draft':
                self.assertNotIn('DRAFT_TRACK', path.read_text(encoding='utf-8'), path.name)


class CheckedInSetTests(unittest.TestCase):
    def setUp(self):
        self.pages = {}
        for path in (ROOT / 'gitp-garden/pages').glob('*.md'):
            release, body = split_page(path.read_text(encoding='utf-8'))
            self.pages[page_name(path)] = (properties(release), body)

    def tracks(self, name, seen=()):
        """Every page a Set or group embeds, following groups."""
        found = []
        for embedded in EMBED.findall(self.pages[name][1]):
            self.assertIn(embedded, self.pages, f'{name} embeds a page that is not checked in')
            self.assertNotIn(embedded, seen, f'{name} embeds itself or its Set')
            found.append(embedded)
            if TRACK_TYPES[0] in self.pages[embedded][0].get('logseq-entity', ''):
                found.extend(self.tracks(embedded, (*seen, name)))
        return found

    def test_plugin_is_turned_on(self):
        config = (ROOT / 'gitp-garden/logseq/config.edn').read_text(encoding='utf-8')
        active = [line for line in config.splitlines() if line.strip().startswith(':lsg/plugins')]
        self.assertEqual(len(active), 1)
        self.assertIn(':ableton-set', active[0])

    def test_public_set_publishes_every_track_it_embeds(self):
        sets = [name for name, (props, _) in self.pages.items()
                if SET_TYPE in props.get('logseq-entity', '') and props.get('public') == 'true']
        self.assertIn('GitP/A/Session/26/11/06-Fri/Set', sets)
        for name in sets:
            tracks = self.tracks(name)
            self.assertTrue(tracks, f'{name} embeds no track')
            for track in tracks:
                props, body = self.pages[track]
                self.assertEqual(props.get('public'), 'true', f'{track} is embedded by {name} and is not public')
                self.assertTrue(any(kind in props.get('logseq-entity', '') for kind in TRACK_TYPES), track)
                self.assertRegex(body, r'(?m)^- # .+\n  type:: \S+', track)

    def test_public_set_is_linked_from_its_public_episode(self):
        props, body = self.pages['GitP/A/Session/26/11/06-Fri']
        self.assertEqual(props.get('public'), 'true')
        self.assertIn('[[GitP/A/Session/26/11/06-Fri/Set]]', body)


if __name__ == '__main__':
    unittest.main()
