public:: true
logseq-entity:: [[Logseq/Entity/Book/Section/Level 2]], [[Logseq/Entity/Proxy/Page]]
up:: [[Microfreak/UG/19 Appendix B Vocoder]]
next:: [[Microfreak/UG/19 Appendix B Vocoder/02 How It Works]]
logseq-proxy-url:: logseq://graph/logseq-encode-garden?page=Microfreak%2FUG%2F19%20Appendix%20B%20Vocoder%2F01%20Intro
logseq-proxy-codeforge-url:: https://github.com/codekiln/logseq-encode-garden/blob/codex%2F204-guide-images-b2/pages/Microfreak___UG___19%20Appendix%20B%20Vocoder___01%20Intro.md
logseq-proxy-last-sync-date:: [[2026-10-08]]
- # 19.1. An Introduction to Vocoding
	- Bell Labs patented the first vocoder in 1939 to speed up telephone connections. Musical vocoders appeared about forty years later and became known for their robotic sound. Artists have since used them in many ways, from Kraftwerk's “Autobahn” to Imogen Heap's “Hide and Seek.”
	- A vocoder transfers qualities of one sound to another. Speech vowels have characteristic frequency peaks called **formants**; a vowel commonly has one to three prominent peaks, F1 through F3. The positions of these peaks vary with the speaker and the sound being made.
	- The **modulator**, usually your voice, supplies the changing formants. A bank of tuned filters analyzes them and applies them to a **carrier**, such as an oscillator wave. The carrier takes on the shape of your voice.
	- Speech also has a changing loudness contour. The vocoder tracks this contour along with the formants, so the carrier follows the way you articulate a word.
