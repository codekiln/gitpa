public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/01 Analog]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/01 Analog/05 Amplifiers]]
next:: [[Ableton/Live/UG/31 Instrument Reference/01 Analog/07 LFOs]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F01%20Analog%2F06%20Envelopes
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___01%20Analog___06%20Envelopes.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.1.6 Envelopes](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#envelopes)
	- Besides the oscillator pitch envelopes, each filter and amp has an [[ADSR]] envelope, all four with the same controls in the display, plus velocity and looping.
		- ![Analog's Envelope Parameters](https://ableton-production.imgix.net/live-manual/12/AnalogEnvelopesL12.png)
	- **Attack**, with **Att < Vel** to shorten it at higher velocities; **Decay**; **Sustain** (fully left removes sustain, fully right removes decay); **Release**.
	- **Env < Vel** — velocity scales the whole envelope.
	- **S.Time** — lets the sustain level fall while the key is held; lower is faster.
	- **Slope** — linear or exponential segments.
	- **Legato** — a note played while another is held continues that note's envelope.
	- **Free** — skips sustain and goes straight from decay to release, so notes have equal length; suits percussion.
	- **Loop**:
		- **Off** — plays once.
		- **AD-R** — attack and decay repeat until release.
		- **ADR-R** — attack, decay and release repeat while held.
		- **ADS-R** — no looping, but attack and release play once more on key release, which can mimic audible dampers.
		- With Free on, AD-R and ADR-R act as if the key is always held.
