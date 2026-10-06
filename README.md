# Ghost in the Patch

Episode notes and media links live in [logseq-encode-garden](https://github.com/codekiln/logseq-encode-garden). Gitpa mirrors each session under its exact page name, together with its embedded audio asset page. The website and RSS read those checked-in pages.

To refresh an episode, run `mise run episode:sync -- --source /path/to/logseq-encode-garden 'GitP/A/Session/26/09/24-Thu'`. Sync replaces the page body and preserves Gitpa's page properties. A destination page without a matching proxy URL stops the whole batch before writing. Relative assets are copied; missing source assets are reported.

To re-sync a page already mirrored here, run the garden's own task, imported into `gitp-garden/mise-tasks/`: `mise run logseq:entity:proxy:page:sync --source /path/to/logseq-encode-garden --destination gitp-garden --page 'GitP/A/Session/26/09/24-Thu' --apply`. It also brings the page's entity definitions and records what it imported in `gitp-garden/.logseq-proxy/manifest.json`. Re-running it against unchanged garden pages changes nothing except `logseq-proxy-last-sync-date::`.

Set `public:: true` on the episode page to release the episode on the website and RSS. The website build turns embedded recording and artwork pages into direct audio and image links, and labels preset and MIDI downloads. Proxy and storage properties remain in the checked-in garden; the exported listener view hides page properties. A `Notes` or `Production notes` heading publishes its children only when the heading carries `public:: true`. The website build derives asset-page visibility from public episodes; shared assets stay visible while any public episode links to them. The episode's `podcast-guid::` identifies its RSS item permanently; `podcast-published-at::` holds its publication time with a timezone offset. The RSS builder reads the title and description from the session's opening heading and paragraph, follows its embedded MP3 asset page, and gets the enclosure size from the public MP3 server. `public:: false` keeps an episode out of the website and RSS.

The November and December 2024 recordings enter the feed with this release. Their publication times record that release; their recording dates remain on the session pages. The September 2026 episodes retain their existing feed identities and publication times.

Run `mise run rss:build` and commit `rss.xml` with a publication PR. `mise run rss:check` checks the feed against the public pages and audio server; `mise run rss:test` runs offline tests. Merging a publication PR triggers the Pages workflow, which publishes the website and [podcast feed](https://codekiln.github.io/gitpa/rss.xml).

Install the staged-file guard with `lefthook install`. It uses the machine's `mise run secrets:scan` task. GitHub Actions scans the public source before publishing.

The homepage lists published episodes by publication time, newest first. Preparation normalizes publication timestamps to UTC in the temporary website graph so different timezone offsets sort chronologically. Run `mise install` and `npm ci`, then `mise run site:query:check` to test the actual query and result transform using the same Logseq file parser version as the publishing action. The check includes false and string-valued publication fixtures. PR builds upload a `gitpa-website` artifact for browser review.
