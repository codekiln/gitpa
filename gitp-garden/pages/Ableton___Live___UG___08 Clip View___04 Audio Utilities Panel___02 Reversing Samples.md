public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/08 Clip View/04 Audio Utilities Panel]]
prev:: [[Ableton/Live/UG/08 Clip View/04 Audio Utilities Panel/01 Warp Controls]]
next:: [[Ableton/Live/UG/08 Clip View/04 Audio Utilities Panel/03 Destructive Sample Editing]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F08%20Clip%20View%2F04%20Audio%20Utilities%20Panel%2F02%20Reversing%20Samples
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___08%20Clip%20View___04%20Audio%20Utilities%20Panel___02%20Reversing%20Samples.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [8.4.2 Reversing Samples](https://www.ableton.com/en/live-manual/12/clip-view/#reversing-samples)
	- Reverse writes a reversed copy of the sample and swaps it into the clip; it's saved under the Project's Samples/Processed/Reverse, or the Temporary Folder until the Set is saved.
	- Warp Markers stay fixed to the sample, so they flip (a marker on bar 2's downbeat ends up on the second-to-last bar), and loop and region settings flip too. Clip envelopes stay fixed in time.
	- Long samples show progress in the Status Bar and briefly lock editing, though playback continues. Live remembers both versions until it quits, so reversing again is instant.
	- Session View reverses one clip at a time; in Arrangement View, select a range and use Reverse Clip(s) or `R`. Avoid reversing during a performance: reapplying settings can glitch.
