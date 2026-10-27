public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/29 Audio Effect Reference/25 Looper]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F29%20Audio%20Effect%20Reference%2F25%20Looper%2F01%20Feedback%20Routing
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___29%20Audio%20Effect%20Reference___25%20Looper___01%20Feedback%20Routing.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [29.25.1 Feedback Routing](https://www.ableton.com/en/live-manual/12/live-audio-effect-reference/#feedback-routing)
	- Looper can send to and receive from other tracks, so overdubs keep passing through another track's effects:
		- 1. Put Looper on a track and record at least one pass.
		- 2. Create another audio track.
		- 3. Set its top Audio From and Audio To to the Looper track.
		- 4. Set its bottom Audio From and Audio To to "Insert-Looper".
		- 5. Set its Monitoring to In.
		- 6. Add effects to the new track.
		- 7. Put Looper in Overdub.
	- Each pass goes through the other track's effects and back into Looper, getting more processed every time.