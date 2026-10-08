public:: true
logseq-entity:: [[Logseq/Entity/Proxy/Page]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Logseq%2FFrontmatter%2Ftags
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Logseq___Frontmatter___tags.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
## `tags::`- treat [[Logseq/Tags]] with care
	- Logseq tags have a special impact on the Logseq UI, but their implementation is buggy and inconsistent. In addition, the human gardener's use of `tags::` pre-dated the more mature [[Logseq/Entity]] entity system, and the human's rules for applying them are fuzzy and ill-defined. It's easier to use them incorrectly than to use them correctly.
	- As a result, their use is considered protected on existing pages: AI should not modify, add, or remove it unless explicit human instruction overrides the garden tagging rules.
	- For new pages, add `tags::` only when the relevant page-type convention explicitly requires it or nearby pages establish the same pattern.