public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/40 MIDI Fact Sheet]]
prev:: [[Ableton/Live/UG/40 MIDI Fact Sheet/03 Live's MIDI Solutions]]
next:: [[Ableton/Live/UG/40 MIDI Fact Sheet/05 Tips for Achieving Optimal MIDI Performance]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F40%20MIDI%20Fact%20Sheet%2F04%20Variables%20Outside%20of%20Live%27s%20Control
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___40%20MIDI%20Fact%20Sheet___04%20Variables%20Outside%20of%20Live%27s%20Control.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [40.4 Variables Outside of Live’s Control](https://www.ableton.com/en/live-manual/12/midi-fact-sheet/#variables-outside-of-lives-control)
	- Timestamps only exist inside the computer. External hardware acts on MIDI as soon as it arrives.
	- MIDI cables are serial, so a chord's notes travel one after another; dense passages can smear timing.
	- Older synths may scan their own keyboards slowly, adding jitter. Problems multiply as more devices join the chain.
	- Live has to trust incoming timestamps and the handling of outgoing events, and can verify neither.
	- ## Tests and Results
		- Input test: a MIDI source feeds a zero-latency splitter. One branch records into a MIDI clip; the other goes through a MIDI-to-audio converter into an audio clip. The offset between matching events measures Live's accuracy.
			- ![MIDI Input Test Configuration](https://ableton-production.imgix.net/live-manual/12/MIDIInTestSetup.png)
		- Ableton tested three combined audio/MIDI interfaces, A, B and C, at about 50% CPU, on macOS and Windows, at 44.1 and 96 kHz and three buffer sizes: 36 configurations.
		- Results: most jitter fell within ±1 ms on every interface. Worst cases ranged from ±4 ms (Windows, A) to ±10 ms (Windows, C at 44.1 kHz / 1024 samples) and ±11 ms (macOS, A and B at 44.1 kHz / 1152 samples). Interface C on macOS stayed within ±1 ms in every test.
		- Output tests gave results comparable to input.
			- ![MIDI Output Test Configuration](https://ableton-production.imgix.net/live-manual/12/MIDIOutTestSetup.png)
