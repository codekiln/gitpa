public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/01 Analog]]
next:: [[Ableton/Live/UG/31 Instrument Reference/01 Analog/02 Oscillators]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F01%20Analog%2F01%20Architecture%20and%20Interface
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___01%20Analog___01%20Architecture%20and%20Interface.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.1.1 Architecture and Interface](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#architecture-and-interface)
	- Two oscillators and a noise generator feed two multi-mode filters, each followed by an amplifier. The filters can run in series or in parallel.
		- ![Diagram of Analog's Signal Flow](https://ableton-production.imgix.net/live-manual/12/AnalogSignalFlow.png)
	- Two LFOs modulate oscillators, filters and amps, and each filter and amp has its own envelope.
	- The interface is a central display surrounded by the shell. The shell holds each section's main controls; the display shows the selected section's visualizations and extra controls.
	- A Global section holds volume, vibrato, polyphony and similar settings, and an MPE section maps pressure, slide and per-note pitch bend.
