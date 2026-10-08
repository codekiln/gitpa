public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/13 Sequencer]]
next:: [[Microfreak/UG/13 Sequencer/02 Mod Tracks]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F13%20Sequencer%2F01%20Use
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F204-guide-images-b2/pages/Microfreak___UG___13%20Sequencer___01%20Use.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 13.1. Using the Sequencer
	- The icon strip changes function with Arp | Seq. In arpeggiator mode, its icons control Hold, Order, Random, and Pattern. After Shift + Seq activates the sequencer, they control Tie/Rest, pattern A, pattern B, Record/Stop, and Play/Stop.
	- The Sequencer Controls
		- ![01 The Sequencer Controls](https://s3.us-east-005.backblazeb2.com/logseq-encode-garden/Microfreak___UG___13%20Sequencer___01%20Use___Asset___01-The-Sequencer-Controls.png)
	- The Sequencer Controls: Stop and Start
		- ![02 The Sequencer Controls Stop and Start](https://s3.us-east-005.backblazeb2.com/logseq-encode-garden/Microfreak___UG___13%20Sequencer___01%20Use___Asset___02-The-Sequencer-Controls-Stop-and-Start.png)
	- The Tie/Rest Icon
		- ![03 The Tie Rest Icon](https://s3.us-east-005.backblazeb2.com/logseq-encode-garden/Microfreak___UG___13%20Sequencer___01%20Use___Asset___03-The-Tie-Rest-Icon.png)
	- **Tie/Rest:** During step recording, extend a note across steps or enter silence.
	- **A and B:** Select the pattern.
	- **Record (O):** Start step recording while playback is stopped. During playback, press Record to start real-time recording.
	- **Play (>):** Start or stop playback; also ends step recording.
	- > [[Note/Info]] During playback, the MicroFreak sends MIDI and analog clock signals. Starting or stopping playback also sends MIDI start or stop messages to external sequencers.
	- A preset can contain monophonic or paraphonic patterns. In paraphonic mode, the sequencer can play up to four voices; with Paraphony off, it plays only the lowest note of each step.
	- Keyboard notes take priority over sequence notes. If you hold two keys in four-voice paraphonic mode, two voices remain for the sequence, which plays its lowest two notes. Incoming MIDI notes have the same priority as keyboard notes; sequence notes have the lowest priority.
	- > [[Note/Info]] The pitch CV output sends the lowest note in a sequence step. During keyboard playing, it sends the most recently played note.
	- MIDI sends all notes in a played chord, including velocity and aftertouch, even when the chord has more than four notes.
	- {{embed [[Microfreak/UG/13 Sequencer/01 Use/01 Select & Play]]}}
	- {{embed [[Microfreak/UG/13 Sequencer/01 Use/02 Keyboard]]}}
	- {{embed [[Microfreak/UG/13 Sequencer/01 Use/03 Record]]}}
