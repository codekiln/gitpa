public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/40 MIDI Fact Sheet]]
prev:: [[Ableton/Live/UG/40 MIDI Fact Sheet/02 MIDI Timing Problems]]
next:: [[Ableton/Live/UG/40 MIDI Fact Sheet/04 Variables Outside of Live's Control]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F40%20MIDI%20Fact%20Sheet%2F03%20Live%27s%20MIDI%20Solutions
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___40%20MIDI%20Fact%20Sheet___03%20Live%27s%20MIDI%20Solutions.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [40.3 Live’s MIDI Solutions](https://www.ableton.com/en/live-manual/12/midi-fact-sheet/#lives-midi-solutions)
	- Ableton works from two assumptions: latency is better than jitter, because it is predictable, and when playing through while recording you want to record what you hear, even if that is slightly later than what you played.
	- **Recording** — the MIDI interface driver timestamps each event on arrival, and Live places the event in the clip by that timestamp.
	- **Playthrough** — Live delays events by a constant amount rather than playing them whenever the busy system gets to them. With monitoring on, it adds a delay based on the audio buffer size, so notes land in the clip where you heard them.
	- **Playback to hardware** — Live sends timestamps for the driver to schedule outgoing events. Windows MME drivers cannot use timestamps, so Live schedules those events itself.
	- During audio dropouts Live still receives and records MIDI correctly, even if playthrough sounds wrong; playback is accurate once the system recovers.
