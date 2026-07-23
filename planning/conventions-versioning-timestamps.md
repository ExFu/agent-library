# conventions-versioning-timestamps -- convention-base identifiers become UTC timestamps

**Status:** Adopted (Al, 2026-07-23, from a working session in his personal
library during the post-migration fix-up). First timestamped base minted in
plugin 0.6.0. Companion to `skill-version-generic-refs.md` (v0.5.1), which
made overarching skills tolerate version churn; this note governs when and
how the version itself churns.

## Decision

Convention-base identifiers switch from `v0.x` to **UTC timestamps, to the
minute, shortened**: `YYYYMMDD-HHMM`, e.g. `exfu/20260723-1446/`.

- Plugin versions (0.5.1, ...) and conventions identifiers stop sharing a
  naming surface entirely. A date cannot be mistaken for a plugin release,
  so nobody asks "why is the library on v0.3 when the plugin is 0.5?" --
  the confusion that prompted this decision.
- Lexicographic order is chronological order, so directory listings,
  `latest.txt` comparisons, and version-cleanup sweeps all sort correctly
  for free. The one cross-scheme rule: any timestamp identifier is newer
  than any legacy `v0.x` identifier (raw ASCII sort gets this backwards --
  digits sort before `v`).
- Minute precision is enough; no seconds, no timezone suffix (always UTC),
  no full ISO 8601 punctuation.
- Because every conventions release necessarily mints a fresh identifier,
  a version directory's contents can never again change under a stable
  name. (The shipped `v0.3/` had been patched in place across plugin
  0.4.0, 0.5.0, and 0.5.1 -- the drift this scheme ends.)

## Enactment

Nothing renames in user substrates. An installed `exfu/v0.3/` keeps its
name and lives out its life under the side-by-side model. Scope frontmatter
(`exfu: v0.3`) adopts the new identifier as each scope migrates.

No backwards-compatibility machinery: Al is the only plugin user at the
moment and will tell the migrating agent to take the scheme change into
account directly.

## What shipped (plugin 0.6.0)

- The shipped base `src/shared/substrate/exfu/v0.3/` was minted as
  **`20260723-1446/`** (the first timestamped release; contents = the
  former shipped v0.3 plus self-reference updates). The ontology's
  versioning section now documents the scheme.
- Template pins (`scope.md`, all `Follows:` stubs, the registry template)
  bumped to the new identifier in the same commit as the rename -- the
  "versioned content set" rule from skill-version-generic-refs.md.
- `exfu-migrate-to-dropbox` Step 2 gained the deciding-"newer" rule
  (lexicographic within timestamps; timestamps always beat `v0.x`).
- Parser fixes: `index.py discover_versions()` recognises both identifier
  shapes and its latest-fallback prefers the timestamp era;
  `dashboard-generator.py find_convention_dir()` likewise.
- Depictions across exfu-library, exfu-guides, exfu-start, the install
  skills, install-scheduled-agent, and substrate-guide (v9) updated;
  legacy `v0.2`/`v0.3` detection references and changelog history kept.
- `example/` deliberately stays a pinned v0.3-era instance.
