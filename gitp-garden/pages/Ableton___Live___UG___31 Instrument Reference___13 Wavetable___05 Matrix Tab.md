public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable/04 Filters]]
next:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable/06 Mod Sources Tab]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F13%20Wavetable%2F05%20Matrix%20Tab
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___13%20Wavetable___05%20Matrix%20Tab.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.13.5 Matrix Tab](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#matrix-tab-1)
	- Routes internal sources (envelopes, LFOs) across the top to targets down the side; drag in a cell to set the amount.
		- ![Wavetable's Matrix Tab](https://ableton-production.imgix.net/live-manual/12/WavetableMatrixTabL12.png)
	- **Additive** targets sum their sources and add the result to the parameter; neutral is 0, and sources can be bipolar (negative and positive) or unipolar (positive only).
	- **Multiplicative** targets multiply their sources together and then with the parameter; neutral is 1 and minimum 0. The manual marks which parameters work this way.
	- Click a parameter to show it in the matrix; it stays only if modulated. Matrix and MIDI tabs share rows. Click a source header to jump to it in Mod Sources.
	- **Time** — scales every modulator; negative is faster. Modulating Time doesn't affect the modulator doing it. **Amount** — overall depth; multiplicative.
