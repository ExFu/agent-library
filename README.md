# ExFu Plugin

Plugin source for the ExFu plugins, distributed through the public **exfu-library**
marketplace at https://github.com/ExFu/claude-marketplace:

- **exfu-solo** -- personal Agent Library for individuals
- **exfu-team** -- personal layer on top of a team's shared substrate
- **exfu-team-admin** -- tools for the substrate champion running a team install

## Install

From the public **exfu-library** marketplace (works in both Claude Code and Cowork):

```
/plugin marketplace add ExFu/claude-marketplace
/plugin install exfu-solo@exfu-library
```

Swap `exfu-solo` for `exfu-team` or `exfu-team-admin` as needed.

This repo is the plugin **source**; it no longer carries its own marketplace
manifest. The marketplace lives in the `ExFu/claude-marketplace` repo, whose
entries point back at the `plugins/` built here.

## Build

```
./build/build.sh all          # compose src/ into plugins/ (committed)
./build/build.sh all --dist   # additionally produce versioned zips in dist/
```

Plugin source lives in `src/` (shared + per-variant); `plugins/` is generated
output -- never edit it directly. See `CLAUDE.md` for the full orientation.

Extracted from the `exfu_website` repo on 2026-07-22 with plugin-only git
history preserved. The website serves the public install page and download
zips at https://exfu.ai/install.
