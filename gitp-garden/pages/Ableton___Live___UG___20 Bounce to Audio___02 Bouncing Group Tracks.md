public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/20 Bounce to Audio]]
prev:: [[Ableton/Live/UG/20 Bounce to Audio/01 Bouncing Individual Tracks]]
next:: [[Ableton/Live/UG/20 Bounce to Audio/03 Pasting Bounced Audio]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F20%20Bounce%20to%20Audio%2F02%20Bouncing%20Group%20Tracks
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___20%20Bounce%20to%20Audio___02%20Bouncing%20Group%20Tracks.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [20.2 Bouncing Group Tracks](https://www.ableton.com/en/live-manual/12/bounce-to-audio/#bouncing-group-tracks)
	- **Bounce Group in Place** replaces a whole Group Track with one audio track. Find it in the group's title bar, a group slot, or the group's main lane context menu.
		- ![A Group Track before and after Bounce Group in Place](https://ableton-production.imgix.net/live-manual/12/GroupTrackBounceInPlaceL12.png?auto=&w=320)
	- **Bounce Group to New Track** renders selected clips or a time selection in the group to a new track and mutes the originals; also `Cmd+B` / `Ctrl+B`.
	- Groups bounce after the mixer, from what reaches the Main output — including effects and sends inside the group, excluding the Main track's own effects.
	- Tracks routed outside the group are left out and may leave silence; return tracks count only if their output reaches Main.
		- ![Bounce Group to New Track with one track routed outside the group](https://ableton-production.imgix.net/live-manual/12/GroupTrackBounceExternalRoutingL12.png?auto=&w=320)
