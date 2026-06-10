---
name: substrate-index
description: Scheduled task that generates a scope-level JSON index of the substrate. Walks the folder tree, discovers scopes via scope.md files, and writes a fresh map to exfu/derived/index.json. Runs locally; no external dependencies. This standalone task is available for first-run and debugging; in steady state, use the nightly-agents task instead (which runs this as part of the nightly cadence).
---

# Substrate Index Scheduled Task

## What this task does

Runs a Python script that walks your substrate folder tree and writes a fresh JSON index to `exfu/derived/index.json`. The index maps every scope: its tree position, which folder-types are populated, version pins, and parent relationships.

The index gives any agent a whole-substrate picture in one read. No directory walking needed.

## Standalone vs nightly-agents

This task exists in two forms:

1. **Standalone** (this task) -- runs the index script directly. Use for first-run setup and debugging.
2. **Nightly-agents** -- the recommended steady-state approach. The nightly-agents scheduled task runs all registered nightly scheduled agents in run order, including the nightly-index librarian. See `scheduled-agents/TASK.md`.

If you have the nightly-agents task set up, you don't need this standalone task. Both produce the same index.

## How to enable (standalone)

1. Open **Claude Desktop**
2. Go to the **Cowork** tab
3. Click **Scheduled** in the left sidebar
4. Click **+ New task** in the upper right
5. Paste the task prompt below (with the path filled in)
6. Set the schedule to **Daily** at **03:00** (or any overnight time that suits you)
7. Click **Save**

The task runs while Claude Desktop is open. If the machine is asleep at the scheduled time, it runs automatically the next time the app opens.

## Task prompt

Replace `[SUBSTRATE_ROOT]` with the absolute path to your substrate root folder, then paste:

---

Run the substrate index script:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py [SUBSTRATE_ROOT]
```

Report the output. If the script is missing or fails, report the error -- do not attempt to recreate or fix the script.

---

## Finding your substrate root

The substrate root is the folder you selected during your ExFu install -- the one that contains `CLAUDE.md` and folders like `user/`, `scopes/`, `exfu/`. It's also noted in your wow skill.

## After the task runs

Nothing to do. The script writes `exfu/derived/index.json` and prints a brief summary. Agents read the index automatically when they need an orientation pass.

## Testing

After setup, run it manually once to confirm it produces a sensible index:

```
python3 [PATH_TO_PLUGIN]/scheduled-tasks/substrate-index/index.py [SUBSTRATE_ROOT]
```

The script prints how many scopes it indexed, which versions were found, and where the output was written.

## Privacy note

The index is generated locally and written to your substrate. It never leaves your machine. It contains scope names, folder-type status, and version pins -- no file contents, no credentials, no personal data.
