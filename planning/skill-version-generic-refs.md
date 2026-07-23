# skill-version-generic-refs -- overarching skills stop naming the convention version

**Status:** Adopted (approved by Al in plan mode, 2026-07-23, after line-by-line
inventory review). Landed in v0.5.1.

## Why

Al's migration of his own v0.3 substrate to the v0.4+ ExFu Library approach
broke because overarching skills -- notably the generated wow skill installed in
Claude Desktop -- hardcoded `exfu/v0.3/...` paths. When the substrate moved on,
those references pointed at nothing. Version numbers baked into prescriptive
prose are churn debt: every convention-base bump would need a ~30-site sweep
across skills, and any missed site becomes a silent runtime breakage in a
user-side artefact that no substrate migration can reach.

## The ruling (Al, 2026-07-23)

Keep anything *within* scopes and the ExFu Library folder that is genuinely
version dependent. It is the *overarching* abstract instructions -- like the wow
skill -- that must allow version churn underneath them.

## Classification applied

1. **FIX** -- prose and instructions that *prescribe* behaviour say
   `exfu/<version>/` and resolve at read time: `exfu/latest.txt` inside a
   substrate; the single version directory under
   `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/` inside the plugin.
2. **KEEP (pin)** -- instantiated pins: `scope.md`'s `exfu:` field, `Follows:`
   lines, registry `source:` paths. These are the versioned content set and
   bump in the same commit as a future base rename.
3. **KEEP (depiction)** -- examples and diagrams that depict real file content
   stay concrete (real files really contain versions).
4. **KEEP (legacy)** -- v0.2 references used for old-setup detection.
5. **KEEP (history)** -- changelogs and the planning corpus.

## What changed (v0.5.1)

- Wow template navigation map: version-generic; generated wows no longer
  snapshot the convention version.
- exfu-guides, substrate-guide, exfu-create-wow, exfu-library: prescriptive
  refs to `exfu/<version>/`; drifting headings dropped (exfu-library's heading
  still said v0.4.0 under the 0.5.0 plugin).
- Install skills (all three variants): deploy whatever version the plugin
  ships; latest.txt names it; checklists match.
- exfu-migrate-to-dropbox: version-aware refresh -- same version overwrites in
  place; newer installs alongside and updates latest.txt (side-by-side model).
- Script docstring version labels dropped (they already disagreed with each
  other: v0.3.0 vs v0.5.0).
- Example library: wow-template copy synced (it had also missed the 0.4
  `substrate` -> `exfu-library` rename); everything else in example/ is a
  deliberately pinned v0.3 instance and stays.

The full line-by-line inventory reviewed for this change lives in the session
plan (2026-07-23); the classification rules above are the durable part.
