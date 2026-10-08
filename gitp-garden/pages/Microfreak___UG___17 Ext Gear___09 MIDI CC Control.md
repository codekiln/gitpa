public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/17 Ext Gear]]
prev:: [[Microfreak/UG/17 Ext Gear/08 MIDI Tutorial VCV Rack]]
next:: [[Microfreak/UG/17 Ext Gear/10 Tutorial MIDI CC]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F17%20Ext%20Gear%2F09%20MIDI%20CC%20Control
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F204-guide-images-b2/pages/Microfreak___UG___17%20Ext%20Gear___09%20MIDI%20CC%20Control.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 17.8 Using MIDI CC# codes for control
	- MicroFreak encoders send MIDI CC# data as you turn them. CC# codes control parameters on external synthesizers, modular systems, and software such as VCV Rack. They are parameter-control messages, separate from note messages.
	- CC# codes work like remote knobs. For example, the MicroFreak's Filter knob sends CC# 23; a value of 0 closes the filter and a value of 127 opens it fully. The MicroFreak has 20 CC# codes for its parameters.
	- CC# codes can also control plug-in parameters. Arturia's V Collection plug-ins have MIDI Learn, which can link a MicroFreak knob to a plug-in knob. For example, the MicroFreak's Filter knob can control filters in CZ V, DX7 V, and Buchla Easel V at the same time.
	- Consult the DAW and V Collection documentation for setup instructions.
	- > [[Note/Info]] If CC# messages are not sent, check the knob-send-CC# setting in Utility or MIDI Control Center.
	- The tutorials below show how to use CC# codes to control VCV Rack modules.
