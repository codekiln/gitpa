public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/06 Arrangement View]]
prev:: [[Ableton/Live/UG/06 Arrangement View/07 Moving and Resizing Clips]]
next:: [[Ableton/Live/UG/06 Arrangement View/09 Selecting Clips and Time]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F06%20Arrangement%20View%2F08%20Audio%20Clip%20Fades%20and%20Crossfades
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___06%20Arrangement%20View___08%20Audio%20Clip%20Fades%20and%20Crossfades.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [6.8 Audio Clip Fades and Crossfades](https://www.ableton.com/en/live-manual/12/arrangement-view/#audio-clip-fades-and-crossfades)
	- Audio clips have fades at their start and end; neighbouring clips on a track can crossfade.
	- Hover over a clip, in a tall enough track, to see the fade handles as small squares at its edges. In Automation Mode, hold `F` over an automation lane to show them.
	- Fade In Start and Fade Out End handles change a fade's length without moving its peak; the Fade Curve handle shapes it.
	- ![Adjusted Fades in a Clip](https://ableton-production.imgix.net/live-manual/12/ArrangementClipFade.png?auto=&w=320)
	- Selecting time that includes a clip's start or end and choosing Create → Create Fade In/Out, `Cmd+Option+F` (Mac) / `Ctrl+Alt+F` (Win), sets the fade to that length.
	- Crossfade by dragging a fade handle over the neighbouring clip's edge, or select across the boundary and choose Create Crossfade. The slope handle shapes it.
	- `Delete` removes a selected fade, unless Create Fades on Clip Edges is on in Record, Warp & Launch Settings; then it resets to 4 ms, and adjacent clips get automatic 4 ms crossfades to prevent clicks.
	- Fades can't cross a clip's loop boundaries, and a clip's two fades can't overlap. A dotted line shows a selected handle's limit.
	- Fades belong to clips, not tracks, and are separate from automation.
