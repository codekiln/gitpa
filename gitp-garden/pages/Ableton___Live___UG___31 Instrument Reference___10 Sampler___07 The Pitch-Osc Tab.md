public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler/06 The Sample Tab]]
next:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler/08 The Filter-Global Tab]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F10%20Sampler%2F07%20The%20Pitch-Osc%20Tab
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___10%20Sampler___07%20The%20Pitch-Osc%20Tab.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.10.7 The Pitch/Osc Tab](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#the-pitchosc-tab)
	- ![The Pitch/Osc Tab](https://ableton-production.imgix.net/live-manual/12/SamplerPitchTabL12.png)
	- ## 31.10.7.1 The Modulation Oscillator (Osc)
		- One modulation oscillator per voice performs **FM** or **AM** on the samples; it is never heard directly. Subsonic AM varies volume; audible AM creates composite waves.
		- 21 waveforms in **Type**, a loopable amplitude envelope with the usual levels, and:
			- **Volume** — modulation depth; **Vol < Vel** scales it with velocity.
			- **Fixed** with **Freq** × **Multi** — a constant frequency.
			- **Coarse** (0.125–48) and **Fine** (0–1000) — tuning when not fixed.
	- ## 31.10.7.2 The Pitch Envelope
		- A multi-stage envelope on the sample's pitch, and the modulation oscillator's; drag breakpoints or use sliders. **Amount** sets its range in semitones.
		- Global controls on the right:
			- **Spread** — two detuned voices per note; doubles CPU.
			- **Transp** (semitones) and **Detune** (cents).
			- **Zn Shft** — shifts which key zone plays without changing pitch, for interesting multisample artifacts.
			- **Glide** — Glide is monophonic, Portamento polyphonic; **Time** sets duration.
