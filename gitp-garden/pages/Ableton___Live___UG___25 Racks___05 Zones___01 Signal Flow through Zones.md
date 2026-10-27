public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/25 Racks/05 Zones]]
next:: [[Ableton/Live/UG/25 Racks/05 Zones/02 Key Zones]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F25%20Racks%2F05%20Zones%2F01%20Signal%20Flow%20through%20Zones
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___25%20Racks___05%20Zones___01%20Signal%20Flow%20through%20Zones.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [25.5.1 Signal Flow through Zones](https://www.ableton.com/en/live-manual/12/instrument-drum-and-effect-racks/#signal-flow-through-zones)
	- In a MIDI Effect Rack with four chains, all chains receive the same MIDI.
	- Before entering a chain, a note must pass that chain's key zone, then its velocity zone, then its chain select zone. Failing any one keeps it out.
	- The outputs of all chains are mixed and passed to whatever follows the Rack.
