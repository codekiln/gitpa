public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/38 Computer Audio Resources/01 Managing the CPU Load]]
prev:: [[Ableton/Live/UG/38 Computer Audio Resources/01 Managing the CPU Load/02 CPU Load from Multichannel Audio]]
next:: [[Ableton/Live/UG/38 Computer Audio Resources/01 Managing the CPU Load/04 Track Freeze]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F38%20Computer%20Audio%20Resources%2F01%20Managing%20the%20CPU%20Load%2F03%20CPU%20Load%20from%20Tracks%20and%20Devices
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___38%20Computer%20Audio%20Resources___01%20Managing%20the%20CPU%20Load___03%20CPU%20Load%20from%20Tracks%20and%20Devices.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [38.1.3 CPU Load from Tracks and Devices](https://www.ableton.com/en/live-manual/12/computer-audio-resources-and-strategies/#cpu-load-from-tracks-and-devices)
	- Tracks and devices cost CPU only while they process audio. Adding devices while stopped adds little load; an effect with no input is essentially idle, and a reverb or delay stays active until its tail finishes.
	- That lowers average load but not peak load. To stress-test a Set before a show, play a clip on every track with all devices on; if the CPU meter's Current value stays well under 100%, the Set should hold up.
	- The mixer's **Performance Impact** indicators show each track's share of the load as six rectangles. Turn them on from the Show/Hide Mixer Config menu at the bottom right, or View → Mixer Controls.
		- ![The Mixer's Performance Impact Indicators](https://ableton-production.imgix.net/live-manual/12/MixerPerformanceImpactSectionL12.png)
	- Freeze a heavy track, or turn off some of its devices, to lower its impact.
