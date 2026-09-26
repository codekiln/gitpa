# gitpa
Ghost in the Patch Alpha podcast

## Podcast media upload

Prepare an MP3 from an exported WAV with
`mise run media:prepare -- SOURCE.wav OUTPUT.mp3`. The task makes a stereo
192 kbps MP3 with one decibel of headroom and keeps the export outside Git.

The public media bucket is `logseq-encode-garden`. Upload one prepared MP3 with
`mise run media:upload -- SOURCE.mp3 gitpa/episodes/YYYY-MM-DD/FILE.mp3`.
Use `--dry-run` before the source path to check the destination without credentials.
The task uses the `logseq-encode-publishing` 1Password Environment mount and
will stop if it is absent. It does not read the Backblaze administration mount.
It prints the public Backblaze URL, then checks that the URL responds after the
upload. Set `GITPA_MEDIA_BASE_URL` when a custom media domain is ready.
