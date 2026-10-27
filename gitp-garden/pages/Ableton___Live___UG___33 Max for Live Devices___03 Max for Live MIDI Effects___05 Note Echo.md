public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/33 Max for Live Devices/03 Max for Live MIDI Effects]]
prev:: [[Ableton/Live/UG/33 Max for Live Devices/03 Max for Live MIDI Effects/04 MPE Control]]
next:: [[Ableton/Live/UG/33 Max for Live Devices/03 Max for Live MIDI Effects/06 Shaper MIDI]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F33%20Max%20for%20Live%20Devices%2F03%20Max%20for%20Live%20MIDI%20Effects%2F05%20Note%20Echo
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___33%20Max%20for%20Live%20Devices___03%20Max%20for%20Live%20MIDI%20Effects___05%20Note%20Echo.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [33.3.5 Note Echo](https://www.ableton.com/en/live-manual/12/max-for-live-devices/#note-echo)
	- ![The Note Echo Effect](https://ableton-production.imgix.net/live-manual/12/MaxNoteEchoL12.png?auto=&w=320)
	- A MIDI echo: repeats each note at set intervals with falling velocity.
	- **Sync** on — the delay is chosen in 16th notes from numbered switches; 4 is one beat. The **Delay Time** percentage nudges the repeats off the grid for a drum-machine swing.
	- **Sync** off — the delay is in milliseconds; drag the Delay Time slider or type a value.
	- **Input** — **Thru** plays the original note and the echoes; **Mute** plays only the echoes.
	- **Pitch** — transposition added on each repeat
	- **Delay** — velocity of the echoes; **Fback** — how much output feeds back into the delay
	- **MPE** — echoes MPE data with the notes (otherwise it is filtered out). **Press**, **Slide** and **Note PB** then set feedback for each; below 100% the echoed MPE data fades with each repeat.