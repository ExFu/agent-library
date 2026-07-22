---
name: install-scheduled-agent
description: Manages the lifecycle of scheduled agents -- recurring jobs defined as agent instructions that run in scheduled sessions. Covers both kinds -- librarians (substrate maintenance, e.g. the nightly index) and business agents (the user's recurring domain work, e.g. a listings scanner or weekly digest). Handles registering, unregistering, enabling, disabling, listing, scanning for available definitions, and reporting health. Triggers on "install a librarian", "register a scheduled agent", "set up that scanner to run nightly", "register a maintenance task", "what librarians are available", "what's running on a schedule", "agent health", "check librarian status", "scan for scheduled agents", "disable the version cleanup librarian", or any intent to manage the substrate's scheduled automation layer.
---

# Install Scheduled Agent -- v0.3.0

Manages the lifecycle of scheduled agents in the substrate. A scheduled agent is recurring work defined as *agent instructions* -- a markdown file (with YAML frontmatter) that an agent reads and carries out in a scheduled session, calling scripts as tools where the definition says to. There are two kinds with identical mechanics and different remits:

- **Librarians** (kind `librarian`) maintain the substrate itself. Their definitions live in `librarians/` folders.
- **Business agents** (kind `agent`) do the user's recurring domain work. Their definitions live in `scheduled/` folders.

Each gets registered in a central registry that the scheduled cadence session reads. This skill is the interface between definition files and that registry. It does not execute anything -- execution happens in the cadence's scheduled session, where Claude reads each due definition and does the work.

## Hard constraints

1. **Never auto-enable a scheduled agent without user confirmation.** When installing, show what will be registered and ask for confirmation before writing to the registry. The user should always know what runs in the background -- doubly so for business agents, which act on their behalf in their domain.

2. **Never delete definition files.** Uninstalling removes an entry from the registry. The definition file stays where it is. The user can re-install it later. (An unregistered definition is also the normal way to stage work for the user's approval.)

3. **Never run scheduled agents from this skill.** This skill reads and writes the registry JSON. Execution belongs to the scheduled cadence session (or to the user explicitly asking for an ad hoc run).

4. **Require substrate access.** The registry lives at `exfu/derived/agent-registry.json` inside the substrate. If the substrate is not accessible, halt and say so. Do not work from memory or guess at registry contents.

---

## Registry location and schema

The registry file is `exfu/derived/agent-registry.json` at the substrate root.

### Schema

```json
{
  "agents": [
    {
      "name": "nightly-index",
      "kind": "librarian",
      "cadence": "nightly",
      "depends_on": [],
      "enabled": true,
      "source": "exfu/v0.3/librarians/nightly-index.md",
      "installed": "2026-06-10T14:00:00Z",
      "last_run": null,
      "last_status": null,
      "consecutive_failures": 0
    }
  ],
  "cadences": {
    "nightly": {
      "scheduled_task": "nightly-agents",
      "last_run": null
    }
  }
}
```

Each entry carries:
- `name` -- unique identifier (kebab-case)
- `kind` -- `librarian` (substrate maintenance) or `agent` (business logic). Within a cadence, librarians run before business agents.
- `cadence` -- when it runs: nightly, weekly, hourly, on-demand
- `depends_on` -- names that must run first within the same cadence
- `enabled` -- whether the scheduled session should run it
- `source` -- path to the definition file, relative to substrate root. The definition is the source of truth for what the agent does; the registry only indexes it.
- `installed` -- ISO 8601 timestamp of when it was registered
- `last_run`, `last_status` -- recorded after each run (success, failure, or skipped) via the `agents.py record` helper
- `consecutive_failures` -- count of sequential failed runs; reset on success

The `cadences` object maps each cadence name to its backing scheduled task and last run time.

---

## Definition format

A definition is a markdown file with YAML frontmatter. Required fields: `name`, `cadence`, `description`. The body below the frontmatter is the work itself: instructions an agent reads cold and carries out at run time.

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
- `scripts` -- deterministic tools the instructions call (paths relative to the plugin root). Purely declarative: the body says when and how to run them. A definition with no scripts is fully agentic.
- `reads` / `writes` -- what it touches, for conflict detection and the dashboard.
- `depends_on` -- entries that must run first within the same cadence.

**Kind is determined by where the definition lives**, not by a frontmatter field: a definition in a `librarians/` folder (including the convention base's `exfu/<version>/librarians/`) registers as kind `librarian`; a definition in an `scheduled/` folder registers as kind `agent`. If a definition arrives from anywhere else, ask the user which remit it has and suggest moving it to the right folder.

---

## Verbs

### install

Register a scheduled agent from its definition file.

**When the user says:** "install the version cleanup librarian", "register the mx5 scanner", "make that digest run weekly", "add the nightly index"

**Steps:**

1. **Find the definition file.** If the user names a specific file, use that. Otherwise, search for it by name in these locations (in order):
   - `exfu/<version>/librarians/` -- convention base shipped librarians (resolve `<version>` via `exfu/latest.txt`)
   - `*/librarians/` and `*/scheduled/` directories under each scope (use the index at `exfu/derived/index.json` to find scopes)
   - Any path the user points to

2. **Read and validate the definition.** Check:
   - `name` -- present, kebab-case
   - `cadence` -- present, one of: nightly, weekly, hourly, on-demand
   - `description` -- present
   - The body below the frontmatter contains actual instructions -- an empty body means there is nothing for the scheduled session to follow.
   - If the frontmatter lists `scripts`, check each path exists under the plugin root and mention any that don't.

   If validation fails, tell the user what's missing and stop.

3. **Determine kind from the definition's location** (librarians/ -> `librarian`, scheduled/ -> `agent`).

4. **Check for conflicts** (see Conflict detection below).

5. **Show what will be registered and ask for confirmation:**
   > "Ready to register **mx5-scanner** (business agent, nightly cadence). It reads the hunt brief and dealer listings, and writes to the sightings database. Confirm?"

6. **On confirmation, add the entry to the registry:**
   - Set `kind` from step 3, `enabled: true`, `installed` to the current UTC timestamp
   - Set `last_run` and `last_status` to null, `consecutive_failures` to 0
   - Copy `name`, `cadence`, and `depends_on` from the frontmatter
   - Set `source` to the definition file path relative to substrate root

7. **Check whether a scheduled task exists for this cadence.** Look at the `cadences` object in the registry.
   - If the cadence already has a `scheduled_task` entry, confirm: "Registered mx5-scanner. It will run with the next nightly cycle."
   - If the cadence is new (no entry), add it to `cadences` with `scheduled_task` set to `<cadence>-agents` and `last_run` null. Then tell the user they need to create the scheduled task:

     > "Registered weekly-digest. This is the first weekly scheduled agent, so you'll need a weekly scheduled task to run it. Use the task prompt from `scheduled-tasks/scheduled-agents/TASK.md` with the cadence word swapped to `weekly`, and set it up in Cowork's Scheduled tab on a weekly schedule."

8. **Write the updated registry** back to `exfu/derived/agent-registry.json`. Format the JSON readably (2-space indent).

### uninstall

Remove an entry from the registry.

**When the user says:** "uninstall the version cleanup librarian", "stop the scanner", "deregister that"

**Steps:**

1. Find the entry by name in the registry. If not found, say so and stop.
2. Confirm: "This will remove **version-cleanup** from the registry. The definition file stays untouched. Confirm?"
3. On confirmation, remove the entry from the `agents` array.
4. Check if this was the last entry in its cadence group. If so, note it:
   > "version-cleanup was the last weekly scheduled agent. The weekly-agents scheduled task can be removed from Cowork if you no longer need it."
5. Write the updated registry.

### enable / disable

Toggle an entry's `enabled` flag without removing it.

**When the user says:** "disable the inbox triage librarian", "pause the scanner", "turn the digest back on"

**Steps:**

1. Find the entry by name. If not found, say so and stop.
2. Toggle the `enabled` flag.
3. Confirm: "Disabled **mx5-scanner**. It won't run until re-enabled." or "Enabled **version-cleanup**. It will run with the next weekly cycle."
4. Write the updated registry.

### list

Show all registered scheduled agents with their status.

**When the user says:** "what's running on a schedule", "show me my scheduled agents", "list background tasks", "what librarians are registered"

**Steps:**

1. Read the registry.
2. For each entry, show: name, kind, cadence, enabled/disabled, last run time and status (or "never run"), consecutive failures (if > 0).
3. Format as a readable list, librarians first. Example:

   > **Scheduled agents:**
   > - **nightly-index** (librarian, nightly) -- enabled, last ran 2h ago, healthy
   > - **version-cleanup** (librarian, weekly) -- enabled, never run
   > - **mx5-scanner** (business agent, nightly) -- disabled

### scan

Walk the substrate for definitions not yet in the registry.

**When the user says:** "what scheduled agents are available", "scan for maintenance tasks", "are there any agents I haven't installed"

**Steps:**

1. Read the registry to get the list of already-installed names.

2. Walk these locations for markdown files with scheduled-agent frontmatter:
   - `exfu/<version>/librarians/` -- convention base shipped librarians
   - `*/librarians/` and `*/scheduled/` directories under each scope (the index gives you the scope list; check both folders per scope)

3. For each file found, read the YAML frontmatter. A valid definition has at minimum: `name`, `cadence`, `description`, plus an instruction body. Skip files that don't parse or lack required fields -- they may be documentation (like `agent.md`).

4. Compare against the registry. Report three categories:

   **Available but not installed:**
   > - mx5-scanner (business agent, nightly) -- "Scans dealer listings against the hunt brief and updates the sightings database"

   **Installed and healthy:**
   > - nightly-index (librarian, nightly) -- last ran 2h ago, no failures

   **Installed but failing:**
   > - inbox-triage (librarian, nightly) -- 3 consecutive failures, last error: "Script not found"

5. If everything is installed and healthy, say so. If there are available definitions not yet installed, offer to install them.

### health

Summarise the health of the scheduled-agent system.

**When the user says:** "agent health", "are my scheduled tasks running", "anything broken in the background"

**Steps:**

1. Read the registry.

2. Read `exfu/derived/agent-log.json` if it exists (the run log) for recent history.

3. Report:

   **Per entry:** name, kind, cadence, enabled/disabled, last run time and status plus the detail line from the most recent log entry, consecutive failures (flag 3+ as needing attention).

   **Per cadence:** which scheduled task backs it, when it last ran, how many entries are in the group.

   **Alerts:**
   - Any entry with >= 3 consecutive failures
   - Any cadence that hasn't run in longer than expected (nightly not run in > 36h, weekly not run in > 10 days)
   - Any registered entry whose source definition file is missing

4. Run a scan (same as the scan verb) and note any unregistered definitions found. Keep this brief -- counts and names, not full details.

5. If everything is healthy, say so plainly: "All 3 scheduled agents healthy. Nightly cadence last ran 3h ago."

---

## Conflict detection

Before installing, check for three types of conflict:

### Name collision
Another entry with the same `name` is already in the registry. Hard block -- two scheduled agents cannot share a name. Tell the user and stop.

### Write overlap
Another registered entry has overlapping `writes` paths. Warning, not a block. Tell the user which entry writes to the same paths and let them decide:
> "Note: **nightly-index** also writes to `exfu/derived/index.json`. This could cause conflicts if both run in the same cycle. Proceed anyway?"

### Missing dependency
The entry's `depends_on` references a name that is not registered. Warning:
> "**version-cleanup** depends on **nightly-index**, which is not currently registered. The scheduled session will record it as skipped until that dependency is installed."

If the missing dependency is in a different cadence, note that dependency ordering only works within the same cadence:
> "**version-cleanup** (weekly) depends on **nightly-index** (nightly). Dependency order isn't enforced across cadences -- make sure the nightly cadence runs before the weekly one."

---

## Language and tone

- With users who haven't adopted the internal terms, say "maintenance task" for librarians and "background helper" or "standing job" for business agents. If the user uses "librarian" or "scheduled agent" themselves, mirror it back.
- Never use em-dashes. Use " -- " (space-dash-dash-space) for asides.
- Keep confirmations brief. One sentence for the action, one for the next step if relevant.
- Format JSON readably when writing (2-space indent, trailing newline).

---

## Baseline context

The install conversation (exfu-start or equivalent) pre-registers the **nightly-index** librarian as part of the substrate baseline, copying the starter registry from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/agent-registry.json`. That happens before this skill is ever invoked. This skill handles everything after: additional librarians, business agents, lifecycle management, health monitoring, and discovery.

If the user asks to install nightly-index and it's already registered, say so: "nightly-index is already registered and [healthy/has issues]. Did you want to reinstall it?"

---

## Dependencies

- **substrate** skill -- must be loaded for substrate access. This skill reads and writes files in the substrate.
- **Scheduled cadence sessions** -- execute registered entries: Claude reads each due definition and does the work. See `scheduled-tasks/scheduled-agents/TASK.md`. This skill never executes; it manages the registry those sessions read.
- **Helper** at `${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/agents.py` -- the deterministic chores (`due` lists what's due in run order; `record` updates health and the log). Used by the scheduled sessions, not by this skill.
- **Registry** at `exfu/derived/agent-registry.json` -- the central data store this skill operates on.
- **Log** at `exfu/derived/agent-log.json` -- read by the health verb for run history.
