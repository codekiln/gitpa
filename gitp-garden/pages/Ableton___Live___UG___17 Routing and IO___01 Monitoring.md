public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/17 Routing and IO]]
next:: [[Ableton/Live/UG/17 Routing and IO/02 External Audio In-Out]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F17%20Routing%20and%20IO%2F01%20Monitoring
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___17%20Routing%20and%20IO___01%20Monitoring.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [17.1 Monitoring](https://www.ableton.com/en/live-manual/12/routing-and-i-o/#monitoring)
	- Monitoring passes a track's input to its output through the device chain, so you hear what you play, with effects and interface latency.
	- Each audio and MIDI track has three monitor modes:
		- **Auto** ([[Ableton/Track/IO/Monitor/Auto]]) — monitors while the track is armed, but not while it plays clips. Suits most recording.
		- **In** — always monitors the input and silences the track's clips, turning it into an aux-style input. The track's Activator switch turns blue to show it.
		- **Off** ([[Ableton/Track/IO/Monitor/Off]]) — never monitors. For acoustic instruments heard in the room, an external mixer, or an interface's direct monitoring. Set Overall Latency in the Audio Settings when recording this way.
	- With In or Auto, **Keep Monitoring Latency in Recorded Audio** is on by default, lining the recording up with what you heard. Leave it on for software instruments and effects; turn it off for acoustic instruments or external monitoring. Right-click the In or Auto button to switch it.
	- Clicking a Monitor button applies to all selected tracks. With In/Out shown, `Delete` or Edit → Return to Default resets it: Off for audio tracks, Auto for MIDI tracks.
