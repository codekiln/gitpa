public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/28 Video]]
prev:: [[Ableton/Live/UG/28 Video/03 Matching Sound to Video]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F28%20Video%2F04%20Video%20Trimming%20Tricks
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___28%20Video___04%20Video%20Trimming%20Tricks.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [28.4 Video Trimming Tricks](https://www.ableton.com/en/live-manual/12/working-with-video/#video-trimming-tricks)
	- Movies often arrive with a few seconds of pre-roll (the "two-beep") that the mix engineer expects in the delivered audio too. To compose with the action at 1.1.1 and timecode 00:00:00:00, then restore the pre-roll:
		- Drop the movie at 1.1.1.
			- ![A video clip at the start of the Arrangement](https://ableton-production.imgix.net/live-manual/12/VideoInArrangement.png?auto=&w=320)
		- In Clip View, drag the Start Marker right to where the action begins.
			- ![Dragging the Start Marker past the pre-roll](https://ableton-production.imgix.net/live-manual/12/VideoStartMarkerAtTwoSecs.png?auto=&w=320)
		- When the music is ready to render, Select All and drag everything a few seconds right.
		- Select only the video clip and drag its left edge all the way left to reveal the pre-roll.
			- ![The video clip with its pre-roll restored](https://ableton-production.imgix.net/live-manual/12/VideoClipWithTwoBeepBack.png?auto=&w=320)
	- With the video clip still selected, Export Audio/Video renders a file as long as the original movie, pre-roll included.
