# T2 -- Librarian framework

The system for defining, installing, scheduling, and running librarians: autonomous maintenance agents that keep the substrate healthy.

---

## Why

A substrate is a living system. Files accumulate, indexes go stale, old convention versions linger, inbox items pile up. Without maintenance, entropy wins. Librarians are the answer: defined agents that run on a schedule, each responsible for a specific maintenance task.

The nightly index already exists as a standalone Python script. But it's a one-off; there's no framework for adding more librarians, grouping them by cadence, tracking their health, or letting users install them through a guided conversation. As the substrate grows, so does the need for maintenance. The framework makes that scalable.

## How

### Core concepts

**Librarian definition.** A markdown file with YAML frontmatter describing what the librarian does, what it touches, how often it runs, and how it's implemented. Lives in `librarians/` within a scope or the convention base.

**Cadence.** How often a librarian runs. Standard cadences: `nightly`, `weekly`, `hourly`, `on-demand`. Each cadence maps to one scheduled task. Multiple librarians share a cadence (and therefore a scheduled task); different cadences get different tasks.

**Registry.** A JSON file at `exfu/derived/librarian-registry.json` tracking every installed librarian: name, cadence, implementation, dependencies, enabled/disabled, last run, last status. The runner reads this; the install-librarian skill writes to it.

**Runner.** A Python script invoked by a scheduled task. Reads the registry for its cadence, resolves dependency order, executes each librarian in sequence, logs results. One runner per cadence; the nightly scheduled task runs the nightly runner.

**Implementation types.** A librarian can be:
- `python-script` -- a standalone .py file (like the nightly index)
- `shell` -- a shell command
- `skill` -- a Claude skill to be loaded and run conversationally (for librarians that need judgment)
- `mcp-tool` -- an MCP tool call

### Definition format

```yaml
---
name: nightly-index
cadence: nightly
implementation: python-script
script: scheduled-tasks/substrate-index/index.py
reads:
  - "*/scope.md"
  - "*/agent.md"
writes:
  - "exfu/derived/index.json"
depends_on: []
description: Walks the substrate and regenerates the global scope index
---
```

Followed by a markdown body explaining why the librarian exists, what it does, and any nuances. The body is for humans and agents reading the definition; the frontmatter is for the runner.

### Cadence grouping

Each cadence becomes one scheduled task:

| Cadence | Scheduled task | Typical librarians |
|---|---|---|
| nightly | `nightly-librarians` | Index, inbox triage summary, stale-scope detection |
| weekly | `weekly-librarians` | Version cleanup, context freshness check |
| hourly | `hourly-librarians` | (rare; for high-frequency maintenance) |
| on-demand | (no task; run manually) | Scope migration, one-time cleanup |

The nightly task will likely accumulate many librarians. The others may have only one or two for a long time. That's fine; the framework supports both.

### Dependency ordering

Within a cadence group, `depends_on` determines execution order. The runner topologically sorts the registered librarians and executes in dependency order. Circular dependencies are detected and reported as errors.

### Error handling

- If a librarian fails, log the error and continue with the next one
- Each librarian's exit status is recorded in the run log
- A librarian that fails 3 consecutive runs gets flagged (not disabled) in the registry
- The health summary surfaces failures so users (or agents) can investigate

### Scope-level librarians

The convention base defines global librarians (nightly index, version cleanup). A scope's `librarians/` folder can define scope-specific librarians too. The install-librarian skill handles both: it reads the definition and registers it in the global registry regardless of where the definition lives.

Discovery: the install-librarian skill can scan for unregistered definitions. The nightly index could also report "librarian definitions found but not registered" as a health signal.

### Registry schema

```json
{
  "librarians": [
    {
      "name": "nightly-index",
      "cadence": "nightly",
      "implementation": "python-script",
      "script": "scheduled-tasks/substrate-index/index.py",
      "depends_on": [],
      "enabled": true,
      "source": "exfu/v0.3/ontology/librarian/nightly-index.md",
      "installed": "2026-06-10T14:00:00Z",
      "last_run": "2026-06-11T02:00:00Z",
      "last_status": "success",
      "last_duration_ms": 450,
      "consecutive_failures": 0
    }
  ],
  "cadences": {
    "nightly": {
      "scheduled_task": "nightly-librarians",
      "last_run": "2026-06-11T02:00:00Z"
    }
  }
}
```

### Run log

Each execution appends to `exfu/derived/librarian-log.json`:

```json
{
  "runs": [
    {
      "cadence": "nightly",
      "started": "2026-06-11T02:00:00Z",
      "finished": "2026-06-11T02:00:02Z",
      "results": [
        {"name": "nightly-index", "status": "success", "duration_ms": 450},
        {"name": "inbox-summary", "status": "success", "duration_ms": 1200}
      ]
    }
  ]
}
```

Capped at 90 days of history to prevent unbounded growth.

### Pause/disable

A librarian can be disabled in the registry without removing its definition. The install-librarian skill supports `disable` and `enable` verbs. Disabled librarians are skipped by the runner but remain visible in the health summary.

### Health summary

An agent (or the dashboard) can read the registry + log and answer:
- What librarians are registered?
- When did each last run, and was it successful?
- Are any failing? How many consecutive failures?
- Are there librarian definitions that aren't installed?
- Which cadences are active?

## What

### T3 plans

| T3 | What it delivers |
|---|---|
| `T3-librarian-definitions.md` | Update convention base with structured YAML format, create registry schema, update existing definitions |
| `T3-nightly-runner.md` | Build the cadence-based runner, refactor index.py to be callable from it, create nightly-librarians scheduled task |
| `T3-install-librarian-skill.md` | Skill to register/unregister/enable/disable librarians, scan for unregistered definitions |

### Trade-offs

- **Registry file vs scan-on-run.** The runner could scan the substrate for definitions on every run instead of maintaining a registry. Simpler, but slower and can't track state (last run, failures, enabled/disabled). We pick the registry.
- **One runner per cadence vs one universal runner.** A universal runner checks all cadences and decides what's due. Simpler deployment but harder to reason about scheduling. We pick per-cadence: each scheduled task runs its own cadence, delegating timing to the scheduler.
- **Python runner vs skill-based runner.** A Python runner is simpler and more reliable for script-type librarians. Skill-type librarians need Claude, which means a different execution path. The runner dispatches by implementation type: scripts run directly, skills are flagged for the next interactive session.

### Open questions

1. **Skill-type librarian execution.** If a librarian needs Claude's judgment (e.g. inbox triage), it can't run as a cron job. Options: (a) queue it and surface it at next session start, (b) use a headless Claude session, (c) restrict the framework to script-type only for scheduled runs. Probably (a) for now.
2. **Log rotation.** 90-day cap is a guess. May need tuning based on actual log volume.
3. **Multi-substrate.** If a user has multiple substrates (work + personal), each has its own registry and runner. No cross-substrate coordination needed for now.

---

## Where this plan lives

- This file: `plugin/planning/T2-librarian-framework.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md` (phase 2)
- Convention base librarian definitions: `plugin/src/shared/substrate/exfu/v0.3/ontology/librarian/`
