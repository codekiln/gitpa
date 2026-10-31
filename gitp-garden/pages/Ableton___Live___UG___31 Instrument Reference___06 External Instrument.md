public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/05 Electric]]
next:: [[Ableton/Live/UG/31 Instrument Reference/07 Impulse]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F06%20External%20Instrument
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___06%20External%20Instrument.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.6 External Instrument](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#external-instrument)
	- A routing utility, not a sound source: it sends MIDI to a hardware synth or a multitimbral plug-in and brings its audio back.
		- ![The External Instrument](https://ableton-production.imgix.net/live-manual/12/ExternalInstrumentL12.png)
	- **MIDI To** — two choosers. The first picks a MIDI port or a track holding a multitimbral plug-in; the second picks the MIDI channel.
	- **Audio From** — for hardware, the audio interface inputs wired to the synth's outputs, as set in the Audio Settings; for a plug-in, its auxiliary outputs. Main outputs play on the plug-in's own track.
	- **Gain** — level of the returning audio; set it to avoid clipping.
	- **Hardware Latency** — manual delay compensation for the external device, in ms or samples. Use samples for digital connections so the count survives sample-rate changes, ms for analog ones; samples allow finer tuning, but switch back to ms before changing sample rate. Disabled for internal routing, which is compensated automatically, and when Options → Delay Compensation is off.
	- Routing details: [[Ableton/Live/UG/17 Routing and IO]]. Related: [[Ableton/How To/Record MIDI and Audio from external device]]
