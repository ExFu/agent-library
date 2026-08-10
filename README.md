# ExFu Agent Library

Plugin source for the ExFu Agent Library, distributed through the public **`exfu`**
marketplace at https://github.com/ExFu/exfu-marketplace:

- **exfu-agent-library-solo** -- personal Agent Library for individuals
- **exfu-agent-library-team** -- personal layer on top of a team's shared substrate
- **exfu-agent-library-team-admin** -- tools for the substrate champion running a team install

## Install

From the public **`exfu`** marketplace (works in both Claude Code and Cowork):

```
/plugin marketplace add ExFu/exfu-marketplace
/plugin install exfu-agent-library-solo@exfu
```

Swap `exfu-agent-library-solo` for `exfu-agent-library-team` or `exfu-agent-library-team-admin` as needed.

This repo is the plugin **source**; it no longer carries its own marketplace
manifest. The marketplace lives in the `ExFu/exfu-marketplace` repo, whose
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

## License

Proprietary — see [LICENSE](LICENSE). This repository is public for
distribution convenience; publication does not grant an open-source licence.
Redistribution enquiries: al@exfu.ai
