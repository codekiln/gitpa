public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 4]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/14 Config/02 MIDI Control Center/02 Wavetables Tab]]
next:: [[Microfreak/UG/14 Config/02 MIDI Control Center/02 Wavetables Tab/02 Dragging]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F14%20Config%2F02%20MIDI%20Control%20Center%2F02%20Wavetables%20Tab%2F01%20Management
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F202-proxy-task-import-docs/pages/Microfreak___UG___14%20Config___02%20MIDI%20Control%20Center___02%20Wavetables%20Tab___01%20Management.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 14.2.2.1 Wavetable Management
	- The buttons above the computer and MicroFreak panes move and manage wavetables.
	- Wavetable management buttons
		- ![01 Wavetable management buttons](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___01-Buttons.png)
	- **New Bank** creates an empty bank on the computer and prompts for its name. Drag a wavetable over the new bank's name to add it; banks can combine wavetables from other banks.
	- New Bank name prompt
		- ![02 New Bank name prompt](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___02-New-Bank.png)
	- **Del Bank** deletes a bank after confirmation. Factory banks cannot be deleted.
	- **Import** opens three choices:
		- **Replace Wavetable (.mfw)** replaces the selected wavetable with a MicroFreak Wavetable file.
		- **Replace Wavetable (.wav/.aiff)** replaces it with a WAV or AIFF audio file.
		- **Import New Bank** imports an MFWB bank into the computer pane.
	- Import choices
		- ![03 Import choices](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___03-Import.png)
	- When importing WAV or AIFF audio, MicroFreak converts it into an MFW wavetable of 32 cycles, each 2,048 samples long:
		- Each group of 2,048 source samples counts as a cycle.
		- The source's first and last cycles become cycles 1 and 32.
		- With more than eight source cycles, MicroFreak distributes them evenly across the wavetable and crossfades between them.
		- With fewer than eight source cycles, it spreads them across the slots so the Wave knob can reach every cycle.
	- An audio file can therefore become a usable wavetable without manually preparing each cycle.
	- **Export** saves a selected wavetable as MFW or a selected bank as MFWB. Choose a location in the system save dialog.
	- Export choices
		- ![04 Export choices](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___04-Export.png)
	- **Delete** removes a selected wavetable after confirmation and replaces it with an init wavetable that morphs between simple waveforms.
	- Delete confirmation
		- ![05 Delete confirmation](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___05-Delete.png)
	- **Send to MicroFreak** transfers the bank assembled in the computer pane to the MicroFreak for the User Wavetable oscillator.
	- > [[Note/Warning]] This overwrites every wavetable in the MicroFreak. Do not turn its knobs while the transfer progress bar is visible.
	- Wavetable transfer progress
		- ![06 Wavetable transfer progress](../assets/Microfreak___UG___14-Config___02-MIDI-Control-Center___02-Wavetables-Tab___01-Management___06-Transfer.png)
	- **Recall to Computer** copies the MicroFreak's current wavetables into a new bank in the computer pane. The bank initially has a date-and-time name, which you can change in the Bank Name field.
