public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control]]
prev:: [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control/02 Manual Control Surface Setup]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F34%20MIDI%20and%20Key%20Remote%2F01%20MIDI%20Remote%20Control%2F03%20Takeover%20Mode
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___34%20MIDI%20and%20Key%20Remote___01%20MIDI%20Remote%20Control___03%20Takeover%20Mode.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [34.1.3 Takeover Mode](https://www.ableton.com/en/live-manual/12/midi-and-key-remote-control/#takeover-mode)
	- ![MIDI Controller Takeover Mode](https://ableton-production.imgix.net/live-manual/12/MIDITakeOverMode.png?auto=&w=320)
	- Takeover Mode decides what happens when a control that sends absolute values, such as a fader, is first moved after a bank switch has pointed it at a different parameter, so the hardware and the parameter disagree.
		- **None** — the new value goes straight to the parameter, usually as a sudden jump.
		- **Pick-Up** — moving the control does nothing until it passes the parameter's current value; from then on the parameter follows the control. Smooth, but the pick-up point is hard to predict.
		- **Value Scaling** — Live compares the two values and brings the parameter toward the control smoothly as the control moves, then follows it 1:1 once they meet.