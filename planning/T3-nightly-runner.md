# T3 -- Nightly librarian runner

Build the cadence-based runner that reads the librarian registry, resolves dependencies, and executes each registered librarian in order. Create the `nightly-librarians` scheduled task as the first cadence group.

**Parents:** `T2-librarian-framework.md` (domain), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-librarian-definitions (the registry schema and structured format must exist)
**Status:** not started.

---

## Why

The nightly index currently runs as a standalone script (`index.py`) triggered by a scheduled task. That works for one librarian. When there are five nightly librarians with dependency ordering, error isolation, and health tracking, a standalone script per librarian doesn't scale. The runner is the orchestration layer.

---

## What to build

### 1. Runner script

A Python script at `plugin/src/shared/scheduled-tasks/nightly-librarians/runner.py` that:

1. Accepts the substrate root path and cadence name as arguments
2. Reads `exfu/derived/librarian-registry.json`
3. Filters to librarians matching the cadence and enabled=true
4. Topologically sorts by `depends_on`
5. Executes each in order:
   - `python-script`: runs the script with subprocess, passing substrate root
   - `shell`: runs the command with subprocess
   - `skill`: logs as "queued for next interactive session" (not executable in cron)
   - `mcp-tool`: logs as "queued" (future implementation)
6. Records results (success/failure, duration, any stderr output)
7. Updates the registry with last_run, last_status, consecutive_failures
8. Appends to the run log
9. Trims log entries older than 90 days

**Error handling:**
- If a librarian fails, log the error and continue with the next one
- If a librarian's dependency failed in this run, skip it (log "skipped: dependency failed")
- Exit code 0 unless the runner itself crashes (individual librarian failures are logged, not propagated)

### 2. Refactor index.py

The current `index.py` is a standalone script with its own argument parsing. Refactor so it can be:
- Called by the runner (passing substrate root as argument)
- Still run standalone for testing/debugging

This is a minor refactor: ensure it accepts a positional argument and returns a clean exit code.

### 3. Nightly-librarians scheduled task

Create `plugin/src/shared/scheduled-tasks/nightly-librarians/`:
- `TASK.md` -- scheduled task definition (name, description, cadence: nightly)
- `runner.py` -- the runner script
- The existing `substrate-index/` scheduled task remains for backwards compatibility but delegates to (or is replaced by) the runner

### 4. Wire up nightly-index

Register the nightly index as the first librarian in the system:
- Create a default `librarian-registry.json` with the nightly-index entry
- The install-librarian skill (T3-install-librarian-skill) will handle future registrations; for now, the registry ships with the nightly index pre-registered

### 5. Runner for other cadences

The runner is cadence-agnostic (it takes cadence as an argument). Additional cadence groups just need their own scheduled task that invokes `runner.py <root> <cadence>`. No separate runner script per cadence.

---

## Acceptance criteria

1. `runner.py` reads the registry and executes nightly librarians in dependency order
2. Individual librarian failures don't crash the runner
3. Registry is updated with last_run, last_status after each run
4. Run log is appended with per-librarian results
5. `index.py` works both standalone and called by the runner
6. The `nightly-librarians` scheduled task is defined and wired
7. Running the scheduled task against the example substrate produces correct output

---

## Files to create/modify

- Create: `plugin/src/shared/scheduled-tasks/nightly-librarians/TASK.md`
- Create: `plugin/src/shared/scheduled-tasks/nightly-librarians/runner.py`
- Modify: `plugin/src/shared/scheduled-tasks/substrate-index/index.py` (minor refactor)
- Create: default `librarian-registry.json` content (shipped in substrate template or created at install)

---

## Where this plan lives

- This file: `plugin/planning/T3-nightly-runner.md`
- Domain: `plugin/planning/T2-librarian-framework.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
