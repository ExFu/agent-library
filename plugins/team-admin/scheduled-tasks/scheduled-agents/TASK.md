---
name: nightly-agents
description: Scheduled task in which Claude runs all registered nightly scheduled agents -- librarians (substrate maintenance) first, then business agents (the user's recurring domain work). Scheduled agents are agent instructions -- Claude reads each due definition and carries out the work itself, calling scripts as tools where a definition says to. A small helper handles the deterministic chores (what is due, recording outcomes). The nightly index is typically the first to run.
---

# Nightly Agents Scheduled Task

## Why this task exists

Two kinds of recurring work want to happen overnight without the user asking. Substrates drift without maintenance: indexes go stale, agent backlogs silt up, dockets fill with closed entries, old convention versions linger -- that's the librarians' remit. And users delegate standing domain work -- scan the listings, draft the digest, watch the mailbox -- that's the business agents' remit. Both are defined the same way: as *agent instructions*, markdown files an agent reads cold and acts on.

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

That is the nightly task. The hourly cadence, which hosts the docket's dispatcher, is a different kind of task: it needs the local filesystem and a cheap model, so it is created as a **Claude Code Desktop local task** rather than in Cowork. See "Hourly task" below.

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

## Hourly task

The hourly cadence exists for one librarian: the dispatcher, which asks the local index what is due, fires each due trigger through the handler and channel it names, and writes a receipt for every fire. On most runs nothing is due and the whole job is one query, so the task must be cheap, and it must see the local filesystem where the index lives. That rules out Cowork's scheduled tasks, which run in the cloud without local files.

### How to enable

1. Open **Claude Desktop**
2. Go to the **Code** tab
3. Open **Routines**, then **Local**
4. Create a new local task and paste the hourly prompt below (with the path filled in)
5. Set the schedule to **Hourly**
6. In the task's **model picker**, select the **cheapest model** available -- the dispatcher runs against the local index and usually has nothing to do
7. Save

A local task runs only while the app is open and the machine is awake; a missed slot gets exactly one catch-up run, which matches the dispatcher's own misfire rule (fire the most recent elapsed occurrence, record the rest as skipped, never backfill). If you only use Cowork, skip this task: the session-start check delivers the same items when you next open a session, and the dashboard shows what is waiting.

### Hourly task prompt

Replace `[SUBSTRATE_ROOT]` with the absolute path to your substrate root folder, then paste:

---

You are the hourly scheduled-agent session for the ExFu substrate at [SUBSTRATE_ROOT].

Scheduled agents are recurring jobs defined as agent instructions. Some are librarians (they maintain the substrate itself); some are business agents (they do the user's recurring domain work). You are the agent for all of them: you read each due definition and carry out its instructions yourself. Where a definition tells you to run a script, that script is a tool -- run it, check the result, and apply judgment to what comes back.

Three constraints hold for the whole session, because the hourly cadence hosts the dispatcher:

- Do not boot the library. Do not load the boot skill, the user's way of working, `context/`, or any docket entry file. Your inputs are the due view and the trigger rows it names; the `assess` text on a trigger is the whole brief.
- Do not act on a trigger without first writing its intent receipt, and do not leave the run without a result receipt for everything you attempted.
- Do not send through a channel marked `send: auto` unless `durable/ledger/grants.md` holds an active grant for it, the channel is a `dm`, and its target is the trigger's owner. Everything else is drafted.

1. Find out what is due:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/agents.py due [SUBSTRATE_ROOT] hourly
```

2. For each scheduled agent listed, in the order given:
   - Read its definition file (the `definition:` path in the output). The body below the frontmatter is your instructions.
   - Do the work the definition describes.
   - Record the outcome before moving to the next one:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/agents.py record [SUBSTRATE_ROOT] <name> --status success|failure|skipped --detail "one line of what happened"
```

3. If one fails: record the failure with what went wrong, record anything that depends on it as skipped, and continue with the independent ones. Do not try to repair a failing definition -- that needs an interactive session with the user.

4. Finish with a short summary: what ran, what fired, and anything that needs the user's attention. If nothing was due, say so in one line.

Write only inside [SUBSTRATE_ROOT] and the per-machine index directory the tools name, except where a definition explicitly directs delivery through a connector the user has connected. Treat the plugin's scripts as read-and-execute tools.

---

## After the task runs

The registry (`exfu/derived/agent-registry.json`) carries per-agent health; the log (`exfu/derived/agent-log.json`) carries the run history with one detail line per outcome. The exfu-library skill reads these at session start and surfaces failures or items needing attention. You don't need to check manually unless you want to.

## Other cadences

The registry groups scheduled agents by cadence (nightly, weekly, hourly). Each cadence gets one scheduled task of this shape: copy this task with the cadence word swapped (e.g. `weekly-agents`, scheduled weekly) when the first agent of a new cadence is registered. The hourly cadence is the exception already written out above: same mechanics, but a Desktop local task with the cheapest model and the dispatcher's three constraints. The install-scheduled-agent skill tells you when a new cadence's task is needed and which kind it should be.

## Testing

To exercise it without waiting for the schedule, give any interactive substrate-aware session the task prompt above. The helper alone can be smoke-tested directly:

```
python3 [PATH_TO_PLUGIN]/scheduled-tasks/scheduled-agents/agents.py due [SUBSTRATE_ROOT] nightly
```

It prints the due list without changing anything.

## Privacy note

The session reads and writes only within your substrate (and any external tools a business agent's definition explicitly uses). Scripts run locally. No data leaves your machine beyond what those connected tools involve.
