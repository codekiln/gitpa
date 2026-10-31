public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/37 Sync with Link Tempo Follower and MIDI/03 Synchronizing via MIDI]]
prev:: [[Ableton/Live/UG/37 Sync with Link Tempo Follower and MIDI/03 Synchronizing via MIDI/01 Synchronizing External MIDI Devices to Live]]
next:: [[Ableton/Live/UG/37 Sync with Link Tempo Follower and MIDI/03 Synchronizing via MIDI/03 Sync Delay]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F37%20Sync%20with%20Link%20Tempo%20Follower%20and%20MIDI%2F03%20Synchronizing%20via%20MIDI%2F02%20Synchronizing%20Live%20to%20External%20MIDI%20Devices
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___37%20Sync%20with%20Link%20Tempo%20Follower%20and%20MIDI___03%20Synchronizing%20via%20MIDI___02%20Synchronizing%20Live%20to%20External%20MIDI%20Devices.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [37.3.2 Synchronizing Live to External MIDI Devices](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/#synchronizing-live-to-external-midi-devices)
	- To follow an external sequencer, set it up to send sync and enable it as a sync source in the Tempo & MIDI Settings. An **EXT** button then appears in the [[Ableton/Live/UI/Control Bar]]; turn it on, or use Options → External Sync. The upper LED beside EXT flashes when usable sync arrives.
	- Live accepts song position pointers, so it jumps when the host jumps. With [[Ableton/Live/UI/Control Bar/Toggle/Arrangement Loop]] on, positions wrap into the loop.
	- ## 37.3.2.1 MIDI Timecode Options
		- Set per MIDI device by selecting it in the MIDI Ports list of the Tempo & MIDI Settings. Both options apply only when the MIDI Sync Type is MIDI Timecode.
		- **MIDI Timecode Rate** — the SMPTE frame rate to follow. "SMPTE All" detects the format automatically. The Arrangement's display format is set separately under Options → Time Ruler Format.
		- **MIDI Timecode Offset** — a SMPTE time that Live treats as the Arrangement's start.
