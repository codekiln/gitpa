public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/22 Stem Separation/02 Separating Audio Files and Clips]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F22%20Stem%20Separation%2F02%20Separating%20Audio%20Files%20and%20Clips%2F01%20Separation%20Speed%20vs.%20Quality
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___22%20Stem%20Separation___02%20Separating%20Audio%20Files%20and%20Clips___01%20Separation%20Speed%20vs.%20Quality.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [22.2.1 Separation Speed vs. Quality](https://www.ableton.com/en/live-manual/12/stem-separation/#separation-speed-vs-quality)
	- **High Speed** separates every stem in one pass. It can still take several minutes on older computers.
	- **High Quality** gives cleaner results (a higher signal-to-distortion ratio) by running separate passes for Vocals, Drums and Bass, then deriving Others from what remains.
	- Crop the clip first to save time: Crop Clip Sample to Time Selection in the Sample Editor, or Crop Clip in the Arrangement, both `Cmd+Shift+J` (Mac) / `Ctrl+Shift+J` (Windows).
	- In High Quality, choosing fewer stems saves time unless Others is included, since Others needs all three other passes. Unused stems from those passes are still saved in the Stems folder.
	- Older Windows computers and Intel Macs separate on the CPU only, so they're slower than Apple silicon Macs, which also use the GPU.
	- Some sounds land in an unexpected stem, such as hi-hat highs in Others or chorused synths in Vocals. Trying both modes can show which suits the material.
