import json
from datetime import date
from pathlib import Path
import tempfile
import unittest

from scripts.draft_session_note import (
    description_from_note,
    explicit_description,
    find_note,
    note_facts,
    transcript_quality,
    update_empty_description,
)


class DraftSessionNoteTests(unittest.TestCase):
    def test_logseq_manual_link_supports_fm_description(self):
        with tempfile.TemporaryDirectory() as temporary:
            note = Path(temporary) / "session.md"
            note.write_text(
                "- # [[GitP/Session/26/09/24 Thu]] with Microfreak and Launchpad\n"
                "\t- On the [[Microfreak]], started with [[Microfreak/UG/06 Dig Osc/03 Types/08 Two Op.FM]] on initialized patch.\n",
                encoding="utf-8",
            )
            devices, detail = note_facts(note)
            self.assertEqual(
                description_from_note(devices, detail),
                "A MicroFreak and Launchpad session beginning with two-operator FM on an initialized patch.",
            )

    def test_repeated_asr_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            transcript = Path(temporary) / "transcript.json"
            transcript.write_text(
                json.dumps({"segments": [{"text": "Thank you."}] * 25 + [{"text": "This is weird."}]}),
                encoding="utf-8",
            )
            self.assertFalse(transcript_quality(transcript)[0])

    def test_note_discovery_uses_contents_when_filename_lacks_gitpa(self):
        with tempfile.TemporaryDirectory() as temporary:
            pages = Path(temporary) / "pages"
            pages.mkdir()
            note = pages / "Music___Composition___Log___26___09___25 Fri.md"
            note.write_text("- Podcast title: GitP.26.09.25\n\t- Description: A synth session.\n", encoding="utf-8")
            self.assertEqual(find_note(Path(temporary), date(2026, 9, 25), None), note)
            self.assertEqual(explicit_description(note), "A synth session.")

    def test_draft_never_overwrites_a_written_description(self):
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / "episode.yml"
            record.write_text("published: false\ndescription: 'My own copy'\n", encoding="utf-8")
            self.assertFalse(update_empty_description(record, "Generated copy"))
            self.assertIn("My own copy", record.read_text(encoding="utf-8"))

    def test_new_record_is_unpublished(self):
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / "2026" / "09" / "24" / "episode.yml"
            record.parent.mkdir(parents=True)
            self.assertTrue(update_empty_description(record, "A session."))
            content = record.read_text(encoding="utf-8")
            self.assertIn("published: false", content)
            self.assertIn('description: "A session."', content)


if __name__ == "__main__":
    unittest.main()
