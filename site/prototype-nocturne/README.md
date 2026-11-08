# Prototype: Nocturne

A moonlit garden surrounds a pale initial in an ink-blue manuscript panel. Gilded corners, a crescent moon, uneven foliage, and a small spirit suggest a voice coming through the night. A seed derived from the episode changes the stars, flower color, and the spirit's position.

This is an experiment for [issue #164](https://github.com/codekiln/gitpa/issues/164). It changes only the preview server's responses; normal site builds do not load these files.

Build the site as described in [the publishing guide](../../docs/gardener-publishing.md), then run:

```sh
python3 site/prototype-nocturne/preview.py /private/tmp/gitpa-preview
```

Open `http://localhost:8766/gitpa/GitP/A/Session/26/11/06-Fri/` for an episode with both initials. The server works with any generated site whose `gitpa` directory is inside the given parent directory. Navigate normally to compare episodes and appearance settings.
