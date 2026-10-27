public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/03 Drift]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/03 Drift/01 Subtractive Synthesis]]
next:: [[Ableton/Live/UG/31 Instrument Reference/03 Drift/03 Filter Section]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F03%20Drift%2F02%20Oscillator%20Section
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___03%20Drift___02%20Oscillator%20Section.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.3.2 Oscillator Section](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#oscillator-section)
	- Two oscillators, pitch modulation, a waveform display, an oscillator mixer and a noise generator.
		- ![Drift's Oscillator Section](https://ableton-production.imgix.net/live-manual/12/DriftOscSectionL12.png)
	- ## 31.3.2.1 Oscillator 1
		- Waveforms: Sine, Triangle, Shark Tooth, Saturated, Saw, Pulse, Rectangle. Shark Tooth is based on a classic Moog shape; Saturated suits bass.
		- **Oct** transposes by octaves. **Shape** alters the harmonics, somewhat like pulse-width modulation, differently per waveform; the Waveform Display shows the result.
		- **Shape Mod Source** — Env 1, Env 2/Cyc, LFO, Key (more modulation for higher notes when positive), Velocity, Modwheel, Pressure or Slide, with an amount of -100% to 100%. Shape Mod can move the waveform even when Shape is 0%.
	- ## 31.3.2.2 Oscillator 2
		- Waveforms: Sine, Triangle, Saturated, Saw, Rectangle. **Oct** in octaves, **Detune** in semitones.
	- ## 31.3.2.3 Pitch Mod
		- Two sources modulate both oscillators' pitch, chosen from the same list as Shape Mod, each with -100% to 100%. An LFO in Ratio mode on pitch can produce FM tones.
	- ## 31.3.2.4 Waveform Display
		- Shows the combined output of Osc 1, Osc 2 and noise as you edit.
			- ![Drift's Waveform Display](https://ableton-production.imgix.net/live-manual/12/DriftWaveformDisplayL12.png)
	- ## 31.3.2.5 Oscillator Mixer
		- ![Drift's Oscillator Mixer](https://ableton-production.imgix.net/live-manual/12/DriftOscMixL12.png)
		- Switches and gain for Osc 1, Osc 2 and white **Noise**.
		- With filtering on, raising gain drives the filter's two saturation points, before and after the filter, for analog-style distortion: the first engages above the default -6.0 dB, the second above 0.0 dB.
		- Arrow toggles beside each gain send that source through the filter; off bypasses it.
		- **R** — Retrigger resets both oscillators' phase on each note; off lets them run free.
