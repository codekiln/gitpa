public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 4]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works/03 Vocoder Osc]]
next:: [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works/03 Vocoder Osc/02 Shape]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F19%20Appendix%20B%20Vocoder%2F02%20How%20It%20Works%2F03%20Vocoder%20Osc%2F01%20Timbre
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Microfreak___UG___19%20Appendix%20B%20Vocoder___02%20How%20It%20Works___03%20Vocoder%20Osc___01%20Timbre.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 19.2.3.1. Timbre Encoder
	- **Timbre** selects the frequency range used for analysis and resynthesis. Vowel formants peak at different frequencies: for example, a “u” may have peaks near 330 and 1260 Hz, with variation across voices.
	- Matching the range to the speaker, or to an instrument used as a modulator, helps the filters respond to the frequencies that matter. Monitoring fewer frequencies can improve response time and output.
	- Vocoder filter bands and frequency response
		- ![01 Vocoder filter bands](https://s3.us-east-005.backblazeb2.com/logseq-encode-garden/Microfreak___UG___19%20Appendix%20B%20Vocoder___02%20How%20It%20Works___03%20Vocoder%20Osc___01%20Timbre___Asset___01-Vocoder-filter-bands.png)
