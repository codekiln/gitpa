public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/09 Envelope Gen]]
prev:: [[Microfreak/UG/09 Envelope Gen/06 Cycling Envelope]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F09%20Envelope%20Gen%2F07%20Cycling%20Envelope%20Suggestions
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Microfreak___UG___09%20Envelope%20Gen___07%20Cycling%20Envelope%20Suggestions.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 09.7 Freaky Cycling Envelope Suggestions
	- Use the Matrix to modulate the Cycling Envelope's Rise, Hold, and Fall with the LFO or pressure. Pressure gives direct control over the Rise and Fall stages.
	- Matrix modulation can be positive or negative. A negative signal to Fall shortens the Fall stage as pressure increases.
	- Amount controls how strongly the Cycling Envelope affects its destinations. Adjust it carefully, especially when modulating the analog filter. A control that reduces signal strength is an attenuator.
	- The Matrix can combine the Cycling Envelope with stages of the Main Envelope. For example, modulating Attack changes its slope; modulating Decay changes its length. Further Matrix routings can build longer modulation chains.
	- Patch ideas:
		- Use a slow sine LFO to control Cycling Envelope Rise, then use CycEnv to control Main Envelope Sustain.
		- Use a random LFO to control Cycling Envelope Amount, then use CycEnv to control Main Envelope Decay/Release or Sustain.
