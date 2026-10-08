public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/19 Appendix B Vocoder]]
prev:: [[Microfreak/UG/19 Appendix B Vocoder/01 Intro]]
next:: [[Microfreak/UG/19 Appendix B Vocoder/03 Connect Mic]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F19%20Appendix%20B%20Vocoder%2F02%20How%20It%20Works
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F204-guide-images-b2/pages/Microfreak___UG___19%20Appendix%20B%20Vocoder___02%20How%20It%20Works.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 19.2. How Does Vocoder Work?
	- The MicroFreak analyzes incoming sound with 16 tuned bandpass filters. As with the MicroFreak's own filter in BPF mode, each band emphasizes a limited range of frequencies.
	- An envelope follower tracks the loudness in each band. The resulting signals control matching filters on the carrier, allowing each formant peak to follow its own changing volume. The vocoder also recreates the overall loudness pattern at the end of the signal path.
	- MicroFreak Vocoder signal path
		- ![01 Vocoder signal path](https://s3.us-east-005.backblazeb2.com/logseq-encode-garden/Microfreak___UG___19%20Appendix%20B%20Vocoder___02%20How%20It%20Works___Asset___01-Vocoder-signal-path.png)
	- {{embed [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works/01 Resolution]]}}
	- {{embed [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works/02 Voice]]}}
	- {{embed [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works/03 Vocoder Osc]]}}
