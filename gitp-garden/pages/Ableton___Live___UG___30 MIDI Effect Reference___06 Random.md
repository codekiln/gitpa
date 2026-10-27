public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/30 MIDI Effect Reference]]
prev:: [[Ableton/Live/UG/30 MIDI Effect Reference/05 Pitch]]
next:: [[Ableton/Live/UG/30 MIDI Effect Reference/07 Scale]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F30%20MIDI%20Effect%20Reference%2F06%20Random
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___30%20MIDI%20Effect%20Reference___06%20Random.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [30.6 Random](https://www.ableton.com/en/live-manual/12/live-midi-effect-reference/#random)
	- ![The Random Effect](https://ableton-production.imgix.net/live-manual/12/RandomL12.png?auto=&w=230)
	- Random changes the pitch of incoming notes at random.
	- **Chance** is how likely each note is to be changed, like a dry/wet for randomness.
	- **Choices** (1–24) and **Interval** multiply to give the spread of possible pitches above, below or around the played note. With Chance 50%, Choices 1 and Interval 12, repeated C3s play C3 or C4. With Choices 12 and Interval 1, they play C3 or any note from C#3 to C4. (Both examples use Random mode and Add.)
	- **Mode**:
		- **Random** — pitches in no order
		- **Alt** — steps through the possible pitches in a fixed cycle. Chance 100% always moves to the next pitch; 0% always plays the incoming note. With Choices 12 and Interval 1, repeated C3s climb a semitone at a time to C4 and start over; with Choices 2 and Interval 2, they alternate C3 and D3 — useful for up-bow/down-bow or left/right hand samples.
	- **Sign**:
		- **Add** — only higher pitches
		- **Sub** — only lower pitches
		- **Bi** — either
	- LEDs beside Chance flash **+**, **0** or **-** for a higher, unchanged or lower note.
	- **Use Current Scale** in the title bar keeps random pitches in the clip's scale. Alt mode with a scale works like a simple, unpredictable step sequencer.