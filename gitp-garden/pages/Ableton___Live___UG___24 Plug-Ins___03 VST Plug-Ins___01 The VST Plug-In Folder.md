public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 3]], [[Logseq/Entity/Proxy/Page]]
up:: [[Ableton/Live/UG/24 Plug-Ins/03 VST Plug-Ins]]
next:: [[Ableton/Live/UG/24 Plug-Ins/03 VST Plug-Ins/02 VST Presets and Banks]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Ableton%2FLive%2FUG%2F24%20Plug-Ins%2F03%20VST%20Plug-Ins%2F01%20The%20VST%20Plug-In%20Folder
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/main/pages/Ableton___Live___UG___24%20Plug-Ins___03%20VST%20Plug-Ins___01%20The%20VST%20Plug-In%20Folder.md
logseq-proxy-last-sync-date:: [[2026-10-27]]

- # [24.3.1 The VST Plug-In Folder](https://www.ableton.com/en/live-manual/12/using-plug-ins/#the-vst-plug-in-folder)
	- VST sources must be activated before first use: press **Activate** in the browser's Plug-Ins panel, or open the Plug-Ins Settings with `Cmd+,` (Mac) / `Ctrl+,` (Windows) and find Plug-In Sources.
	- **Windows:** Browse to set the VST Plug-In Custom Folder (Live may already have found it in the registry) and turn on **Use VST Plug-In Custom Folder**.
		- ![VST plug-in sources on Windows](https://ableton-production.imgix.net/live-manual/12/VstPluginFolderWinL12.png?auto=&w=320)
	- **macOS:** plug-ins in /Library/Audio/Plug-Ins/VST (home and local) are used when **Use VST plug-ins in System Folders** is on. A custom folder can be added alongside or instead, with its own on/off option.
		- ![VST plug-in sources on macOS](https://ableton-production.imgix.net/live-manual/12/VstPlugInFolderMacL12.png?auto=&w=320)
	- Live scans the chosen folders and their subfolders. Aliases placed in a scanned folder can point to plug-ins elsewhere, even on another drive.
	- A plug-in that crashes the scan is reported on the next launch, with the choice to rescan or disable it. One that crashes twice is disabled until reinstalled.
