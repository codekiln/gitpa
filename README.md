# gitpa
Ghost in the Patch Alpha podcast

## Podcast feed

Published episodes have an `episode.yml` under `gitp-garden/assets/Ceremony/<year>/<month>/<day>/` and a public page under `gitp-garden/pages/`. Set `published: true` only when the episode record has its permanent GUID, publication time, public page URL, and verified MP3 enclosure URL and length. Existing records without `published: true` remain drafts.

Run `mise run rss:build` after editing an episode record and commit the resulting `rss.xml`. `mise run rss:check` verifies that the committed feed matches the records. The Pages workflow checks the feed and copies it to `https://codekiln.github.io/gitpa/rss.xml` after building the Logseq site.

To start an episode from an Ableton export, prepare its MP3 with the garden's `gitpa:media:prepare` task, then run `mise run episode:draft -- '/path/to/GitP26.09.24 Project'`. The draft task finds the matching public garden session page, reads track names from the Ableton set, and creates an unpublished `episode.yml`, editable Logseq page, and sourced `session-note.md`. It leaves existing descriptions and pages alone. Add `--transcribe` to run local MLX Whisper on a matching commentary stem; repetitive speech recognition output is flagged and excluded from the description. Review the note and recording before uploading and publishing.

Install the staged-file guard with `lefthook install`. It uses the machine's `mise run secrets:scan` task, including private identity patterns. GitHub Actions runs the checked-in Secretlint rules across the public source before publishing.
