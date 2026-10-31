public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference]]
prev:: [[Ableton/Live/UG/29 Audio Effect Reference/12 Drum Buss]]
next:: [[Ableton/Live/UG/29 Audio Effect Reference/14 Echo]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F13%20Dynamic%20Tube
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___13%20Dynamic%20Tube.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.13 Dynamic Tube](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#dynamic-tube)
	- ![The Dynamic Tube Effect](https://ableton-production.imgix.net/live-manual/12/DynamicTubeL12.png?auto=&w=320)
	- Dynamic Tube adds tube saturation, with an envelope follower that varies the tone with input level.
	- Tube models:
		- **A** — clean at low Bias, adding bright harmonics once the input passes a threshold
		- **B** — between A and C
		- **C** — a poor tube that always distorts
	- **Tone** — moves the distortion toward the highs or down through the mids and lows
	- **Drive** — how much signal reaches the tube; more is dirtier
	- **Bias** — tube intensity; very high values make the signal break up
	- **Envelope** — lets input level move the Bias. Positive values make loud parts dirtier; negative values clean them up, an expansion effect.
	- **Attack** and **Release** — envelope response; no effect when Envelope is 0
	- **Output** — final level
	- **Hi-Quality** in the title bar's context menu reduces aliasing, especially on high frequencies, for slightly more CPU.