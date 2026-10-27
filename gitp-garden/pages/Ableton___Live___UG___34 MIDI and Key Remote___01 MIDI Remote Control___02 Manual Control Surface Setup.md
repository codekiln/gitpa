public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control]]
prev:: [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control/01 Natively Supported Control Surfaces]]
next:: [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control/03 Takeover Mode]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F34%20MIDI%20and%20Key%20Remote%2F01%20MIDI%20Remote%20Control%2F02%20Manual%20Control%20Surface%20Setup
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___34%20MIDI%20and%20Key%20Remote___01%20MIDI%20Remote%20Control___02%20Manual%20Control%20Surface%20Setup.md
logseq-proxy-last-sync-date:: [[2026-10-27]]
- # [34.1.2 Manual Control Surface Setup](https://www.ableton.com/en/live-manual/12/midi-and-key-remote-control/#manual-control-surface-setup)
	- A controller that is not in the Control Surface chooser can still be mapped by hand from the MIDI Ports section of the Link, Tempo & MIDI tab.
	- ![Defining Control Surfaces Manually](https://ableton-production.imgix.net/live-manual/12/MIDIActivePorts.png?auto=&w=320)
	- To use an input port for remote control, set its **Remote** switch to On. Any number of ports can be on; Live merges their MIDI.
	- For a controller with motorized faders or LEDs, also turn on Remote for its output port so Live can send changed values back to it.
	- To test, send MIDI from the controller: the Control Bar's MIDI indicators flash when Live receives a message.
	- The manual suggests choosing a Takeover Mode before leaving Settings — [[Ableton/Live/UG/34 MIDI and Key Remote/01 MIDI Remote Control/03 Takeover Mode]]. Mapping then happens one parameter at a time.