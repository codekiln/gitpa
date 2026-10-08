public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/08 LFO]]
prev:: [[Microfreak/UG/08 LFO/02 LFO Rate]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F08%20LFO%2F03%20Freaky%20Tips
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F204-guide-images-b2/pages/Microfreak___UG___08%20LFO___03%20Freaky%20Tips.md
logseq-proxy-last-sync-date:: [[2026-10-08]]

- # 08.3 Freaky Tips and Tricks
	- Use the LFO to modulate both the filter cutoff and the envelope attack and decay times. Filter cutoff is a standard Matrix connection; assign the envelope attack and decay destinations explicitly in the Matrix. See [[Microfreak/UG/05 Connections/02 Matrix and Encoder]] for details.
	- Adding some randomness to filter cutoff creates a fuzzy effect. Random modulation of an envelope's decay or sustain adds variety to a rhythmic pulse and can revive a stale sound.
	- Use the sine or sawtooth wave to modulate an envelope's level. Playing an arpeggio then produces cyclic crescendos and diminuendos. A very slow LFO can also modulate the Cycling Envelope's rise and fall times; route the resulting envelope to other destinations.
	- Use the rising sawtooth to modulate the decay time of the Standard or Cycling Envelope for more realistic drum or bell sounds. The Cycling Envelope's attack and fall shapes can also change dynamically from linear to exponential. See [[Microfreak/UG/09 Envelope Gen]] for details.
	- To animate a sequence or arpeggio, sync the LFO, select Random, and apply a small amount of modulation to oscillator pitch in the Matrix. Modulate the Matrix amount with a very short Cycling Envelope set to ENV, so the LFO modulation ends after the initial attack.
	- Assign Glide amount as an LFO destination to switch Glide on and off by setting its amount to zero. With Sync on, the LFO can activate Glide every other or every fourth sequencer step.
