---
name: nightly-agents
description: Scheduled task in which Claude runs all registered nightly scheduled agents -- librarians (substrate maintenance) first, then business agents (the user's recurring domain work). Scheduled agents are agent instructions -- Claude reads each due definition and carries out the work itself, calling scripts as tools where a definition says to. A small helper handles the deterministic chores (what is due, recording outcomes). The nightly index is typically the first to run.
---

# Nightly Agents Scheduled Task

## Why this task exists

Two kinds of recurring work want to happen overnight without the user asking. Substrates drift without maintenance: indexes go stale, inboxes silt up, old convention versions linger -- that's the librarians' remit. And users delegate standing domain work -- scan the listings, draft the digest, watch the mailbox -- that's the business agents' remit. Both are defined the same way: as *agent instructions*, markdown files an agent reads cold and acts on.

The scheduled session is the execution environment: Claude is the scheduled agent. Scripts referenced by a definition (the index walker, the dashboard generator) are tools the agent calls, not the work itself.

One scheduled task covers the whole nightly cadence. Adding a new nightly librarian or business agent means registering it, not creating another scheduled task. Librarians run before business agents, so the substrate is tidy and the index fresh before domain work consumes them.

## How it works

A helper script handles the two deterministic chores around the agentic work:

- `agents.py due <root> nightly` -- which scheduled agents are due, in run order (librarians first, then dependencies), with definition paths and health notes
- `agents.py record <root> <name> --status ... --detail ...` -- update registry health and append to the run log

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

You are the nightly scheduled-agent session for the ExFu substrate at [SUBSTRATE_ROOT].

Scheduled agents are recurring jobs defined as agent instructions. Some are librarians (they maintain the substrate itself); some are business agents (they do the user's recurring domain work). You are the agent for all of them: you read each due definition and carry out its instructions yourself. Where a definition tells you to run a script, that script is a tool -- run it, check the result, and apply judgment to what comes back.

1. Find out what is due:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/agents.py due [SUBSTRATE_ROOT] nightly
```

2. For each scheduled agent listed, in the order given:
   - Read its definition file (the `definition:` path in the output). The body below the frontmatter is your instructions.
   - Do the work the definition describes.
   - Record the outcome before moving to the next one:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/agents.py record [SUBSTRATE_ROOT] <name> --status success|failure|skipped --detail "one line of what happened"
```

3. If one fails: record the failure with what went wrong, record anything that depends on it as skipped, and continue with the independent ones. Do not try to repair a failing definition -- that needs an interactive session with the user.

4. Finish with a short summary: what ran, what changed, and anything that needs the user's attention.

Write only inside [SUBSTRATE_ROOT], except where a business agent's definition explicitly directs work in an external tool the user has connected. Treat the plugin's scripts as read-and-execute tools.

---

## After the task runs

The registry (`exfu/derived/agent-registry.json`) carries per-agent health; the log (`exfu/derived/agent-log.json`) carries the run history with one detail line per outcome. The exfu-library skill reads these at session start and surfaces failures or items needing attention. You don't need to check manually unless you want to.

## Other cadences

The registry groups scheduled agents by cadence (nightly, weekly, hourly). Each cadence gets one scheduled task of this shape: copy this task with the cadence word swapped (e.g. `weekly-agents`, scheduled weekly) when the first agent of a new cadence is registered. The install-scheduled-agent skill tells you when that's needed.

## Testing

To exercise it without waiting for the schedule, give any interactive substrate-aware session the task prompt above. The helper alone can be smoke-tested directly:

```
python3 [PATH_TO_PLUGIN]/scheduled-tasks/scheduled-agents/agents.py due [SUBSTRATE_ROOT] nightly
```

It prints the due list without changing anything.

## Privacy note

The session reads and writes only within your substrate (and any external tools a business agent's definition explicitly uses). Scripts run locally. No data leaves your machine beyond what those connected tools involve.
