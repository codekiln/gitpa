public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler/07 The Pitch-Osc Tab]]
next:: [[Ableton/Live/UG/31 Instrument Reference/10 Sampler/09 The Modulation Tab]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F10%20Sampler%2F08%20The%20Filter-Global%20Tab
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___10%20Sampler___08%20The%20Filter-Global%20Tab.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.10.8 The Filter/Global Tab](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#the-filterglobal-tab)
	- ![The Filter/Global Tab](https://ableton-production.imgix.net/live-manual/12/SamplerFilterTabL12.png)
	- ## 31.10.8.1 The Filter
		- A polyphonic filter with the same types and Cytomic circuits as Operator: low-pass, high-pass, band-pass, notch and Morph at 12 or 24 dB, with Clean, OSR, MS2, SMP and PRD circuits. See [[Ableton/Live/UG/31 Instrument Reference/09 Operator/05 Filter Section]].
		- **Frequency**, **Resonance**, **Drive** on non-Clean low-, high- and band-pass, and **Morph** for the Morph type.
		- **F. Env** — a filter envelope with levels, ADSR, loop and slopes; its **Amount** must be non-zero to act.
		- **Shaper** — Soft, Hard, Sine or 4bit, with Amount. An arrow sets whether it comes before or after the filter.
	- ## 31.10.8.2 The Volume Envelope and Global Controls
		- The global [[ADSR]] volume envelope. Loop and Trigger restart from Initial if a note outlasts Decay, taking **Time** to return; Beat and Sync restart after **Repeat**.
		- **Pan** and **Pan < Rnd**; **Time** scales every envelope; **Time < Key** scales them by pitch.
		- **Voices** up to 32. **R** retriggers playing notes instead of adding voices, saving CPU with long releases played quickly.
