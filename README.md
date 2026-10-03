# gitpa
Ghost in the Patch Alpha podcast

## Podcast feed

Published episodes have an `episode.yml` under `gitp-garden/assets/Ceremony/<year>/<month>/<day>/` and a public page under `gitp-garden/pages/`. Set `published: true` only when the episode record has its permanent GUID, publication time, public page URL, and verified MP3 enclosure URL and length. Existing records without `published: true` remain drafts.

Run `mise run rss:build` after editing an episode record and commit the resulting `rss.xml`. `mise run rss:check` verifies that the committed feed matches the records. The Pages workflow checks the feed and copies it to `https://codekiln.github.io/gitpa/rss.xml` after building the Logseq site.

Install the staged-file guard with `lefthook install`. It uses the machine's `mise run secrets:scan` task, including private identity patterns. GitHub Actions runs the checked-in Secretlint rules across the public source before publishing.
