public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/19 Appendix B Vocoder/07 Config]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F19%20Appendix%20B%20Vocoder%2F07%20Config%2F01%20Preset%20Settings
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Microfreak___UG___19%20Appendix%20B%20Vocoder___07%20Config___01%20Preset%20Settings.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 19.7.1. Preset related Vocoder settings
	- Two settings under **Utility > Preset** are saved with each preset:
		- **Vocoder Hiss Mode**
		- **Vocoder Hiss Vol**
	- Older vocoders added high-frequency noise (“hiss”) to the lower, voiced “buzz” range to make consonants easier to understand.
	- ## Vocoder Hiss Mode
		- **Off:** Only the lower, vowel-like buzz range is heard.
		- **Switched:** A detector distinguishes voiced sections from unvoiced sections. During an unvoiced section, white noise replaces the carrier oscillator. Output is gated by the modulator and follows its level.
		- **Pass:** The vocoded synth signal is mixed with the part of the microphone signal above 5 kHz, allowing the high frequencies of the voice through.
	- ## Vocoder Hiss Vol
		- Sets the level of hiss mixed with the microphone signal and the white-noise replacement level in Switched mode, from -20 dB to 0 dB.
