public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable/01 Wavetable Synthesis]]
next:: [[Ableton/Live/UG/31 Instrument Reference/13 Wavetable/03 Sub Oscillator]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F13%20Wavetable%2F02%20Oscillators
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___13%20Wavetable___02%20Oscillators.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.13.2 Oscillators](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#oscillators-2)
	- Without modulation, the raw oscillators are fully band-limited and don't alias at any pitch.
		- ![Wavetable's Oscillators](https://ableton-production.imgix.net/live-manual/12/WavetableOscillatorsL12.png)
	- Each oscillator tab has an on switch, **Gain**, **Pan**, **Semi** and **Detune**, relative to the global Transpose.
	- Two choosers pick a wavetable category and table; the arrows step through all tables across categories.
	- Drop any WAV or AIFF on the display to use it as a wavetable; the choosers then browse that file's folder. Wavetable cleans up imports unless **Raw** is on, which suits files made as wavetables or deliberately glitchy results.
		- ![Wavetable's Raw Mode Switch](https://ableton-production.imgix.net/live-manual/12/WavetableOscillatorsRawSwitchL12.png)
	- Drag in the display or use **Wave Position** to move through the table. The display is linear (waveforms stacked bottom to top, time left to right) or polar (loops from inside out, time clockwise).
	- Oscillator effects, two parameters each; values carry over when switching effect:
		- **FM** — **Amt** and **Tune**; ±50% is an octave up or down, ±100% two octaves, and values between give inharmonic, noisy overtones.
		- **Classic** — **PW** pulse width on any table, not just squares; **Sync** to a hidden oscillator.
		- **Modern** — **Warp**, similar to pulse width, and **Fold**, wavefolding.
