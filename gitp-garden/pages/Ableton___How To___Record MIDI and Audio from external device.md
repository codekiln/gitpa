public:: true
logseq-entity:: [[Logseq/Entity/Proxy/Page]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FHow%20To%2FRecord%20MIDI%20and%20Audio%20from%20external%20device
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___How%20To___Record%20MIDI%20and%20Audio%20from%20external%20device.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
# How to record to [[Ableton/Track/MIDI]] and [[Ableton/Track/Audio]] simultaneously from an external device
	- ## [[My Notes]]
		- [[2025-05-31 Sat]]
			- With an external keyboard that generates audio, such as an external synthesizer, if you want to record MIDI and audio at the same time into two tracks, one MIDI and one audio, then it's important that you set [[Ableton Track IO - Monitor set to Off]] in the MIDI channel.
			- Why? Because if you have [[Ableton/Track/Record Arm]] set to on for both tracks, then by default, if you have [[Ableton Track IO - Monitor set to Auto]], then the incoming MIDI notes will trigger an outgoing MIDI note back to the external device, causing a double onset of the external sound, which can sound like a "phaser" effect.
	-