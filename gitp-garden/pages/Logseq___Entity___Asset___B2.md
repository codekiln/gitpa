logseq-entity:: [[Logseq/Entity/Definition]], [[Logseq/Entity/Proxy/Page]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Logseq%2FEntity%2FAsset%2FB2
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Logseq___Entity___Asset___B2.md
logseq-proxy-last-sync-date:: [[2026-10-05]]
- # Backblaze B2 Asset
	- In this garden, **Backblaze B2 Asset** pages represent files stored in Backblaze B2, following [[Logseq/Entity/Asset]] for filenames, ownership, and page contents.
	- ## Storage location
		- Upload the page-derived filename at the root of the garden's configured B2 bucket. Its optional local copy uses `assets/.remote/<filename>`.
		- For `Course/Asset/Diagram/Overview/png`, the filename is `Course___Asset___Diagram___Overview.png` and the local copy is `assets/.remote/Course___Asset___Diagram___Overview.png`.
		- The remote URL has the shape `https://<download-host>/file/<garden-bucket>/Course___Asset___Diagram___Overview.png`. The garden's B2 configuration supplies the host and bucket; URL encoding preserves the filename.
	- ## Frontmatter and body
		- `logseq-entity:: [[Logseq/Entity/Asset/B2]]` identifies the file as a B2 asset. Shared asset frontmatter and embedded media or download links follow [[Logseq/Entity/Asset]].
		- The body uses the usable remote URL. The URL already identifies the bucket and filename; separate properties would repeat them.
	- ## Uploading and backing up
		- Uploading makes a file available at its remote location. Publication through a website or podcast feed is a separate step in that site's workflow.
		- DVC maintains checksums and restoration metadata separately. A DVC push backs up a tracked file; a named B2 upload supplies the URL used by its asset page.
