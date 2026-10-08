public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/17 Ext Gear]]
prev:: [[Microfreak/UG/17 Ext Gear/06 MIDI Channels]]
next:: [[Microfreak/UG/17 Ext Gear/08 MIDI Tutorial VCV Rack]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F17%20Ext%20Gear%2F07%20MIDI%20Tutorial%20MINI%20V
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Microfreak___UG___17%20Ext%20Gear___07%20MIDI%20Tutorial%20MINI%20V.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 17.6 Tutorial 1: Using MIDI to control the MINI V VST synth
	- This tutorial uses the MicroFreak to control the filter frequency in Arturia MINI V. The same method works with any V Collection instrument that receives MIDI on channel 4.
	- Set the MicroFreak to transmit on MIDI channel 4 in Utility. MINI V instruments receive on all channels by default; set MINI V to channel 4 from the MIDI channel control at the bottom right.
	- Connect the MicroFreak's USB output to the computer and open MINI V in standalone mode or in a DAW.
	- Open the Arturia System menu and choose Audio MIDI settings. Select Arturia MicroFreak under MIDI devices.
	- Select the MIDI icon in the upper-right corner of the main menu. MINI V's knobs turn red or purple.
	- Select the Filter section's Cutoff Frequency knob, then turn the MicroFreak's Filter knob. MINI V's Cutoff Frequency should respond.
