# ExFu Plugin

Source and Claude Code plugin marketplace for the ExFu plugins:

- **exfu-solo** -- personal Agent Library for individuals
- **exfu-team** -- personal layer on top of a team's shared substrate
- **exfu-team-admin** -- tools for the substrate champion running a team install

## Install

```
/plugin marketplace add /Users/al/Studio/projects/exfu_plugin
/plugin install exfu-solo@exfu-library
```

(Once this repo has a public remote, the path becomes the repo slug.)

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
