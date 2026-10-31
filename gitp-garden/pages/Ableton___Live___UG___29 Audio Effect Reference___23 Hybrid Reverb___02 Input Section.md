public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference/23 Hybrid Reverb]]
prev:: [[Ableton/Live/UG/29 Audio Effect Reference/23 Hybrid Reverb/01 Signal Flow]]
next:: [[Ableton/Live/UG/29 Audio Effect Reference/23 Hybrid Reverb/03 Convolution Reverb Engine]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F23%20Hybrid%20Reverb%2F02%20Input%20Section
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___23%20Hybrid%20Reverb___02%20Input%20Section.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.23.2 Input Section](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#input-section-1)
	- **Send** — gain into the reverb; the dry signal passes unchanged
	- **Predelay** — delay before the first early reflection. It affects how big a room sounds; natural values are about 1–25 ms. **Predelay Sync** chooses time or beat-synced values.
	- **Feedback** — predelay output fed back into its input; time and synced modes each keep their own setting
	- The main window has **Reverb** and **EQ** tabs. In the Reverb tab, **Routing** offers:
		- **Serial** — convolution feeds the algorithmic engine. **Blend** sets how much convolution goes on; 100/0 is pure convolution, 0/100 pure algorithmic fed by the convolution.
		- **Parallel** — both engines side by side; Blend sets the balance
		- **Algorithm** — only the algorithmic engine
		- **Convolution** — only the convolution engine
	- Controls for an unused engine are grayed out. Blend has no effect in Algorithm or Convolution routing.