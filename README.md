# gitpa
Ghost in the Patch Alpha podcast

## Podcast feed

Published episodes have an `episode.yml` under `gitp-garden/assets/Ceremony/<year>/<month>/<day>/` and a public page under `gitp-garden/pages/`. Set `public:: true` on the episode page when its RSS record has a permanent GUID, publication time, public page URL, and verified MP3 enclosure URL and length. This page property is the single publication switch for both the website and RSS; pages with `public:: false` remain drafts.

Run `mise run rss:build` after editing an episode record and commit the resulting `rss.xml`. `mise run rss:check` verifies that the committed feed matches the records. The Pages workflow checks the feed and copies it to `https://codekiln.github.io/gitpa/rss.xml` after building the Logseq site.

Production notes, Ableton inspection, transcription and media preparation live in [logseq-encode-garden](https://github.com/codekiln/logseq-encode-garden). The garden's `gitpa:episode:draft` task prepares a handoff JSON file; import that file with `mise run episode:import -- '/path/to/episode-handoff.json'`.

The handoff contains `recorded_on` (YYYY-MM-DD), `episode_title` and `description`. Optional verified media metadata must include `audio_url`, `audio_length` and `audio_type` together. The importer creates an unpublished `episode.yml` and a Logseq draft page, preserves existing editorial copy, page content and publication identity, and rejects conflicting enclosure metadata before writing. Repeated imports leave existing copy untouched. Unknown fields, including `published`, `guid` and `page`, are rejected; `gitpa` owns the final copy, page, GUID and publication time. Review the description and verify the public MP3 before preparing a release PR with `public:: true` on the episode page. Merging that PR publishes the episode through CI.

Install the staged-file guard with `lefthook install`. It uses the machine's `mise run secrets:scan` task, including private identity patterns. GitHub Actions runs the checked-in Secretlint rules across the public source before publishing.
