public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 4]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/19 Appendix B Vocoder/08 Global Settings/03 Set Gain]]
prev:: [[Microfreak/UG/19 Appendix B Vocoder/08 Global Settings/03 Set Gain/01 Noise Gate]]
next:: [[Microfreak/UG/19 Appendix B Vocoder/08 Global Settings/03 Set Gain/03 External Sources]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F19%20Appendix%20B%20Vocoder%2F08%20Global%20Settings%2F03%20Set%20Gain%2F02%20Mic%20Detection
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Microfreak___UG___19%20Appendix%20B%20Vocoder___08%20Global%20Settings___03%20Set%20Gain___02%20Mic%20Detection.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 19.8.3.2. Mic detection
	- **On** is the default. The MicroFreak checks for a microphone whenever a vocoder preset is loaded or the Vocoder Oscillator is selected.
	- If no microphone is detected, the display warns “warning! mic needed”. The mic input is disabled until the next preset loads, and the vocoder filterbank is bypassed, leaving the raw Vocoder Oscillator sound.
	- > [[Note/Info]] Save a preset as a vocoder-type preset before editing it to keep active microphone-level monitoring.
