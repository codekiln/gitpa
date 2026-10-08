# Microfreak references

Gitpa imports the complete `Microfreak` namespace under its source names, including the guide, presets, CLI notes and metadata pages. [Issue #18](https://github.com/codekiln/gitpa/issues/18) tracks the import; [the audit](microfreak-namespace-audit.json) lists imported definitions and references that need follow-up.

The source inventory contains 611 namespace pages. The shared planner includes their entity definitions and supporting dictionaries, giving 657 pages in this import. All imported bodies and protected tags match the source. Destination publication properties expose the reference pages while retaining existing local choices; proxy provenance and ownership remain in the checked-in manifest.

The user guide has 594 navigation targets and the namespace has 212 page embeds. All resolve in the imported graph. All 130 linked local assets are copied from the source and remain available in the prepared website graph. The logical references `Microfreak/Docs` and `Microfreak/Preset/Initialized` have no source files and remain references without invented content.

## Refresh

Run from the repository root. Preview discovers the current root and descendants, including newly added pages:

```sh
mise run namespace:sync --source /path/to/logseq-encode-garden --namespace Microfreak --report /tmp/microfreak-audit.json
```

Apply the validated batch:

```sh
mise run namespace:sync --source /path/to/logseq-encode-garden --namespace Microfreak --report /tmp/microfreak-audit.json --apply
```

The current source is the explicit `codex/202-proxy-task-import-docs` worktree, supplying the reviewed importer from [garden PR #203](https://github.com/codekiln/logseq-encode-garden/pull/203). Its selected instrument content matches garden main. After that dependency merges, select the registered garden checkout and refresh source URLs to the default branch.

## References for follow-up

The audit reports logical supporting hubs without content, including `Logseq/Entity/Preset` and the `up`, `prev`, and `next` frontmatter dictionary pages. Navigation values themselves resolve; these missing dictionary pages describe the property names.

External links include Arturia/MCC guides, Elektroid, music-log references, and general garden topics. The report also contains literal examples, aliases and date-page references from the shared definition documentation; an absent exact page file does not establish a missing logical page. The two `MyPage/...` embed warnings come from examples in shared frontmatter documentation. Every Microfreak guide embed has source and destination content.

Shared entity definitions and manifest ownership are integrated sequentially after the [Launchpad/helper import](https://github.com/codekiln/gitpa/issues/19) and [existing proxy refresh](https://github.com/codekiln/gitpa/pull/21). The repeated namespace preview reports no further writes.
