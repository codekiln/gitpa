public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/33 Max for Live Devices/02 Max for Live Audio Effects]]
prev:: [[Ableton/Live/UG/33 Max for Live Devices/02 Max for Live Audio Effects/01 Align Delay]]
next:: [[Ableton/Live/UG/33 Max for Live Devices/02 Max for Live Audio Effects/03 LFO]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F33%20Max%20for%20Live%20Devices%2F02%20Max%20for%20Live%20Audio%20Effects%2F02%20Envelope%20Follower
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___33%20Max%20for%20Live%20Devices___02%20Max%20for%20Live%20Audio%20Effects___02%20Envelope%20Follower.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [33.2.2 Envelope Follower](https://www.ableton.com/en/live-manual/12/max-for-live-devices/#envelope-follower)
	- ![The Envelope Follower Effect](https://ableton-production.imgix.net/live-manual/12/MaxEnvelopeFollowerL12.png?auto=&w=320)
	- A modulator that follows the level of the incoming audio and turns it into a smooth control curve. Auto-wah is the classic use.
	- Mapping, Mod, polarity and Min/Max work as described in [[Ableton/Live/UG/33 Max for Live Devices/02 Max for Live Audio Effects]].
		- ![You Can Map up to Eight Parameters](https://ableton-production.imgix.net/live-manual/12/MaxEnvelopeFollowerMappingL12.png?auto=&w=320)
	- **Gain** — input gain
	- **Rise** and **Fall** — smooth the attack and release of the curve
	- **Delay** — delays the curve, in time or synced divisions (Delay Mode buttons)
	- Sidechain: by default the curve comes from the track's own input. The triangle at the top left opens the Audio Routing panel.
		- ![The Sidechain Section in Envelope Follower](https://ableton-production.imgix.net/live-manual/12/MaxEnvelopeFollowerSidechainL12.png?auto=&w=320)
		- turn on **Sidechain**, choose the source track in **Audio From**, and choose Pre FX, Post FX or Post Mixer (and a Rack channel if needed)
		- **Direct** and **S.C.** meters show the track and sidechain levels
		- **Sidechain Mix** — 0% uses only the track input, 100% only the sidechain; a Drum Rack as sidechain gives rhythmic ducking or gating