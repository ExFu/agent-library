---
name: nightly-librarians
description: Scheduled task in which Claude runs all registered nightly librarians. Librarians are agent instructions -- Claude reads each due definition and carries out the work itself, calling scripts as tools where a definition says to. A small helper handles the deterministic chores (what is due, recording outcomes). The nightly index is typically the first librarian in this group.
---

# Nightly Librarians Scheduled Task

## Why this task exists

Substrates drift without maintenance: indexes go stale, inboxes silt up, old convention versions linger. Librarians are that maintenance, defined as *agent instructions* -- markdown files an agent reads cold and acts on. The scheduled session is the execution environment: Claude is the librarian. Scripts referenced by a definition (the index walker, the dashboard generator) are tools the agent calls, not the work itself.

One scheduled task covers the whole nightly cadence. Adding a new nightly librarian means registering it, not creating another scheduled task.

## How it works

A helper script handles the two deterministic chores around the agentic work:

- `librarians.py due <root> nightly` -- which librarians are due, in dependency order, with definition paths and health notes
- `librarians.py record <root> <name> --status ... --detail ...` -- update registry health and append to the run log

Everything between those two calls is Claude reading a definition and doing what it says.

## How to enable

1. Open **Claude Desktop**
2. Go to the **Cowork** tab
3. Click **Scheduled** in the left sidebar
4. Click **+ New task** in the upper right
5. Paste the task prompt below (with the path filled in)
6. Set the schedule to **Daily** at **03:00** (or any overnight time that suits you)
7. Click **Save**

## Task prompt

Replace `[SUBSTRATE_ROOT]` with the absolute path to your substrate root folder, then paste:

---

You are the nightly librarian session for the ExFu substrate at [SUBSTRATE_ROOT].

Librarians are maintenance jobs defined as agent instructions. You are the agent: you read each due librarian's definition and carry out its instructions yourself. Where a definition tells you to run a script, that script is a tool -- run it, check the result, and apply judgment to what comes back.

1. Find out what is due:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/nightly-librarians/librarians.py due [SUBSTRATE_ROOT] nightly
```

2. For each librarian listed, in the order given:
   - Read its definition file (the `definition:` path in the output). The body below the frontmatter is your instructions.
   - Do the work the definition describes.
   - Record the outcome before moving to the next one:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/nightly-librarians/librarians.py record [SUBSTRATE_ROOT] <name> --status success|failure|skipped --detail "one line of what happened"
```

3. If a librarian fails: record the failure with what went wrong, record anything that depends on it as skipped, and continue with the independent ones. Do not try to repair a failing librarian -- that needs an interactive session with the user.

4. Finish with a short summary: what ran, what changed, and anything that needs the user's attention.

Write only inside [SUBSTRATE_ROOT]. Treat the plugin's scripts as read-and-execute tools.

---

## After the task runs

The registry (`exfu/derived/librarian-registry.json`) carries per-librarian health; the log (`exfu/derived/librarian-log.json`) carries the run history with one detail line per outcome. The substrate skill reads these at session start and surfaces failures or items needing attention. You don't need to check manually unless you want to.

## Testing

To exercise it without waiting for the schedule, give any interactive substrate-aware session the task prompt above. The helper alone can be smoke-tested directly:

```
python3 [PATH_TO_PLUGIN]/scheduled-tasks/nightly-librarians/librarians.py due [SUBSTRATE_ROOT] nightly
```

It prints the due list without changing anything.

## Privacy note

The session reads and writes only within your substrate. Scripts run locally. No data leaves your machine.
