public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/31 Instrument Reference/02 Collision]]
prev:: [[Ableton/Live/UG/31 Instrument Reference/02 Collision/05 LFO Tab]]
next:: [[Ableton/Live/UG/31 Instrument Reference/02 Collision/07 Sound Design Tips]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F31%20Instrument%20Reference%2F02%20Collision%2F06%20MIDI-MPE%20Tab
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___31%20Instrument%20Reference___02%20Collision___06%20MIDI-MPE%20Tab.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [31.2.6 MIDI/MPE Tab](https://www.ableton.com/en/live-manual/12/live-instrument-reference/#midimpe-tab)
	- Maps pitch bend (including per-note), mod wheel, pressure and slide to two destinations each, with amounts.
		- ![Collision's MIDI/MPE Tab](https://ableton-production.imgix.net/live-manual/12/CollisionMIDIMPEL12.png)
	- Key and Vel sliders let note pitch and velocity modulate further Mallet, Noise, resonator and LFO parameters.
	- ## 31.2.6.1 The Global Section
		- ![Collision's Global Section](https://ableton-production.imgix.net/live-manual/12/CollisionGlobalL12.png)
		- **Voices** — maximum polyphony.
		- **Retrig.** — retriggers a playing note instead of adding a voice, saving CPU.
		- **Structure** — 1 > 2 (serial): both exciters feed Resonator 1, whose mono mix also feeds Resonator 2 while Resonator 1 reaches its own mixer in stereo. 1 + 2 (parallel): the exciter mix feeds both resonators.
		- **Volume** — overall output.
