---
name: install-librarian
description: Manages the lifecycle of librarians -- background maintenance tasks that keep the substrate healthy. Handles registering, unregistering, enabling, disabling, listing, scanning for available definitions, and reporting health. Triggers on "install a librarian", "register a maintenance task", "what librarians are available", "librarian health", "check librarian status", "what background tasks are running", "scan for librarians", "disable the version cleanup librarian", "uninstall nightly-index", or any intent to manage the substrate's automated maintenance layer.
---

# Install Librarian -- v0.3.0

Manages the lifecycle of librarians in the substrate. A librarian is a background maintenance task defined as *agent instructions* -- a markdown file (with YAML frontmatter) that an agent reads and carries out, calling scripts as tools where the definition says to. Each librarian gets registered in a central registry that the scheduled cadence session reads.

This skill is the interface between those definition files and the registry. It does not execute librarians -- that happens in the cadence's scheduled session, where Claude reads each due definition and does the work.

## Hard constraints

1. **Never auto-enable a librarian without user confirmation.** When installing, show what will be registered and ask for confirmation before writing to the registry. The user should always know what background tasks are active.

2. **Never delete librarian definition files.** Uninstalling removes a librarian from the registry. The definition file stays where it is. The user can re-install it later.

3. **Never run librarians from this skill.** This skill reads and writes the registry JSON. Execution belongs to the scheduled cadence session (or to the user explicitly asking for an ad hoc run).

4. **Require substrate access.** The registry lives at `exfu/derived/librarian-registry.json` inside the substrate. If the substrate is not accessible, halt and say so. Do not work from memory or guess at registry contents.

---

## Registry location and schema

The registry file is `exfu/derived/librarian-registry.json` at the substrate root.

### Schema

```json
{
  "librarians": [
    {
      "name": "nightly-index",
      "cadence": "nightly",
      "depends_on": [],
      "enabled": true,
      "source": "exfu/v0.3/ontology/librarian/nightly-index.md",
      "installed": "2026-06-10T14:00:00Z",
      "last_run": null,
      "last_status": null,
      "consecutive_failures": 0
    }
  ],
  "cadences": {
    "nightly": {
      "scheduled_task": "nightly-librarians",
      "last_run": null
    }
  }
}
```

Each librarian entry carries:
- `name` -- unique identifier (kebab-case)
- `cadence` -- when it runs: nightly, weekly, hourly, on-demand
- `depends_on` -- list of librarian names that must run first within the same cadence
- `enabled` -- whether the scheduled session should run it
- `source` -- path to the definition file, relative to substrate root. The definition is the source of truth for what the librarian does; the registry only indexes it.
- `installed` -- ISO 8601 timestamp of when it was registered
- `last_run`, `last_status` -- recorded after each run (success, failure, or skipped) via the `librarians.py record` helper
- `consecutive_failures` -- count of sequential failed runs; reset on success

The `cadences` object maps each cadence name to its backing scheduled task and last run time.

---

## Librarian definition format

A librarian definition is a markdown file with YAML frontmatter. Required fields: `name`, `cadence`, `description`. The body below the frontmatter is the librarian itself: instructions an agent reads cold and carries out at run time.

```yaml
---
name: nightly-index
cadence: nightly
scripts:
  - scheduled-tasks/substrate-index/index.py
reads:
  - "*/scope.md"
writes:
  - "exfu/derived/index.json"
depends_on: []
description: Walks the substrate and regenerates the global scope index
---
```

Optional fields:
- `scripts` -- deterministic tools the instructions call (paths relative to the plugin root). Purely declarative: the body says when and how to run them. A librarian with no scripts is fully agentic.
- `reads` / `writes` -- what the librarian touches, for conflict detection and the dashboard.
- `depends_on` -- librarians that must run first within the same cadence.

---

## Verbs

### install

Register a librarian from its definition file.

**When the user says:** "install the version cleanup librarian", "register the inbox triage task", "add the nightly index librarian"

**Steps:**

1. **Find the definition file.** If the user names a specific file, use that. Otherwise, search for the librarian by name in these locations (in order):
   - `exfu/v0.3/ontology/librarian/` -- convention base definitions
   - `*/librarians/` directories under each scope
   - Any path the user points to

2. **Read and validate the definition.** Check:
   - `name` -- must be present, kebab-case
   - `cadence` -- must be present, one of: nightly, weekly, hourly, on-demand
   - `description` -- must be present
   - The body below the frontmatter must contain actual instructions (an Instructions section or equivalent) -- an empty body means there is nothing for the scheduled session to follow.
   - If the frontmatter lists `scripts`, check each path exists under the plugin root and mention any that don't.

   If validation fails, tell the user what's missing and stop.

3. **Check for conflicts** (see Conflict detection below).

4. **Show what will be registered and ask for confirmation:**
   > "Ready to register **version-cleanup** (weekly cadence). It reads `exfu/derived/index.json` and writes nothing automatically. Confirm?"

5. **On confirmation, add the entry to the registry:**
   - Set `enabled: true`
   - Set `installed` to the current UTC timestamp
   - Set `last_run` and `last_status` to null
   - Set `consecutive_failures` to 0
   - Copy `name`, `cadence`, and `depends_on` from the frontmatter
   - Set `source` to the definition file path relative to substrate root

6. **Check whether a scheduled task exists for this cadence.** Look at the `cadences` object in the registry.
   - If the cadence already has a `scheduled_task` entry, confirm: "Registered version-cleanup (weekly cadence). It will run with the next weekly cycle."
   - If the cadence is new (no entry), add it to `cadences` with `scheduled_task` set to `<cadence>-librarians` and `last_run` as null. Then tell the user they need to create the scheduled task:

     > "Registered version-cleanup. This is the first weekly librarian, so you'll need a weekly scheduled task to run it. Use the task prompt from `scheduled-tasks/nightly-librarians/TASK.md` with the cadence word swapped to `weekly`, and set it up in Cowork's Scheduled tab on a weekly schedule."

7. **Write the updated registry** back to `exfu/derived/librarian-registry.json`. Format the JSON readably (2-space indent).

### uninstall

Remove a librarian from the registry.

**When the user says:** "uninstall the version cleanup librarian", "remove nightly-index from the registry", "deregister that maintenance task"

**Steps:**

1. Find the librarian by name in the registry. If not found, say so and stop.
2. Confirm: "This will remove **version-cleanup** from the registry. The definition file stays untouched. Confirm?"
3. On confirmation, remove the entry from the `librarians` array.
4. Check if this was the last librarian in its cadence group. If so, note it:
   > "version-cleanup was the last weekly librarian. The weekly-librarians scheduled task can be removed from Cowork if you no longer need it."
5. Write the updated registry.

### enable / disable

Toggle a librarian's `enabled` flag without removing it.

**When the user says:** "disable the inbox triage librarian", "pause nightly-index", "re-enable version-cleanup", "turn that maintenance task back on"

**Steps:**

1. Find the librarian by name in the registry. If not found, say so and stop.
2. Toggle the `enabled` flag.
3. Confirm: "Disabled **nightly-index**. It won't run until re-enabled." or "Enabled **version-cleanup**. It will run with the next weekly cycle."
4. Write the updated registry.

### list

Show all registered librarians with their status.

**When the user says:** "what librarians are registered", "show me my maintenance tasks", "list background tasks"

**Steps:**

1. Read the registry.
2. For each librarian, show:
   - Name
   - Cadence
   - Enabled/disabled
   - Last run time and status (or "never run" if null)
   - Consecutive failures (if > 0)
3. Format as a readable list. Example:

   > **Registered librarians:**
   > - **nightly-index** (nightly) -- enabled, last ran 2h ago, healthy
   > - **version-cleanup** (weekly) -- enabled, never run
   > - **inbox-triage** (nightly) -- disabled

### scan

Walk the substrate for librarian definitions not yet in the registry.

**When the user says:** "what librarians are available", "scan for maintenance tasks", "are there any librarians I haven't installed"

**Steps:**

1. Read the registry to get the list of already-installed names.

2. Walk these locations for markdown files with librarian-format YAML frontmatter:
   - `exfu/v0.3/ontology/librarian/` -- convention base definitions
   - `*/librarians/` directories under each scope (check `scopes/*/librarians/`)
   - `exfu/v0.3/librarians/` -- if it exists

3. For each file found, read the YAML frontmatter. A valid librarian definition has at minimum: `name`, `cadence`, `description`, plus an instruction body.

4. Compare against the registry. Report three categories:

   **Available but not installed:**
   > - version-cleanup (weekly) -- "Keeps the exfu/ directory tidy by identifying unreferenced convention versions"

   **Installed and healthy:**
   > - nightly-index (nightly) -- last ran 2h ago, no failures

   **Installed but failing:**
   > - inbox-triage (nightly) -- 3 consecutive failures, last error: "Script not found"

5. If everything is installed and healthy, say so. If there are available definitions not yet installed, offer to install them.

### health

Summarise the health of the librarian system.

**When the user says:** "librarian health", "are my maintenance tasks running", "check librarian status", "anything broken in the background"

**Steps:**

1. Read the registry.

2. Read `exfu/derived/librarian-log.json` if it exists (the run log). This gives recent run history.

3. Report:

   **Per librarian:**
   - Name, cadence, enabled/disabled
   - Last run time and status, plus the detail line from the most recent log entry
   - Consecutive failures (flag any with 3 or more as needing attention)

   **Per cadence:**
   - Which scheduled task backs it
   - When it last ran
   - How many librarians are in the group

   **Alerts:**
   - Any librarian with >= 3 consecutive failures
   - Any cadence that hasn't run in longer than expected (nightly not run in > 36h, weekly not run in > 10 days)
   - Any registered librarian whose source definition file is missing

4. Run a scan (same as the scan verb) and note any unregistered definitions found. Keep this brief -- just counts and names, not full details.

5. If everything is healthy, say so plainly: "All 2 librarians healthy. Nightly cadence last ran 3h ago."

---

## Conflict detection

Before installing, check for three types of conflict:

### Name collision
Another librarian with the same `name` is already in the registry. This is a hard block -- two librarians cannot share a name. Tell the user and stop.

### Write overlap
Another registered librarian has overlapping entries in its `writes` list. This is a warning, not a block. Tell the user which librarian writes to the same paths and let them decide:
> "Note: **nightly-index** also writes to `exfu/derived/index.json`. This could cause conflicts if both run in the same cycle. Proceed anyway?"

### Missing dependency
The librarian's `depends_on` list references a librarian that is not registered. This is a warning. Tell the user:
> "**version-cleanup** depends on **nightly-index**, which is not currently registered. The scheduled session will record it as skipped until that dependency is installed."

If the missing dependency is in a different cadence than the librarian being installed, note that dependency ordering only works within the same cadence:
> "**version-cleanup** (weekly) depends on **nightly-index** (nightly). Dependency order isn't enforced across cadences -- make sure the nightly cadence runs before the weekly one."

---

## Scan and discovery locations

When scanning, walk these paths relative to the substrate root:

1. `exfu/v0.3/ontology/librarian/` -- the convention base ships definitions here. These are the "built-in" librarians.
2. `scopes/*/librarians/` -- individual scopes can define their own librarians for scope-specific maintenance.
3. `exfu/v0.3/librarians/` -- an alternative convention base location.

For each `.md` file found, attempt to parse YAML frontmatter. A file is a valid librarian definition if its frontmatter contains all three required fields: `name`, `cadence`, `description`.

Skip files that don't parse or lack required fields -- they may be documentation (like `what-is-a-librarian.md` or `agent.md`).

---

## Language and tone

- Use "maintenance task" or "background task" when talking to users who haven't adopted the term "librarian". If the user uses "librarian" themselves, mirror it back.
- Never use em-dashes. Use " -- " (space-dash-dash-space) for asides.
- Keep confirmations brief. One sentence for the action, one for the next step if relevant.
- Format JSON readably when writing (2-space indent, trailing newline).

---

## Baseline context

The install conversation (exfu-start or equivalent) pre-registers the **nightly-index** librarian as part of the substrate baseline. That registration happens before this skill is ever invoked. This skill handles everything after that initial setup: additional librarians, lifecycle management, health monitoring, and discovery.

If the user asks to install nightly-index and it's already registered, say so: "nightly-index is already registered and [healthy/has issues]. Did you want to reinstall it?"

---

## Dependencies

- **substrate** skill -- must be loaded for substrate access. This skill reads and writes files in the substrate.
- **Scheduled cadence sessions** -- execute registered librarians: Claude reads each due definition and does the work. See `scheduled-tasks/nightly-librarians/TASK.md`. This skill never executes; it manages the registry those sessions read.
- **Helper** at `${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/nightly-librarians/librarians.py` -- the deterministic chores (`due` lists what's due in dependency order; `record` updates health and the log). Used by the scheduled sessions, not by this skill.
- **Registry** at `exfu/derived/librarian-registry.json` -- the central data store this skill operates on.
- **Log** at `exfu/derived/librarian-log.json` -- read by the health verb for run history.
