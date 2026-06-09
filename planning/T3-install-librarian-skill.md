# T3 -- Install-librarian skill

A skill that registers, unregisters, enables, and disables librarians in the substrate. The interface between librarian definitions and the runner.

**Parents:** `T2-librarian-framework.md` (domain), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-librarian-definitions (the structured format and registry schema must exist)
**Status:** not started.

---

## Why

Librarian definitions describe what a librarian does. The runner executes what's registered. Something needs to bridge the gap: reading a definition, validating it, adding it to the registry, and ensuring the right scheduled task exists for its cadence. That's the install-librarian skill.

Without it, librarian registration is manual JSON editing. With it, adding a librarian is a conversation: "install the inbox triage librarian" or "what librarians are available but not installed?"

---

## What to build

### 1. Core verbs

The skill supports these actions:

- **install** -- Read a librarian definition, validate the frontmatter, add it to the registry. If the cadence's scheduled task doesn't exist yet, create it.
- **uninstall** -- Remove a librarian from the registry. If it was the last librarian in its cadence group, offer to remove the scheduled task.
- **enable / disable** -- Toggle a librarian's enabled flag without removing it.
- **list** -- Show all registered librarians with their status.
- **scan** -- Walk the substrate for librarian definitions that aren't registered. Report what's available.
- **health** -- Summarise the health of all registered librarians: last run, failures, cadence coverage.

### 2. Registration flow

When the user says "install the version cleanup librarian":

1. Skill finds the definition file (user specifies or skill searches librarians/ folders)
2. Reads and validates YAML frontmatter
3. Checks for conflicts (name collision, write-path overlap with existing librarians)
4. Adds entry to `exfu/derived/librarian-registry.json`
5. Checks if a scheduled task exists for the cadence; creates one if not
6. Confirms to user: "Registered version-cleanup (weekly cadence). It will run with the next weekly cycle."

### 3. Scheduled task creation

When a new cadence group is needed:

1. Check if `scheduled-tasks/<cadence>-librarians/` exists
2. If not, create it with a TASK.md and a runner invocation: `python3 runner.py <root> <cadence>`
3. The runner script itself is shared (lives in nightly-librarians/ or a common location)

### 4. Scan and discovery

The scan verb walks:
- `exfu/v0.3/ontology/librarian/` -- convention base definitions
- `*/librarians/` in each scope -- scope-level definitions
- Any file with librarian-format YAML frontmatter (name + cadence + implementation)

Compares found definitions against the registry. Reports:
- "Found but not installed: version-cleanup (weekly)"
- "Installed and healthy: nightly-index (nightly, last ran 2h ago)"
- "Installed but failing: inbox-triage (nightly, 3 consecutive failures)"

### 5. Conflict detection

Before installing, check:
- **Name collision:** another librarian with the same name already registered
- **Write overlap:** another librarian writes to the same paths (warning, not blocking)
- **Missing dependency:** the librarian depends_on a librarian not registered at the same cadence

---

## Acceptance criteria

1. Skill can install a librarian from a definition file into the registry
2. Skill can uninstall, enable, and disable registered librarians
3. Skill creates scheduled tasks for new cadence groups
4. Scan discovers unregistered definitions across the substrate
5. Health summary surfaces failures and stale runs
6. Conflict detection warns on name collision and write overlap
7. All operations update `exfu/derived/librarian-registry.json` correctly

---

## Files to create

- `plugin/src/shared/skills/install-librarian/SKILL.md`
- `plugin/src/shared/skills/install-librarian/` (skill content)

---

## Where this plan lives

- This file: `plugin/planning/T3-install-librarian-skill.md`
- Domain: `plugin/planning/T2-librarian-framework.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
