public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/09 Audio Clips Tempo and Warping/03 Warp Modes]]
next:: [[Ableton/Live/UG/09 Audio Clips Tempo and Warping/03 Warp Modes/02 Tones Mode]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F09%20Audio%20Clips%20Tempo%20and%20Warping%2F03%20Warp%20Modes%2F01%20Beats%20Mode
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___09%20Audio%20Clips%20Tempo%20and%20Warping___03%20Warp%20Modes___01%20Beats%20Mode.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [9.3.1 Beats Mode](https://www.ableton.com/en/live-manual/12/audio-clips-tempo-and-warping/#beats-mode)
	- For material with a strong rhythm, such as drum loops and most dance music; it keeps transients intact.
	- Preserve: Transients for percussive material, or a grid division to keep fixed beat divisions. Large divisions with transposition give rhythmic artifacts.
	- Transient Loop Mode, for the end of each segment between transients:
		- Loop Off: plays to its end, then silence until the next transient.
		- Loop Forward: jumps back to a zero-crossing near the segment's middle and loops until the next transient.
		- Loop Back-and-Forth: plays back and forth from a zero-crossing near the middle until the next transient; with preserved transients this often sounds best, especially at slow tempos.
	- Transient Envelope: the fade on each segment. 100 means no fade; lower values decay faster, from smoothing clicks to gating effects.
