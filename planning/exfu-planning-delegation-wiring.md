# exfu-planning-delegation-wiring -- this repo wired for ExFu planning, delegation, and refreshed APV tooling

**Status:** Adopted (Al, 2026-07-23, in-session). Landed in the same sitting it
was raised: the repo now self-orients to `exfu-agent-planning-and-delegating`
on every surface, and its APV attachment was audited up to toolchain 0.7.1.
Re-audited 2026-08-10 against toolchain 0.7.2 (see "Re-audit at 0.7.2" below).

Anchor for the working-environment wiring of this repo. Not product work: no
plugin source changed, nothing in `src/` or `plugins/` was touched. This
document exists so the setup is reviewable rather than arriving as an
unexplained diff to committed config.

## Why

Three gaps, all in how the repo orients an agent session rather than in what
the repo ships:

1. **Planning and delegation were not wired.** The methodology and the
   delegation core were available as a user-scope plugin but nothing in the
   repo declared the dependency. A session on a surface where the global
   enable did not propagate -- Cowork, or a worktree checkout without
   `.claude/settings.json` -- had no way to discover it.
2. **The APV attachment had drifted.** Toolchain 0.7.1 was installed but the
   repo still carried pre-0.7.1 git hooks, a machine-pinned shim, and a
   `.apv/.toolchain-home` file that resolved only on this machine.
3. **Delegated work had no defined route into the record.** With the ExFu
   delegation core present and this repo APV-tracked, the seam between them
   was undeclared, so a delegate's output had no capture contract and the
   event log was not named as untouchable.

## What was done

- **`.claude/settings.json`** -- enabled `exfu-agent-planning-and-delegating@exfu`
  and registered a `SessionStart` (`startup|resume|clear`) hook. Written by the
  plugin's own idempotent updater, never by hand.
- **`.claude/hooks/exfu-agent-planning-and-delegating-orient.sh`** -- committed,
  project-scope orientation hook, so it fires from the repo's own settings
  regardless of plugin-load state and travels with the repo.
- **`CLAUDE.md`** -- orientation block stamped between its markers, as the
  fallback for surfaces where project hooks are disabled by policy.
- **`.exfu/`** -- `providers.toml` plus `handoffs/`, `returns/`, `state/`; the
  three disposable dirs excluded via `.git/info/exclude` (worktree-safe).
- **APV attach audit** -- `[requires]` block pinning `apv_min_version = "0.7.1"`
  and the three skills; shim refreshed to the machine-independent form;
  `.apv/.toolchain-home` removed in favour of discovery-by-newest; the three
  git hooks refreshed. No hook slot was refused: every slot already held APV's
  own hook, merely stale.

## Operative decisions

**The capture provider is enabled, not left commented.** The shipped
`providers.toml` template ships `capture` commented out and
`protected_paths = []`, on the assumption the repo may not be tracked. This
repo is tracked, which is the exact condition the template's own comment names,
so `capture = "exfu-planning-apv-integration"` is set and
`protected_paths = [".apv/events.jsonl", ".apv/"]` declared. The data dir was
resolved by doctrine (env unset -> `.apv-config.toml` `[storage] data_dir`),
not assumed. Naming `events.jsonl` explicitly alongside the directory is what
makes a delegate touching the record an unambiguous integrity violation under
the core's snapshot comparison.

**The stale `agent-plan-visualiser@apv` enablement key was initially left
alone, then repointed on Al's instruction.** It named a marketplace that no
longer exists (`apv` is absent from the configured marketplace list) and a
plugin id that resolves to nothing installed. The wiring pass deliberately left
it, on the grounds that the updater merges only its own keys and removing
someone else's is not that work's business; Al then directed the fix, so the
entity was reopened and the key repointed to `exfu-agent-plan-visualiser@exfu`.

Repointed rather than deleted. Deletion was the alternative -- the plugin is
enabled at user scope, so nothing is currently broken by its absence -- but a
project-scope enablement is what makes the plugin load on surfaces where the
user-scope enable does not propagate, which is the worktree-checkout case this
repo's own CLAUDE.md warns about. It also keeps the declaration symmetric with
`exfu-agent-planning-and-delegating@exfu` beside it and with the
`[requires]` block in `.apv-config.toml`, so the repo states its APV dependency
in-repo rather than relying on the machine it happens to be cloned onto.

## Re-audit at 0.7.2

The plugin was updated and renamed (`agent-plan-visualiser` ->
`exfu-agent-plan-visualiser`, now 0.7.2), so this anchor was reopened and
`/apv-init` re-run. Every component reported `ok` with no refused hook slot:
the three git hooks resolve the toolchain by a discovery glob that already
matches the new name, so the rename did not strand them. Two things did need
fixing, and one apparent problem turned out not to be one.

**The CLAUDE.md orientation block was stale, and silently so.** It named the
retired plugin and gave a fallback path,
`~/.claude/plugins/cache/*/agent-plan-visualiser/*/skills/`, that no longer
matched anything on disk. A cold agent on a surface without the plugin would
have followed it and found nothing -- precisely the worktree case the block
exists to rescue. `apv-init` offered a migration but warned that the legacy
block's extent was inferred, having no closing marker; the inferred region was
checked against the section boundaries before accepting, and stopped exactly
where the next heading began. The migrated block adds the closing marker, the
skill-versus-slash-alias distinction for Cowork/Desktop, install instructions,
and a note that fresh worktrees must run `/apv-init` because git hooks live in
`.git/` and are not committed.

**The gate was running four checks where the shipped default is seven.**
Because `apv-init` respects an existing `.apv-config.toml` rather than
rewriting it, a config predating `pending-ceremony`,
`deferred-verification` and `attribution-drift` keeps silently omitting them:
the file looks configured, the gate reports `PASS`, and nothing announces the
gap. This is the cost of the respect-existing-config rule, and it is worth
knowing about at each toolchain bump -- the diff to watch is the init script's
own template, not the report. Adding the three surfaced a real signal that had
been invisible: `proposal-multi-provider` has sat in `draft` for 19 commits
with its acceptance ceremony pending, which is exactly the
`2026-07-03.ceremony-prompting-gap` failure the check was written to catch.
`attribution-drift` is inert here (no `[projects]` registry, so no stamps) but
correct to carry. The commented `[projects]` template was also refreshed to the
current `dirs` carve-out shape.

**The schema version is not stale, despite appearances.** `.apv/schema-version.txt`
reads `0.3.0` while the toolchain ships schemas through `0.6.0`. No migration is
owed: `0.3.0` is still what `apv-init` seeds, and `validate-events.sh` always
validates against the newest epoch, whose `schema_version` enum is a superset of
the earlier ones. Recorded here because the mismatch reads as a defect on every
inspection and is not one.

Left alone: `apv_min_version` stays at `0.7.1`. It is a floor and 0.7.2
satisfies it; raising it should be a deliberate act when a newer feature is
actually depended on, not a reflex at each bump.

## Consequences

Delegation preflight in this repo now runs the draft gate against
`.apv/cache.sqlite`. At the time of writing five of nine entities are `draft`,
so implement-mode delegation is refused against all but
`v0.5-dashboard-action-basket`; audit and review modes remain open, being
legitimate against a draft. That is the gate working, not a defect.

Pre-init history is not mined. This attaches from now.
