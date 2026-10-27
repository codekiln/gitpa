public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference/02 Auto Filter]]
prev:: [[Ableton/Live/UG/29 Audio Effect Reference/02 Auto Filter/06 Global Controls]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F02%20Auto%20Filter%2F07%20Sidechain%20Parameters
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___02%20Auto%20Filter___07%20Sidechain%20Parameters.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.2.7 Sidechain Parameters](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#sidechain-parameters)
	- ![Auto Filter’s Sidechain Parameters](https://ableton-production.imgix.net/live-manual/12/AutoFilterSidechainL12.png?auto=&w=320)
	- ![The Sidechain Listen Toggle](https://ableton-production.imgix.net/live-manual/12/AutoFilterSidechainListenL12.png?auto=&w=320)
	- By default the envelope follower listens to Auto Filter's own input. The **Sidechain Section** toggle at the top left opens external sidechain controls.
	- **External** turns on the external sidechain; **External Source** picks the source and **External Tapping Point** picks Pre FX, Post FX or Post Mixer.
	- **Mix** — 0% uses only the internal signal, 100% only the external one
	- **SC Gain** — sidechain input level; it only affects triggering, not volume
	- **Sidechain Listen** — replaces the output with the sidechain signal for monitoring
	- **SC Filter** limits the sidechain to a frequency range, so Auto Filter reacts only to it.
		- **Sidechain Filter Frequency** sets the cutoff; **Type** is low-shelf, peak, high-shelf, low-pass, band-pass or high-pass.
		- Shelves boost or cut on one side of the cutoff to a level set by **Shelf Gain**; peak boosts or cuts around the cutoff by **Peak Gain**.
		- **Sidechain Filter Q** sets the bandwidth.
	- ### [29.2.7.1 Mono Sidechain](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#mono-sidechain)
		- The sidechain is summed to mono by default, so both channels get the same envelope. **Mono Sidechain** in the device's context menu turns that off.