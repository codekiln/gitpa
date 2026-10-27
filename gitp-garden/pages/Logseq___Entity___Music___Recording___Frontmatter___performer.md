public:: true
logseq-entity:: [[Logseq/Entity/Frontmatter/Definition]], [[Logseq/Entity/Proxy/Page]]
alias:: [[performer]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Logseq%2FEntity%2FMusic%2FRecording%2FFrontmatter%2Fperformer
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Logseq___Entity___Music___Recording___Frontmatter___performer.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # `performer::` — who plays on a recording
	- The known people or groups who perform on a [[Logseq/Entity/Music/Recording]]. Published artist identities are recorded separately through [[Logseq/Frontmatter/created-by-identities]]; when present, its first identity supplies the recording namespace.
	- ## Values
		- One or more comma-separated links to person pages (`Person/<Name>`) or group pages (`Group/<Name>`), as `performer:: [[Group/Beak]]`.
		- Record performers whose participation on this recording is known. Session-player details and instruments belong in the page body; identity membership alone does not establish participation.
	- ## Other entities that use it
		- [[Logseq/Entity/Music/Performance]] uses `performer::` with the same values for the people and groups who played at the event.
