public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference]]
prev:: [[Ableton/Live/UG/29 Audio Effect Reference/17 Erosion]]
next:: [[Ableton/Live/UG/29 Audio Effect Reference/19 Filter Delay]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F18%20External%20Audio%20Effect
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___18%20External%20Audio%20Effect.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.18 External Audio Effect](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#external-audio-effect)
	- ![The External Audio Effect](https://ableton-production.imgix.net/live-manual/12/ExternalAudioEffectL12.png?auto=&w=292)
	- External Audio Effect brings a hardware effects unit into a track's device chain.
	- **Audio To** — audio interface outputs feeding the hardware; **Audio From** — inputs bringing it back. "Configure…" at the bottom of each chooser opens the Audio Settings.
	- **Peak** indicators under each chooser hold the highest level; click to reset.
	- **Gain** knobs — send and return levels; set them to avoid clipping in the hardware and on the way back in
	- **Dry/Wet** — set to 100% on a return track
	- **Invert** — flips the phase of the returning signal
	- **Hardware Latency** — manual compensation for the hardware's delay, which Live cannot detect.
		- Use **samples** for digital connections, so the value holds when the sample rate changes; use **ms** for analog connections.
		- Samples are finer, so analog setups can be fine-tuned in samples — then switch back to ms before changing sample rate.
		- Disabled when Delay Compensation is off in the Options menu.
		- The Knowledge Base article "Driver Error Compensation FAQ" explains how to measure it.