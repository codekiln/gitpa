public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference/02 Auto Filter]]
prev:: [[Ableton/Live/UG/29 Audio Effect Reference/02 Auto Filter/02 Filter Display]]
next:: [[Ableton/Live/UG/29 Audio Effect Reference/02 Auto Filter/04 Envelope Follower Controls]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F02%20Auto%20Filter%2F03%20LFO%20Controls
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___02%20Auto%20Filter___03%20LFO%20Controls.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.2.3 LFO Controls](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#lfo-controls)
	- ![Auto Filter’s LFO Controls](https://ableton-production.imgix.net/live-manual/12/AutoFilterLFOControlsL12.png?auto=&w=320)
	- The left and right channels each get their own LFO. **LFO Stereo Mode** sets how they differ:
		- **Phase** — same rate, offset by **LFO Phase** in degrees; 180° puts them fully opposite
		- **Spin** — the two rates are detuned by **LFO Spin** percent
		- Phase 0° or Spin 0% modulates both channels the same
	- **LFO Phase Offset** moves both LFOs' start point; it only works in synced or sixteenth time modes.
	- **LFO Quantization Mode** — **Steps** splits each cycle into **LFO Steps** stepped values; **S&H** quantizes to the beat value in **LFO S&H**.
	- **LFO Amt** — how much the LFOs move the filter, alongside or instead of the envelope
	- **Rate** — in Hz, seconds (shown as **Time**), synced divisions or sixteenths, set by **Mode**
	- **Wave** — Sine, Triangle, Saw, Square, Ramp Up, Ramp Down, Wander, S&H. Spin has no effect with Wander or S&H.
	- **Morph** reshapes the wave; with S&H it becomes **Smooth**.