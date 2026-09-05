---
name: exfu-guides
description: ExFu is a Claude setup tool that installs an Agent Library -- a persistent knowledge base kept organised by Agent Librarians, implemented as a scope-based substrate with folder-types, scheduled agents, and convention versioning. This skill answers questions about how that setup works. Load it when the user asks how something in their Claude setup works, wants a concept explained, or is trying to understand why things are structured the way they are. Triggers on "how does this all work?", "what is the Agent Library?", "what are librarians?", "what is the substrate?", "what is a scope?", "what are folder-types?", "how do librarians work?", "what is a scheduled agent?", "what is the convention base?", "what does store-or-point mean?", "what is wow?", "how does versioning work?", "what is the global index?", "what is the docket?", "how do I add a new scope?", "what is the user scope?", "what's the dashboard?", or any other question about the substrate's design or architecture.
---

# ExFu Guides -- reference for the scope-based substrate

Your job is to answer architecture-level questions well, drawing on the reference material that ships with this plugin. You're a knowledgeable guide, not a search interface. Pull the relevant content, paraphrase for the question, and point at the canonical source if the user wants depth.

## Hard constraints

- Never use em-dashes. Use " -- " instead.
- Do not reproduce entire documents verbatim. Read, then answer the actual question.
- Do not send the user to fetch a URL. All reference content is local in this plugin.
- Do not make up facts about how the substrate works. If you're uncertain, say so and point at the canonical source.
- Do not turn this into a lecture. Answer what was asked. Offer to go deeper if they want.

## Reference content index

The following files ship in this plugin. Read the relevant one before answering:

- `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` -- the definitive reference for the substrate architecture. Start here for most architecture questions.
- `${CLAUDE_PLUGIN_ROOT}/resources/the-substrate-primer.md` -- a lighter human-facing introduction. Useful for orienting someone earlier in their learning.
- `${CLAUDE_PLUGIN_ROOT}/resources/exfu-primer.md` -- what ExFu is, what the install delivers, how it fits into the broader Claude ecosystem.
- `${CLAUDE_PLUGIN_ROOT}/resources/teaching-artefacts.md` -- index of diagrams and interactive widgets. When a visual would help, check here first.
- `${CLAUDE_PLUGIN_ROOT}/resources/ecosystem-references.md` -- catalogue of Anthropic and community resources. Use when the question is better answered by an external resource.

For convention base content (the canonical definitions agents follow). The plugin ships exactly one convention version at `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/` -- list that directory to resolve `<version>`:

- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` -- the complete core ontology in ONE file: the scope model and scope.md format, every folder-type (with anchors like `#docket`), the docket mechanics (`#records`, `#triggers`, `#signals`, `#fires`, `#actors`, `#channels`, `#grants`, `#dispatcher`), scheduled agents and librarians, the way-of-working concept, and the authoring rules. This is the canonical source for nearly every structural question.
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/principles.md` -- the design principles and tool recommendations (unversioned, beside the version directory).
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/librarians/` -- the shipped librarian definitions (nightly-index, docket-compact, backlog-sweep, dispatcher, dashboard-generator, version-cleanup, library-updater).
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/skills/wow-template.md` -- the way-of-working template.

## The core concepts

These are the twelve concepts the substrate is built on. Know them cold. When a question touches one, read the canonical source before answering -- don't rely on this summary alone.

### 1. Scopes

A scope is a bounded working context. Not an org chart entry -- a container for everything an agent needs to operate in one area of work. A scope could be a client, a project, a team, a department, or anything else the user treats as a distinct context.

Every scope has a `scope.md` with YAML frontmatter (`name`, `purpose`, `parent`, `exfu` version pin). Inside it, a scope can contain up to eight standard folder-types. Scopes nest via a `scopes/` subdirectory -- a scope never holds child scopes loose among its own working folders.

The substrate has three zones at the top level: `exfu/` (plugin-owned definitions; not a scope -- no scope.md), `user/` (the personal scope, unversioned, parent: none), and `scopes/` (everything else). Everything under `scopes/` is either a real scope (has `scope.md`) or a grouping folder (no `scope.md`, purely organisational).

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` (Scope section)

### 2. Folder-types

The eight standard folder-types are the vocabulary of "where things go" inside a scope:

| Folder | What it answers |
|---|---|
| `ontology/` | What do the concepts and terms in this scope mean? |
| `context/` | What background should an agent know? (including kept reference documents) |
| `skills/` | What skill definitions belong to this scope? |
| `librarians/` | What substrate maintenance runs here on a schedule? |
| `scheduled/` | What business-logic work runs here on a schedule? |
| `docket/` | What is open here -- tasks, reminders, things left for agents -- and when and how does it get heard? |
| `databases/` | Where do structured, repeating records live? |
| `visualisations/` | Where do agent-created visual outputs live? |

Three folder-types from earlier versions -- `todo/`, `reminders/`, `inbox/` -- are deprecated: `docket/` replaces all three. A scope that has them keeps working and every reader still understands them, but no new scope creates them and the docket migration offers to convert them scope by scope. Their anchors are kept so old `Follows:` lines resolve.

The catalogue is open -- a scope can add its own types and define them in its `ontology/`. Folder-types materialise only when content exists for them: a scope with just scope.md and context/ is healthy, not incomplete. Each materialised folder-type has an `agent.md` whose `Follows:` line anchors into the core ontology (e.g. `Follows: exfu/20260903-1825/ontology.md#docket`) and lists only local deviations. Descriptors never carry state ("currently empty" is banned -- it goes stale).

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` (Folder-types section)

### 3. Convention base

The convention base lives at `exfu/` inside the substrate, and splits in two. The **contract** is `exfu/<version>/ontology.md` (`exfu/latest.txt` names the current version): the default definitions for all folder-types and the scope model, frozen the moment it ships. Everything else the plugin supplies -- `exfu/readme.md`, `exfu/principles.md`, `exfu/librarians/`, `exfu/skills/` -- sits unversioned beside it and moves with plugin releases.

The rule deciding which is which: *a file belongs in a version directory if and only if a `Follows:` line can anchor into it.* Only the ontology qualifies, so only the ontology is frozen. That is what lets the conventions stay genuinely locked while documentation, shipped librarians, and templates keep evolving -- and it keeps registry `source` paths stable, because librarian definitions no longer move when a version is minted.

Scopes reference the contract via `Follows:` lines in their `agent.md` files, anchored into the single ontology file (`Follows: exfu/20260903-1825/ontology.md#context`). A standard folder with no deviations is tiny -- the protective header plus that one line. The base ships with the plugin at `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/` and gets installed into the user's substrate. It is deliberately flat and small so it can be ingested in a handful of reads. Bases shipped before `20260903-1825` hold all four unversioned items inside the version directory instead; that is the older shape.

### 4. Store-or-point

Every folder-type either stores data locally (files in the folder) or points to an external tool. In the docket the choice is per file: a `docket/` may hold a `todo.jsonl`, or its `agent.md` may say `todo: tracked in ClickUp, not stored locally` while `reminders.jsonl` stays local. A `databases/` folder may hold records, or say "contacts live in HubSpot".

Both are equally valid. The convention guarantees the location is discoverable -- an agent always knows where to ask about tasks, reminders, context, etc. for any scope. Whether the data lives there is per-scope, per-user.

This is visible in the global index: each folder-type shows as `data` (files here), `pointer` (data elsewhere), or `empty` (folder exists but nothing in it yet), and the docket reports that status per file.

### 5. Scheduled agents (librarians and business agents)

Scheduled agents are recurring jobs defined as agent instructions: a markdown definition file an agent reads cold and carries out on a cadence, calling scripts as tools where the definition says to. Two kinds share identical mechanics and differ only in remit:

- **Librarians** maintain the substrate itself (sweep the agent backlog, compact the docket, dispatch due reminder rules, regenerate the index, flag stale versions). Definitions live in `librarians/` folders.
- **Business agents** do the user's recurring domain work (scan listings, draft a weekly digest, watch a mailbox). Definitions live in `scheduled/` folders.

Cadences: nightly, weekly, hourly, or on-demand. The nightly index is the canonical librarian -- it walks the entire substrate and regenerates `exfu/derived/index.json`. The hourly cadence hosts the dispatcher, and is created as a Claude Code Desktop local task with the cheapest model because it needs the local index and usually finds nothing due.

The registry at `exfu/derived/agent-registry.json` tracks all registered scheduled agents, their kind, cadence, last run times, and status. One scheduled task per cadence runs them: librarians first, then business agents, then dependency order. Each outcome is recorded to `exfu/derived/agent-log.json`. A definition that exists but isn't registered does nothing -- registration (via the install-scheduled-agent skill) is what makes it live.

ExFu ships seven librarian definitions: nightly-index, docket-compact, backlog-sweep and dispatcher (registered by default at install), plus dashboard-generator, version-cleanup, and library-updater (which is not scheduled at all; the boot skill hands it pending migrations).

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` (Scheduled agents section), shipped definitions in `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/librarians/`

### 6. Versioning

Convention base versions are identified by their release moment: a shortened UTC timestamp to the minute, `YYYYMMDD-HHMM` (e.g. `exfu/20260723-1446/`). No seconds, no timezone suffix, no ISO punctuation. Identifiers deliberately share no naming surface with plugin release numbers, every release mints a fresh identifier (contents never change under a stable name), and lexicographic order is chronological order. Early releases used the legacy `v0.x` scheme (`exfu/v0.3/`); any timestamp identifier is newer than any `v0.x` one.

Versions sit side-by-side under `exfu/`. Each scope pins to a version via the `exfu:` field in its `scope.md`. New scopes default to whatever `exfu/latest.txt` points to. Existing scopes keep their pin until explicitly migrated.

Migration is per-scope, not all-at-once. A substrate can have scopes on different versions simultaneously. The global index tracks which version each scope uses.

Special case: the `user/` scope has no `exfu:` field -- it always reads through `latest`.

### 7. The global index

`exfu/derived/index.json` -- generated nightly by the index librarian. One read gives the whole substrate map:

- Every scope, its tree position, and parent relationships
- Folder-type status per scope (data / pointer / empty)
- ExFu version pins per scope
- Which convention base versions are in use

The index serves two consumers: agents (fast orientation without walking the filesystem) and the dashboard (visual rendering). It is never hand-edited -- it's regenerated on every nightly run.

`exfu/derived/` holds only **text** caches -- the global index, the agent registry and log, the connector availability map (`channels.json`), and the docket's due view (`due.json`) -- because it syncs with the library and a phone reads it through the storage connector. The **search index** is different: it is a SQLite file, and nothing binary is ever written inside the library (Dropbox and git sync its sidecars independently and produce unmergeable conflicts). It lives per machine, outside the synced root, at `~/.exfu/derived/<library-id>/library.sqlite`, where `library-id` is a short hash of the library's root path (`EXFU_DERIVED_DIR` overrides the location). It is rebuilt from the JSONL records incrementally by content hash and is never a source of truth: a moved library simply rebuilds it, and a phone never touches it.

### 8. The user/ scope

The personal scope. Always exists at the substrate root alongside `exfu/` and `scopes/`. Contains about-me context, ways of working, personal preferences, and personal ontology that apply across every scope.

`user/` is not a working scope -- it's who the user is. It has no `exfu:` version pin (always reads through `latest`), no `parent` (it sits at the root), and its content travels with the user across every context.

### 9. The permanent record

`durable/` at the root holds the facts about the library itself that nothing can regenerate: which migrations have been applied, when the library was created and by which version, which channels the user has allowed to send on their behalf without asking (`ledger/grants.md`; the dispatcher checks it before every automatic send, so a flag on the channel grants nothing by itself), and who the library acts as (`ledger/actors.md`: the canonical handle triggers carry as `owner`, plus every alias and medium id that resolves to it, so a trigger written under a display name still fires). Its first tenant is the logbook at `durable/ledger/`. Not a scope, not a folder-type.

It exists because every other home is wrong. `exfu/` is replaced wholesale when the plugin updates. `exfu/derived/` is a cache that is safe to delete and rebuild. So the rule every skill states is positive rather than a list of exceptions: **a refresh replaces `exfu/`; it never touches `durable/`, `user/`, or `scopes/`.**

Three tests decide what may go there, all required: unregenerable (delete it, run every librarian twice, see whether it comes back -- being expensive to recompute is not the same thing), about the library rather than the world (a CRM belongs in a scope's `databases/`), and append-only human-readable text (which is what keeps databases and binaries out, since libraries sync through Dropbox or git).

**With users, call it their "permanent record" and the ledger their "logbook".** Never say "durable" to a user. If they ask what to back up, this is the answer: nothing else in the library is irreplaceable.

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` (#durable)

### 10. The wow skill

The user's personal navigation map and thin always-on kernel. Generated during install by the `exfu-create-wow` skill, updated as the substrate evolves.

`wow` does two things: (1) maps out where the substrate is laid out so a new session can find everything without being told, and (2) carries a small set of universal instructions (communication preferences, formatting rules, always-on behaviours).

It's a living document. Small updates happen directly; substantial changes (new scopes, restructured folders) warrant a full regeneration via `exfu-create-wow`.

### 11. The dashboard

When available, a static HTML page at `exfu/visualisations/dashboard/` that renders the global index into a visual substrate map. Shows the scope tree, folder-type status, ontology chains, and librarian health. Read from the index, not by walking the filesystem live -- so it's fast and works offline.

Tell users to open `dashboard.html` at the top of their library rather than the path above: it is a small generated redirect that lands them on the real page, and it is the one place they can be expected to find without instructions. The bundle stays in the gallery, where visual outputs belong.

Target audience is non-technical users. The dashboard is generated as part of the nightly index run or on-demand.

### 12. The docket

`docket/` is the one folder-type for what is open in a scope: tasks (`todo.jsonl`), reminders (`reminders.jsonl`), and things the user leaves for their agents to attend to (`agent-backlog.jsonl` -- a queue for agents, never the user's own in-tray). One JSONL file per collection rather than one file per item, so an agent reads a whole collection in one call from any surface, including a phone through the storage connector. The files appear on their first entry.

Every entry has the same deliberately thin shape: `title`, `notes` for people, `agent_notes` (freeform instructions for agents: timing, conditions, "only show when"), `status` (`open | done | archived`), optional `keywords` written by the saving agent as the search layer that needs no model, and an envelope of library-wide `id`, `created`, `updated`, `revision`. There are no priority, tag, dependency or recurrence columns; those live in `agent_notes` as prose. Anything a program must read is a **mixin**: a separate JSONL file whose rows point at a record by id.

The docket's mechanics sit beside the entries in the same folder:

- **Triggers** (`triggers.jsonl`) say when and how a matter gets heard: a schedule (`once`, `cron`, or `on-signal`), an `assess` brief in prose, a handler (deliver it, spin up a sub-agent at a stated weight, or run a registered definition), a channel, and an owner. A reminder is an entry with a trigger; a trigger need not point at an entry at all.
- **Signals** (`signals.jsonl`) are facts an agent recorded for whoever listens; any trigger can be armed on a signal name, which is how two-step workflows form without either step knowing about the other.
- **Fire receipts** (`fires.jsonl`) record every firing, intent before acting and result after, so nothing fires twice and a crash leaves a visible half-receipt.
- **Channels** (`channels.jsonl`) are how the scope reaches people: `dm` to one person, `broadcast` to several, or `pull` (the dashboard and session start, always present). Each is `draft` by default; `auto` sending requires a grant in the permanent record.

The **dispatcher** librarian, on the hourly cadence, is what makes triggers fire: it refreshes the index, asks for the due view, and for each due trigger writes the intent receipt, does what the handler says, and writes the result. It never boots the library. The boot skill runs the same due check at session start, so someone in Claude several times a day is served faster than any cron.

One generated personal skill, `<user>-docket` (from `setup-docket`), captures, reminds, completes and snoozes against the docket on both the filesystem and connector backends. It replaces the separate reminders and inbox skills of earlier releases.

With users: "your docket", "a reminder rule", "something happened" (a signal), "tell me" / "tell the team" (channel kinds), "prepare only" / "send automatically" (`draft` / `auto`). The schema words stay internal.

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` (#docket and #docket-mechanics)

## How to handle common question types

**"What is the substrate?"**
Read the primer or the guide intro. Give a one-paragraph answer in plain language. Offer to go deeper on any part.

**"What is a scope?" / "How do I create one?"**
Summarise: a bounded working context with a predictable internal shape. Has `scope.md` with frontmatter, contains folder-types, nests via `scopes/`. The four top-level zones are `exfu/`, `durable/`, `user/`, and `scopes/`. Read the Scope section of `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/<version>/ontology.md` for the format spec. Creating one is the scope-setup skill's job.

**"What are folder-types?" / "What goes where?"**
The eight standard types answer "how does this scope handle this kind of thing?" Walk through the table above. Emphasise that each is a discovery convention -- the data might live locally or in an external tool. If the user has `todo/`, `reminders/` or `inbox/` folders, they are on the deprecated shape: still understood, and the migration converts them when they choose.

**"How does store-or-point work?"**
A folder either stores data or says where the data actually lives. Both are valid. The point is that an agent always knows where to ask. Use the docket's task file as the clearest example -- most users already have a task manager, so `todo` becomes a pointer line while reminders stay local.

**"What is the docket?" / "How do reminders work?"**
One folder for what is open: tasks, reminders, and things left for agents, one line per entry. A reminder is an entry plus a reminder rule (a trigger) saying when and how it gets heard; the dispatcher fires due rules every hour and the session-start check catches the rest. Read concept 12 above, then #docket-mechanics in the core ontology for depth.

**"How do librarians work?" / "What's a scheduled agent?"**
Recurring jobs defined as agent instructions, run by one scheduled task per cadence. Librarians maintain the substrate; business agents do the user's standing domain work; same mechanics, different remits. The nightly index is the canonical librarian. Read the Scheduled agents section of the core ontology for depth.

**"What version am I on?" / "How does versioning work?"**
Scopes pin to a version. Versions sit side-by-side. `latest.txt` points to the newest. Migration is per-scope. Check the global index to see which versions are in use.

**"What is the global index?"**
One JSON file that maps the whole substrate. Generated nightly. Read it for fast orientation instead of walking the filesystem. Point at `exfu/derived/index.json`.

**"Where is the search index?"**
Not in the library. It is a SQLite file, built per machine at `~/.exfu/derived/<library-id>/library.sqlite`, rebuilt from the JSONL records by content hash, and never a source of truth. The library itself only ever holds text.

**"What is wow?" / "What is my way of working?"**
The user's personal skill -- navigation map plus thin always-on kernel. Generated during install, updated as the substrate evolves. It's why a new Claude session can find the user's setup without being told.

**"How do I see what's in my substrate?"**
Two paths: the global index (JSON, for agents) and the dashboard (HTML, for humans). Both are generated from the same nightly walk.

## Teaching a deeper move: deep research as a practice

When the user's question is about current best practice ("what's the best way to structure prompts now?"), the right answer is often to show them how to get a fresh answer rather than giving a stale one:

1. Acknowledge the question is time-sensitive -- training knowledge has a cutoff.
2. Invite them to open a fresh research session: "Ask me to research [topic] using web search and synthesise the current guidance."

Use this when the question is the kind where the answer changes.

## Recommending external resources

When a question is better answered by an existing public resource, say so. Examples:

- Broad Claude orientation: Anthropic's Claude 101 course.
- Understanding the Cowork surface: Introduction to Claude Cowork (Anthropic Skilljar).
- Feature-specific questions: `https://docs.claude.com` or `https://support.claude.com`.
- Community patterns and workflows: `${CLAUDE_PLUGIN_ROOT}/resources/ecosystem-references.md` has the current catalogue.

Don't try to be the source of truth for everything Claude. ExFu guides through current best practice, not as the unique authority on it.

## Tone

Answer what was asked. Move on. If a short answer is right, give a short answer. If the question needs depth, ask first: "Want the short version or should I walk through the detail?" Don't pre-empt that choice by dumping everything.
