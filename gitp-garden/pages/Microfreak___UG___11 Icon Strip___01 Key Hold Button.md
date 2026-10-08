public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/11 Icon Strip]]
next:: [[Microfreak/UG/11 Icon Strip/02 Sequencer and Arpeggiator]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F11%20Icon%20Strip%2F01%20Key%20Hold%20Button
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Microfreak___UG___11%20Icon%20Strip___01%20Key%20Hold%20Button.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 11.1 The Key Hold Button
	- Key Hold locks a key or chord so both hands are free to adjust the MicroFreak's controls.
	- > [[Note/Info]] The HOLD state is not saved with the preset.
	- The Hold Icon
		- ![01 The Hold Icon](../assets/Microfreak___UG___11-Icon-Strip___01-Key-Hold-Button___01-The-Hold-Icon.png)
	- Pressing Hold once keeps the held keys active after the fingers lift. In paraphonic mode, playing additional notes adds them to the current chord.
	- In Arp mode, Hold keeps the arpeggiated notes playing after keys are released. Turning off Arp or Hold ends them. Playing new keys replaces the notes currently playing.
	- > [[Note/Info]] Hold does not work with external MIDI. To hold external MIDI notes, send the MicroFreak a Sustain message.
	- In Sequencer mode, the Hold Icon has alternate functions.
	- The alternative functions of the Hold Icon
		- ![02 The alternative functions of the Hold Icon](../assets/Microfreak___UG___11-Icon-Strip___01-Key-Hold-Button___02-The-alternative-functions-of-the-Hold-Icon.png)
	- In Step-record mode, Hold adds a tie or silence.
	- In Real-time recording mode, Hold clears the content as the sequence records.
	- With Seq Mod, Hold clears sequence modulation; with A or B, it clears the selected sequence.
	- When the Sequencer is disabled, Hold returns to its usual Key Hold function.
	- > [[Note/Info]] Key Hold can help create a generative, self-evolving patch. Modulating pitch with independent rates from sources such as the LFO and Cycling Envelope makes the pitch change continuously without a sequencer.
