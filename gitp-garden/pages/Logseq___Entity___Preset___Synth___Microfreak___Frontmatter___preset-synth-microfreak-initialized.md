public:: true
logseq-entity:: [[Logseq/Entity/Frontmatter/Definition]], [[Logseq/Entity/Proxy/Page]]
alias:: preset-synth-microfreak-initialized
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Logseq%2FEntity%2FPreset%2FSynth%2FMicrofreak%2FFrontmatter%2Fpreset-synth-microfreak-initialized
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Logseq___Entity___Preset___Synth___Microfreak___Frontmatter___preset-synth-microfreak-initialized.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # Initialized Preset
	- Owning type: [[Logseq/Entity/Preset/Synth/Microfreak]].
	- Boolean `true` or `false`: the initialization bit in the last saved header. Initialized slots are omitted from the populated preset inventory.
	- The decoded bit is `header[3] & 0x08`; see [Elektroid preset download](https://github.com/dagargo/elektroid/blob/6f3d50e2588f0236afb3510e1c55bbb292446aa2/src/connectors/microfreak.c#L322).
