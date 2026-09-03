# Substrate Guide

version: 14

This is the reference for how this user's Claude substrate works. Read this whenever you need to understand the structure, conventions, or philosophy behind the way things are organised.

A note on registers: to the user, this whole installation is their **Agent Library**, kept in order by their **Agent Librarians**. "Substrate" is the internal register: the implementation vocabulary this guide is written in. Speak library language with users; use substrate terms only when they ask how it works underneath. (The vocabulary is defined in `exfu/<version>/ontology.md#vocabulary`.)

---

## What is a substrate?

A Claude substrate is the combination of files, skills, connectors, and scheduled tasks that together create a persistent way of working with Claude across sessions and devices. It is what the user experiences as their Agent Library.

No single component is the substrate. It's the interplay between them:
- **Skills** tell Claude how to behave and what conventions to follow
- **Files** in the knowledge base store context, instructions, plans, and data
- **Connectors** make files accessible from any Claude surface
- **Scheduled tasks** handle maintenance, monitoring, and proactive work
- **The local filesystem** gives Claude Desktop faster access and capabilities connectors lack

Everything cross-references everything else. Skills reference files. Files reference other files and skills. Scheduled tasks maintain the filesystem. That interdependence is the substrate.

Without it, every Claude conversation starts from zero. With it, Claude has memory, context, instructions, and continuity.

---

## Why a substrate, rather than Claude's built-in features

A fair question comes up often enough to answer here: Claude has Projects, Claude has memory, Claude has Dispatch. Why all this extra scaffolding?

The honest answer is that Anthropic is moving in this direction, and over time some of what the substrate does will become native. Treat the substrate as filling real *current* gaps, not as a permanent need for everything it does today.

The main current gaps:

**Desktop-mobile parity.** Claude on desktop and the Claude mobile app don't interoperate cleanly. For anyone whose day spans both surfaces, this is a deal-breaker on its own. The substrate's file-based approach bridges it: the same files are visible from either surface.

**Memory the user can see and edit.** Claude Projects has a memory concept, but the memories it creates are hidden, not user-editable, and don't transfer between devices. With the substrate, the "memory" is a folder of plain-text files. The user can read it, correct it, extend it, and move it. If Claude gets something wrong, you can open the file in any text or markdown editor and fix it directly.

**Portability across AI providers.** The substrate's core -- the files -- is platform-agnostic. If the user ever wants to try another assistant, or run multiple assistants against the same knowledge base, only the skills need porting. The substance is preserved.

**Team-shared substrates.** Multiple humans can work against the same substrate with appropriate access scoping. Claude Projects is a single-user container tied to one surface.

**Inspectability.** When Claude behaves oddly, the user (or Claude) can open the files and see exactly what context is being read. Nothing is opaque.

**Durability.** Markdown files survive tool changes, vendor changes, and company changes.

### How to handle this in conversation

Don't volunteer this section unprompted. If the user asks "why not just use Claude Projects / memory?" or shows scepticism about the setup, acknowledge that there are real current reasons and offer to go into whichever one matters to them.

---

## Folders, Claude Projects, and scopes -- three things people confuse

**A folder** is the classical thing -- a directory on a filesystem or cloud drive that holds files.

**A Claude Project** is an Anthropic product feature in the Claude desktop/web app. It's a container to group related conversations and give them shared instructions and uploaded files. Useful, but limited to that surface.

**A scope** is a substrate concept. It's a bounded working context -- any area of active work or attention that has its own directory with a `scope.md` file. A scope is more flexible than a Claude Project and lives at the substrate level -- available wherever the substrate is available.

The short version: a Claude Project is Anthropic's UI-level grouping. A scope is *your* substrate-level grouping. A folder is just a folder.

---

## The two-layer model

The substrate is conceptually two layers. Understanding this boundary is important for deciding what gets stored versus what Claude reads.

### Layer 1 -- Substrate proper (file-based, versioned)

Holds: skills, templates, context docs (brand voice, policies, conventions), structured data, configuration, working notes, contacts, CRM records. Versioned, auditable, shareable, evolves at its own pace.

This is what the substrate guide describes. Everything in the directory structure below lives here.

### Layer 2 -- Secrets and sensitive credentials

Holds: API keys, tokens, passwords, credential files (.env, *.key, *.pem, credentials.json, id_rsa, id_ed25519). These never enter the substrate. They belong in a password manager or a dedicated secrets store.

**The boundary is simple: only true secrets are banned.** Names, contacts, org charts, CRM records, personal notes, meeting minutes, preference profiles -- all of it lives wherever it naturally belongs in the scope structure. There is no separate PII layer and no special PII machinery.

For team substrates where regulatory requirements demand stricter data separation, the scope's storage backend and access controls can handle it -- the substrate doesn't prevent it, it just doesn't mandate it.

---

## Data tiers

The substrate organises data into three tiers.

### Tier 1: Project files

The actual work product -- source code, presentations, documents, assets. These live wherever makes sense for the project. Claude Desktop accesses them via the filesystem. They must be locally mounted.

### Tier 2: Third-party tools

SaaS platforms the user works in -- task managers, CRMs, email, wikis. Connected via MCP connectors. No local mounting.

### Tier 3: The substrate core (this knowledge base)

The persistent brain. This knowledge base is tier 3. It holds instructions, memory, context, scope planning, databases, and ways of working. It is accessible from every Claude surface via connector and/or local filesystem access.

---

## Directory structure

The substrate root is a single folder. Inside it, the plugin-owned convention base, the library's permanent record, the two scope locations, a guard file, and the generated dashboard front door:

```
[root]/
  CLAUDE.md               # guard file -- read this first
  exfu/                   # convention base and generated artefacts (not a scope)
  durable/                # the permanent record: what's been done to this library
  user/                   # special scope: personal context and global defaults
  scopes/                 # the tree of everything else
  dashboard.html          # generated front door: redirects into exfu/visualisations/
```

This layout is the same for solo users and team setups. There are no separate `orgs/` or `teams/` directories. Organisational structure is expressed through scopes -- an org is a scope, a team is a scope, a project is a scope.

### The exfu/ directory

Not a scope itself (no `scope.md`). This is the convention base and generated-output home, owned by the ExFu plugin. Contains:

```
exfu/
  latest.txt              # single line: the current convention version (e.g. "20260903-1743")
  20260903-1743/          # a convention version -- the frozen contract
    ontology.md           # the complete core ontology, ONE file (scope model,
                          #   folder-types, scheduled agents, authoring rules)
  readme.md               # orientation map for this directory
  principles.md           # ExFu principles and recommendations
  librarians/             # shipped librarian definitions, ready to register
  skills/                 # shipped skill sources (the wow template)
  derived/                # generated TEXT caches (never hand-edited)
    index.json            # the global index -- whole-substrate map
    agent-registry.json   # registered scheduled agents and their health
    agent-log.json        # scheduled-agent run history
    channels.json         # which connectors this surface can send through
    due.json              # the docket's due view, for surfaces without the index
  visualisations/         # ExFu-shipped visual outputs
    dashboard/            # the substrate dashboard (HTML)
      index.html
```

The convention base is one complete ontology file rather than a folder of fragments because agents ingest a single read far more reliably -- the same file-economy principle that governs everything written into the substrate.

**`exfu/derived/` holds text, and only text.** It syncs with the library and a phone reads it through the storage connector, so everything in it is a small text file that is safe to delete and regenerate. Anything binary lives per machine, **outside the synced root**: the search index `library.sqlite` sits at `~/.exfu/derived/<library-id>/` (`library-id` is a short hash of the library's resolved root path; `EXFU_DERIVED_DIR` overrides the location). Dropbox and git sync a database's `-wal` and `-shm` sidecars independently and produce a conflicted binary copy with no merge, which is why nothing binary is ever written inside the library. The index is rebuilt from the text records incrementally by content hash and is never a source of truth; a moved library simply rebuilds it.

**What is frozen, and what is not.** A version directory holds `ontology.md` and nothing else. The rule that decides membership: *a file belongs in a version directory if and only if a `Follows:` line can anchor into it.* Nothing anchors into the readme, the principles, the shipped librarian definitions, or the skill templates, so those sit unversioned at `exfu/` and are refreshed by plugin updates. This keeps the contract genuinely immutable while the material around it evolves at whatever pace features need -- and it keeps registry `source` paths stable, since librarian definitions no longer move when a convention version is minted. Bases shipped before `20260903-1743` carry all four inside the version directory; that is the older shape, and migration lifts them out.

**Versioning is side-by-side.** Convention versions are identified by their release moment: a shortened UTC timestamp to the minute, `YYYYMMDD-HHMM` (e.g. `20260903-1743`) -- no seconds, no timezone suffix, no ISO punctuation. Every release mints a fresh identifier (contents never change under a stable name), lexicographic order is chronological order, and identifiers share no naming surface with plugin release numbers. When a new convention version ships, it appears alongside the existing ones (e.g. `exfu/20260903-1743/` next to `exfu/20260723-1446/`, or a legacy `exfu/v0.3/` -- any timestamp identifier is newer than any legacy `v0.x` one). Existing scopes keep their version pin until explicitly migrated. The `latest.txt` file points to the current default for new scopes.

### The durable/ directory -- the permanent record

Not a scope (no `scope.md`) and not a folder-type. It exists exactly once, at the root, and holds the small set of append-only facts **about the library itself** that nothing can regenerate.

It sits at the root because every other home is categorically wrong. Everything in `exfu/` is plugin-owned and replaced wholesale when the plugin updates, so anything kept there can be destroyed by a routine refresh. `exfu/derived/` is explicitly a disposable cache, safe to delete and rebuild. `user/` and `scopes/` hold the user's own material, not the library's record of itself. The naming states the rule: `derived` is rebuilt, `durable` is kept.

Three tests, all of which must hold before anything is written here:

- **Unregenerable.** No librarian or script can reproduce it from material that still exists. The check is concrete: delete it, run every librarian twice, and see whether it comes back. Being expensive to recompute is not the same thing -- that belongs in `exfu/derived/`.
- **About the library, not about the world.** It only means anything as a fact about this library's installation, migration, decisions, or operation. Records whose subject is a person, company, deal, or a day in the user's life are domain data and belong in a scope's `databases/`.
- **Append-only, human-readable text.** Markdown or JSONL, every entry dated and carrying a stable id, never rewritten in place; a wrong entry is corrected by a later entry saying so. This third test is what keeps the other two honest -- it excludes databases, embeddings, mutable counters, and config files by construction rather than by judgement.

**State the carve-out positively.** Every skill that refreshes, copies, or migrates a library says it in this form, and never as a list of exceptions:

> **A refresh replaces `exfu/`. It never touches `durable/`, `user/`, or `scopes/`.**

An exception list grows silently wrong: each new durable thing is a fresh chance to forget an entry, and a forgotten entry destroys the one category of file that cannot be recovered. Naming what a refresh *may* replace has no such failure mode.

`ledger/` is the first tenant -- materialise-on-demand applies here as everywhere, so `durable/` ships holding `ledger/` and a `readme.md` carrying the membership test, and gains nothing else until another genuine tenant exists. The ledger holds `migrations.md` (every migration considered and how it went, including per-scope journals for migrations that work scope by scope), `install.md` (when the library was created, by which plugin version and surface), and `grants.md` (consent the user gave, and revoked, for a channel to send on their behalf without asking -- the dispatcher checks it before every automatic send, so the flag on the channel itself grants nothing). In the user-facing register `durable/` is the library's **permanent record** and the ledger is its **logbook**; librarians say "permanent record" to users and never say "durable".

### Migrations -- how a library moves between shapes

Releases change structure. Migrations carry existing libraries across, and the ledger records the result.

**They are detected at boot, not scheduled.** A plugin update does not touch the library, it changes what is installed alongside it -- there is no update hook, so nothing can run at update time. The boot skill compares the migrations the plugin ships (`exfu/migrations/`) against `durable/ledger/migrations.md`, and hands anything pending to the `library-updater` librarian. Applying is done with the user present, never unattended.

Three rules make this safe:

- **A fresh install seeds rather than replays.** A new library is already in the target shape, so install records every shipped migration as `not-applicable`. Without this, computing pending as *shipped minus applied* would make every new library attempt the entire history of migrations against a shape it never had.
- **Preconditions are tested against the library, not the ledger.** Each migration declares `applies_when:`, evaluated against actual structure. The ledger says what is believed; the filesystem says what is true. When they disagree, the agent reports and stops rather than interpreting its way past it.
- **Version skew between surfaces is detected.** Claude Code and Cowork have separate plugin installs and either may auto-update, so the same library can be opened by a surface older than the library itself. If the ledger records migrations the installed plugin does not ship, the library is ahead: that surface must not attempt structural work, and says so.

Migration ids are `YYYYMMDD-HHMM-slug`, so lexicographic order is application order -- the same property version identifiers rely on. The plugin ships migrations back to a documented floor; older libraries are told to reinstall rather than migrated through the full history.

### The user/ scope

A real scope (has `scope.md`) for personal context, definitions, and defaults that apply across everything the user does.

```
user/
  scope.md                # no exfu version pin -- always current
  context/                # personal background, preferences, about-me
  ontology/               # personal definitions, ways of working
  skills/                 # sources of the user's generated personal skills (wow, docket)
  docket/                 # what is open: tasks, reminders, things left for agents
  ...                     # other folder-types materialise as content appears
                          #   (databases, scheduled, ...)
```

The user scope's `scope.md` has `parent: none` and no `exfu:` version field. It doesn't pin a version -- it's always current. Migration is by user decision.

### The scopes/ tree

An arbitrary-depth tree of working contexts. A directory inside it is one of two kinds:

- **Scope** -- has `scope.md`. A real working context with the standard internal shape.
- **Grouping folder** -- no `scope.md`. Purely organisational (e.g. `scopes/clients/`). Agents ignore it structurally.

```
scopes/
  acme/                   # a scope
    scope.md
    ontology/
    context/
    docket/
    databases/
    scopes/               # acme's child scopes, gathered here
      sales/              # a sub-scope
        scope.md
        ontology/
        docket/
      eng/                # another sub-scope
        scope.md
  clients/                # a grouping folder (no scope.md)
    ...
  side-project/           # another scope
    scope.md
    context/
    docket/
```

**Scopes nest via their own `scopes/` directory.** A scope never holds child scopes loose among its own working folders. It gathers them in a dedicated `scopes/` subdirectory, keeping the scope's own folder-types clean and predictable. The pattern is self-similar: the root has `scopes/`, a scope can have `scopes/`, and so on.

---

## The CLAUDE.md guard file

The substrate root contains a file named `CLAUDE.md`. Its purpose is to prevent Claude from treating the substrate as a generic working folder when the exfu-library skill is not loaded.

Canonical content:

```
# Don't use this folder

This is the root of an ExFu Agent Library (internally: a substrate).

Do not read, write, or otherwise interact with the contents of this folder
unless your session has loaded the exfu-library skill (or a derivative
that knows the library's conventions).

If you've accidentally been pointed here, stop and ask the user to either:
- Load the exfu-library skill, or
- Work in a different location.

This protects the library from being treated as a generic working folder.
```

Do not modify or remove this file. It is a safety guard, not content.

---

## scope.md -- the scope boundary marker

A directory is a scope if and only if it contains a `scope.md` file. This file declares the scope's identity and its place in the structure.

Format:

```markdown
---
name: Acme
purpose: Client relationship and commercial engagement with Acme Corp
parent: root
exfu: 20260903-1743
---

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Optional 2-3 sentence elaboration of purpose. Not required.
```

**Fields:**
- `name` -- the scope's human-readable name. Does not need to match the directory name (but usually will).
- `purpose` -- one sentence. What this scope is for. Enough for an agent to decide whether to read deeper.
- `parent` -- the name of the parent scope, or "root" for top-level scopes under `scopes/`. This is what makes extraction/sharing safe -- an agent knows something is above it.
- `exfu` -- the ExFu convention version this scope references. New scopes default to whatever `latest.txt` points to. Existing scopes keep their pin until explicitly migrated.

**What scope.md does NOT contain:**
- Entities, conventions, current state, dependencies (these live in folder-types)
- Status, dates, progress tracking (those belong in `docket/` or the global index)
- Arrays of related skills or dependencies (scope.md is a boundary marker, not a knowledge store)

**The protective header** (the blockquote) appears in both `scope.md` and every `agent.md`. Its job is to catch agents that wander into the substrate without having loaded ExFu skills. The exact wording is consistent across every file.

---

## Folder-types -- the standard vocabulary

Inside any scope, the folder-types are the standard vocabulary of "where things go." Each is a discovery convention first, a storage location second. Its job is to tell an agent *how the user handles this kind of thing for this scope* -- whether the data lives here, or somewhere else entirely.

The base catalogue (defined canonically in `exfu/<version>/ontology.md`, one anchored section per type):

| Folder | What it answers | Analogy |
|---|---|---|
| `ontology/` | What do the concepts and terms in this scope mean? | A glossary |
| `context/` | What background should an agent know about this scope? Including kept reference documents -- PDFs, spreadsheets, transcripts | A wiki plus a filing drawer |
| `skills/` | What skill definitions belong to this scope? | Functions |
| `librarians/` | What substrate maintenance runs here on a schedule? | Cron jobs for housekeeping |
| `scheduled/` | What business-logic work runs here on a schedule? | A standing brief to an assistant |
| `docket/` | What is open here -- tasks, reminders, things left for agents -- and when and how does it get heard? | A court's list of matters to be heard |
| `databases/` | Where do structured, repeating records live? Including recurring personal records like daily logs | Structured records |
| `visualisations/` | Where do agent-created visual outputs live for this scope? | A gallery |

**Three folder-types are deprecated.** `todo/`, `reminders/` and `inbox/` were separate folder-types before `docket/` replaced all three. A scope that has them keeps working: every shipped reader (the boot skill, the index, the dashboard, the daily briefing) still understands their markdown forms, and the docket migration offers to convert them scope by scope, with the originals kept in `docket/legacy/`. No new scope creates them, and their anchors stay in the ontology so old `Follows:` lines resolve.

**The catalogue is open.** Any scope may add a folder-type not listed here. If it does, it should define the new type in that scope's `ontology/` so an agent can make sense of it.

### Store-or-point

Store-or-point is a first-class choice for every folder-type, and in the docket it is a choice per file. A `docket/` may hold `todo.jsonl`, or its `agent.md` may say `todo: tracked in ClickUp, not stored locally` while `reminders.jsonl` and `agent-backlog.jsonl` stay local. A `databases/` folder may hold records, or say "contacts live in HubSpot."

The convention guarantees the *location is discoverable*; whether data lives there is per-scope, per-user. The global index tracks the status of each folder-type as `data` (contains files), `pointer` (points elsewhere), or `empty`, and for the docket it tracks that status per file.

### Folder-types materialise on demand

Not every scope uses every folder-type, and a folder-type is only created when there is content to put in it (or the user explicitly asks, e.g. a docket whose tasks point at an external tool). Most scopes start with just `context/`. Additional folder-types are created the moment their first content appears -- never scaffolded empty "for completeness". An empty folder with boilerplate descriptors is noise every future read pays for; a scope with only scope.md and context/ is healthy, not incomplete.

### The docket -- what is open, and when it gets heard

`docket/` is the folder-type agents touch most often, so its shape is the most specified. It holds three kinds of entry, one JSONL file each: `todo.jsonl` (tasks, with a completion state), `reminders.jsonl` (nudges, with a surface time or condition), and `agent-backlog.jsonl` (things the user leaves **for agents** to attend to -- a queue of work for agents to pull from, never the user's own in-tray; the backlog-sweep librarian summarises and suggests homes, the user decides). One file per collection rather than one file per entry, because the reading cost that matters is the number of files: a whole collection is one read from any surface, including one connector call on a phone. A file appears on its first entry; the folder on its first file.

Every entry is one JSON object on one line with the same deliberately thin shape: `title`, `notes` for people, `agent_notes` as freeform instructions for agents (timing, conditions, dependencies, "only show when"), `status` (`open | done | archived`), optional `keywords` written by the saving agent as the search layer that needs no model, and the common envelope -- a library-wide `id` (UTC timestamp to the second plus random base32), `created`, `updated`, and a `revision` the writer increments. There are no priority, tag, dependency or recurrence columns; those live in `agent_notes` as prose. A facet a program must read is a **mixin**: a separate JSONL file whose rows reference the record they decorate by id, so the schema never grows. Sync conflicts fold by id (highest revision wins); the docket-compact librarian moves `done` and `archived` entries into `archive.jsonl` after 30 days so the active files stay small.

The mechanics that make entries *do* something sit beside them in the same folder, joined by id:

- **Triggers** (`triggers.jsonl`) are the scope's statement that at some moment, or on some occurrence, something should be assessed by an agent, and how. Each carries an `assess` brief in prose, a schedule (`once`, `cron` with a timezone, or `on-signal`), a handler (`deliver` through a channel; `agent`, a sub-agent at a stated weight; or `definition`, a registered scheduled agent), a channel, and an owner. A reminder is an entry with a trigger; an email check or "see whether the build passed" is a trigger with no entry at all. Natural-language rules are resolved once, when saved, and the original wording is kept in `assess`.
- **Signals** (`signals.jsonl`) are facts an agent recorded about the world, addressed to whoever is listening. A fired trigger's handler reports the signals it observed; any trigger may be armed on a signal name. Two triggers that share a name form a workflow without either knowing about the other; the dashboard renders the implied graph from the index.
- **Fire receipts** (`fires.jsonl`) record every firing: an `intent` row before acting and a `result` row after, so a crash leaves a visible half-receipt, nothing fires twice, and in a shared scope the intent receipt is the claim that decides which actor proceeds. At most once per trigger per run, never backfilled.
- **Channels** (`channels.jsonl`) are how the scope reaches people: `dm` to one actor, `broadcast` to several, or `pull` (the dashboard and session start, always present). Any scope may declare channels; `user/` is where most people declare their default. Each is `send: draft` unless the user elevates it to `auto`, and the elevation is a grant in the permanent record, not the flag.

The **dispatcher** librarian, on the hourly cadence, is what makes triggers fire. It never boots the library: it refreshes the index, reads the due view, and for each due trigger it owns writes the intent receipt, does what the handler says, and writes the result. It runs as a Claude Code Desktop local scheduled task with the cheapest model, because it needs the local index and on most runs finds nothing due; Cowork's cloud tasks have no local files and cannot host it. The boot skill runs the same due check at session start, so a Cowork-only user still gets their reminders, less promptly, and the dashboard shows what is waiting.

The user's generated personal skill for all of this is `<user>-docket` (from `setup-docket`), which captures, reminds, completes and snoozes on both the filesystem and connector backends. It replaces the separate reminders and inbox skills of earlier releases. With users the vocabulary is plain: "your docket", "a reminder rule", "something happened", "tell me" or "tell the team", "prepare only" or "send automatically". The full contract is `exfu/<version>/ontology.md#docket` and `#docket-mechanics`.

---

## The agent.md / readme.md convention -- reference+delta

Every materialised folder-type directory inside a scope contains an `agent.md`, optionally accompanied by a one-line `readme.md`:

### agent.md (for agents)

Follows the reference+delta pattern: reference the upstream convention, then list only local deviations. Structure:

1. **Protective header** (blockquote, always first)
2. **`Follows:` line** naming the upstream convention by versioned anchor into the core ontology file
3. **`Local deviations:` section** listing only what differs from upstream. If nothing differs, omit this section entirely.

A folder with no deviations:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/20260903-1743/ontology.md#context
```

That's it. One line plus the header. The agent reads the referenced section of `ontology.md` for full behaviour.

A folder with deviations:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/20260903-1743/ontology.md#docket

Local deviations:
- todo: tracked in ClickUp, not stored locally
- Use the ClickUp MCP connector for read/write
- Tag all tasks with scope name "acme-sales"
```

The canonical behaviour of each folder-type lives once, in `exfu/<version>/ontology.md`. This keeps the substrate lean and prevents convention drift across scopes.

### readme.md (for humans)

The same information, for human eyes, in a sentence:

```markdown
Context for the Acme account. See ExFu conventions for details.
```

### Descriptors carry no state

agent.md, readme.md, and scope.md describe what a folder or scope is *for* -- static facts that stay true. Never write current state into them: no "currently empty", no item counts, no "last updated", no status notes. State is only true at write time and goes stale silently, misleading every later reader. Current state belongs in the derived index, the dashboard, and the content itself.

### When to read agent.md files

- At the start of a session, read the `agent.md` of whatever folder the user is working in
- Before creating content, read the target folder's `agent.md` to understand conventions
- When an `agent.md` has a `Follows:` line, read the upstream convention file too
- When the user references something that might exist elsewhere, check `agent.md` files for cross-references

### Maintaining agent.md and readme.md

When you create a new folder-type directory in a scope (which happens only when its first content appears), create the `agent.md` immediately: at minimum the protective header and a `Follows:` line. When you add a local deviation, add it to the `Local deviations:` section. The `readme.md` is an optional one-liner for human eyes.

---

## Ontology and concept resolution

### What an ontology folder is

A collection of definitions -- "here is what this concept means in this scope." Ontologies are **flat lists of complete files**: one file per concept (or one file for the whole ontology while it's small), each file the complete definition of its concept. Never shard a concept across fragments or nest subfolders of pieces -- completeness-per-file is what makes ingestion reliable.

Ontology holds *concepts*, not instances. A definition of what something means belongs here; a thing of a known kind goes where that kind prescribes (a librarian definition in `librarians/`, records in `databases/`, documents in `context/`).

- `exfu/<version>/ontology.md` defines the structural vocabulary the entire substrate runs on, in one file: what a scope is, what a scheduled agent is, the difference between a task and a reminder, what each folder-type means.
- `user/ontology/` adds the user's personal definitions and ways of working that apply across all their scopes.
- Any scope's `ontology/` adds definitions local to that scope ("we call them specialists, not reps"; "a lead in this context means...").

### How resolution works

When an agent operates inside a scope, it reads all the relevant ontologies by walking the declared parent chain: active scope -> each ancestor scope -> `user/` -> `exfu/` base. It holds them all together. If two levels define a term differently, the agent does not mechanically pick a winner -- it recognises both meanings and, where it matters, asks the user in the moment which applies.

The explicit parent declarations in `scope.md` and the explicit `Follows:` references in `agent.md` are what make this work. They tell the agent *which ontologies are relevant* without filesystem guesswork. The structure makes the reference set discoverable; the agent supplies the judgement.

---

## Scopes: what they are and how they work

A scope is a bounded working context. It's the single structural concept in the substrate -- everything is a scope. A project is a scope. A team is a scope. An org is a scope. A client engagement is a scope. Your personal workspace is a scope.

### What makes something a scope

Scopes are for areas where *work is being done* -- decisions being made, notes being kept, drafts in progress, ongoing thinking that benefits from continuity. Not every topic needs a scope. Identity-level information lives in `user/context/` instead.

Common things that become scopes:
- Client engagements or deals
- Product initiatives or launches
- Teams the user belongs to or leads
- Research threads or domains of interest
- Recurring events (conferences, programmes)
- Major life projects (house build, career transition)
- Organisations (expressed through scopes rather than a separate structural concept)

### Scope nesting

Scopes can contain child scopes, gathered in a dedicated `scopes/` subdirectory. The pattern repeats at every level. An agent entering any scope at any depth sees a predictable shape.

```
acme/
  scope.md                # name: Acme, parent: root
  ontology/
  context/
  docket/
  scopes/
    sales/
      scope.md            # name: Sales, parent: Acme
      ontology/
      docket/
      scopes/
        q3-renewal/
          scope.md        # name: Q3 Renewal, parent: Sales
          context/
          docket/
```

Nesting depth is unlimited but practical use rarely exceeds three levels. Flat is always possible -- users who don't want nesting just don't nest.

### Scope discovery via the global index

Scopes are discovered through the global index at `exfu/derived/index.json`, not through individual skills or filesystem traversal. The index is a JSON document that maps every scope in the substrate: its name, path, parent, ExFu version, which folder-types are populated, and whether each is data-bearing, pointer-only, or empty.

An agent reads the index to orient, then navigates to the specific scope the user wants to work in. This is fast and reliable even when the substrate is large or hosted on a cloud drive with caching issues.

---

## Scope vs context -- the distinction

**Context is *about* things. Scopes are *where things happen*.**

Context answers "who/what is this?" Scopes answer "what am I doing here?"

Context is identity-level, standing information -- read-often-write-rarely. You read context to *orient*.

Scopes are active working material -- plans, decisions-in-progress, drafts, call notes. You read a scope to *pick up work*.

### Fuzzy-zone test

If you'd read it to *orient yourself*, it's context. If you'd read it to *pick up the work*, it's a scope.

### Example: same entity, two different reasons to write about it

An imaginary company, Acme:

- `scopes/acme/context/account-overview.md` -- who Acme is, the relationship, their business, standing facts. Rarely changes.
- `scopes/acme/docket/` -- the active tasks and reminders: follow-ups, proposal drafts, decisions.
- `scopes/acme/scopes/q3-renewal/` -- a child scope for a specific deal cycle, with its own context and tasks.

Context and active work coexist within the same scope. They serve different purposes.

---

## The global index

The global index at `exfu/derived/index.json` is a generated JSON document that gives a whole-substrate picture. It is maintained by the nightly index librarian and should never be hand-edited.

The index maps:
- Every scope in the substrate (name, path, parent, ExFu version)
- Which folder-types each scope has, and their status (`data`, `pointer`, or `empty`)
- The scope tree (parent-child relationships)
- Which ExFu convention versions are in use

The index serves two consumers:
1. **Agents.** Instead of traversing the filesystem, an agent reads the index and knows immediately what scopes exist, where they are, and what's in them. Fast orientation, even when the substrate is large.
2. **The substrate dashboard.** The HTML visualisation at `exfu/visualisations/dashboard/index.html` renders the index into a visual map for non-technical users.

The global index is a text cache in `exfu/derived/`, beside the agent registry and log, `channels.json` (which connectors this surface can send through) and `due.json` (the docket's due view, carrying the index generation and source hashes it was computed from, so a stale one is rejected). The **search index** is a different thing: a per-machine SQLite file at `~/.exfu/derived/<library-id>/library.sqlite`, outside the synced root, holding every docket record with full-text search over titles, notes and keywords, plus the trigger, signal, receipt and channel tables the dispatcher and dashboard query. It is rebuilt incrementally by content hash (the nightly run validates everything, the hourly run trusts size and mtime hints), is never a source of truth, and is never read from a phone: mobile sessions read the JSONL files directly.

---

## Scheduled agents: librarians and business agents

A scheduled agent is recurring work defined as *agent instructions*: a markdown definition an agent reads cold and carries out on a cadence (nightly for most; hourly for the dispatcher), calling scripts as tools where the definition says to. The definition is the spec; the platform's scheduled task is the cron; Claude in that session is the worker.

Two kinds share identical mechanics and differ only in remit:

- **Librarians** keep the substrate itself tidy so the user doesn't have to. Their definitions live in `librarians/` folders (the convention base ships its own at `exfu/librarians/`).
- **Business agents** do the user's recurring domain work -- the standing jobs they'd brief an assistant on. Their definitions live in `scheduled/` folders.

### By example

Librarians:
- **Nightly index** (exfu-shipped) -- walks the entire substrate and regenerates `exfu/derived/index.json`. The foundation; others depend on it.
- **Docket compaction** (exfu-shipped, nightly) -- archives closed docket entries after 30 days, folds sync conflicts by id, sweeps expired signals, receipts and orphaned mixins, and emits `entry-completed` signals.
- **Backlog sweep** (exfu-shipped, nightly) -- summarises each scope's agent backlog (and any deprecated inbox) and suggests where items belong; never moves anything itself.
- **Dispatcher** (exfu-shipped, hourly) -- asks the index what is due and fires each trigger through the handler and channel it names, writing a receipt per fire. Runs as a Desktop local task with the cheapest model; never boots the library.
- **Dashboard generator** (exfu-shipped) -- renders the HTML dashboard from the derived data.
- **Version cleanup** (exfu-shipped) -- flags convention versions no scope references any more.
- **Library updater** (exfu-shipped, not scheduled) -- applies pending migrations with the user present when the boot skill finds the ledger behind the plugin.

Business agents:
- A listings scanner that checks dealer sites against a brief and updates a sightings database.
- A weekly digest drafter that summarises a scope's movement.
- A mailbox watcher that files invoices as they arrive.

What a definition does is scope-dependent -- it reads that scope's ontology, the user's preferences, and the ExFu defaults to determine its behaviour.

### Definitions, registration, execution

Definitions are markdown files with YAML frontmatter (`name`, `cadence`, `description`, plus optional `scripts`, `reads`, `writes`, `depends_on`) and natural-language instructions -- rich enough for a scheduled agent to read cold and know what to do, but not so procedural that they become brittle scripts. The canonical format lives in `exfu/<version>/ontology.md` (Scheduled agents section).

A definition does nothing until *registered* (the install-scheduled-agent skill handles this, always with user confirmation). The registry of all registered scheduled agents lives at `exfu/derived/agent-registry.json`; run history is logged at `exfu/derived/agent-log.json`. One scheduled task per cadence (e.g. `nightly-agents`) executes everything registered for that cadence: librarians first, so the substrate is tidy and the index fresh before business agents consume them, then dependency order. The nightly task is a Cowork scheduled task, as before. The hourly task (`hourly-agents`) is a Claude Code Desktop local task with the cheapest model selected, because the dispatcher it hosts needs the local index and usually has nothing to do; it runs only while the app is open and the machine is awake, with one catch-up run for a missed slot, which is the dispatcher's own misfire rule. A Cowork-only user skips it and relies on the session-start check.

---

## The exfu-library skill and user vocabulary

For git-backed team substrates, users interact with Claude using natural verbs. The exfu-library skill (the boot skill; in pre-0.4 releases it was named `substrate`) maps these to the underlying git operations. No git terminology surfaces to the user.

| User says | What happens |
|---|---|
| save | commit on personal branch |
| share for review | push branch and open a pull request via the git API |
| check for updates | pull from main |
| fix clashes | guided merge conflict resolution |
| approve change | merge the pull request (authorised users only) |

Terms not used with users: branch, draft space, sandbox, fetch, diff, show my changes.

### Permission-aware behaviour

The exfu-library skill is a single skill, not separate admin and non-admin variants. When it loads, it checks what permissions the current user has on the substrate repository. Users with admin or maintainer rights see the review and approval vocabulary. Users without those rights see only the personal vocabulary (save, share for review, check for updates).

The git repository's own permission model is the gatekeeper. No separate Claude-side permission scaffolding is needed.

The specific permission lookup -- which git provider, which API, which identity integration -- is resolved by the wrapping plugin or the installing Claude. See `cross-cut-extension-and-wrapping.md`.

### Lightweight sync

For team substrates, sync defaults to a script that checks the remote HEAD commit hash against local. Claude wakes only when there is an actual delta. Tokens are consumed only when needed.

---

## Access modes

### Filesystem (preferred on desktop)

When the knowledge base is mounted in a session, use filesystem tools directly. This is faster and supports all operations including delete, move, and rename.

### Connector (universal)

When filesystem access isn't available (mobile, unmounted sessions), use the storage connector. The Dropbox connector supports delete, move, and copy natively, addresses files by path, and keeps revision history for recovery (see the exfu-dropbox-storage skill if installed). Git-backed substrates use their own sync flow (see git-substrate-sync).

---

## Naming conventions

- Lowercase, hyphen-separated: `meeting-notes-2026-04-15.md`
- Date-prefix for time-sensitive files: `YYYY-MM-DD-filename`
- No spaces in filenames

---

## Substrate hygiene: what not to put here

The substrate may be shared and may be version-controlled. A few things don't belong:

- **Credentials, API keys, passwords, access tokens.** Use a password manager or a dedicated secrets store.
- **Government identifiers and financial account details.** SSNs, passport numbers, full credit card numbers, bank account numbers.
- **Raw health and medical records.** Diagnoses, test results, therapy notes. Summaries and context are fine -- the raw files belong in a purpose-built system.
- **Other people's private information without consent.**

Names, contacts, org charts, CRM records, personal notes, meeting minutes, preference profiles, decision history -- all fine. The line is: would it matter if this appeared in a breach? Secrets and regulated data stay out. Working data stays in.

---

## Universal naming in this guide

This guide does not name specific git providers, specific cloud drives, or specific tools. The substrate conventions are universal; clients and installs vary. The wrapping plugin or the installing Claude resolves provider-specific decisions. See `cross-cut-extension-and-wrapping.md`.

---

## Extending the substrate

The substrate is designed to grow.

**Custom databases** -- Ask Claude to manage structured data (contacts, CRM, task lists, anything). It creates and maintains the data in a scope's `databases/` folder-type. The user interacts through conversation.

**Custom folder-types** -- A scope can define folder-types beyond the standard eight. Define the new type in that scope's `ontology/` so agents can make sense of it.

**Custom skills** -- Draft skills in the user's `skills/` folder-type or a scope's `skills/`, test them, then install as proper skills. Skills can encode any repeated workflow, convention, or way of working.

**Custom scheduled agents** -- Define librarians (recurring tidying, checking, routing of the substrate itself) in a scope's `librarians/` folder, and business agents (recurring domain work: scanning, digesting, watching) in a scope's `scheduled/` folder. Register them with the install-scheduled-agent skill to make them live.

**Substrate visualisation** -- The dashboard at `exfu/visualisations/dashboard/index.html` renders the global index into a visual map of the entire substrate. The user opens it in a browser and sees the full scope tree, folder-type status, and ontology chain. It's regenerated nightly, and `dashboard.html` at the library root redirects to it so nobody has to remember the path.

**Inter-agent communication** -- Agents for different team members can exchange information via the available connectors. The pattern is defined by the team's way of working.

---

## Evolving this document

This guide is a starting point. The user and their team should modify it as their way of working develops. When making changes:

1. Update the version number at the top
2. Append a changelog entry at the bottom with date, new version, and a one-line summary of what changed and why
3. If the change affects other folders or skills, update their agent.md and readme.md files too

### Changelog rule (applies to any versioned file in the substrate)

Any file that carries a `version:` line also carries a `## Changelog` section at the bottom. When you bump the version, append an entry to the changelog on the same edit:

```
- YYYY-MM-DD v[N]: one-line summary of what changed and why.
```

Newest entries at the top of the Changelog section. Append-only. Don't rewrite history.

---

## Changelog

- 2026-09-03 v14: The docket replaces three folder-types, and the library gains triggers (plugin 0.11.0, conventions `20260903-1743`). `todo/`, `reminders/` and `inbox/` collapse into one `docket/` per scope: `todo.jsonl`, `reminders.jsonl` and `agent-backlog.jsonl` (the inbox renamed to say whose queue it is), one JSONL file per collection so a whole collection is one read from any surface including a phone. The three old folder-types are deprecated, never wiped: every reader keeps its legacy parser, no new scope creates them, and the migration is offered per scope with a journal in the ledger, originals preserved in `docket/legacy/`, and a scope the user or agent declines staying on the old shape indefinitely. One thin record shape for all three files -- `title`, `notes`, `agent_notes`, `status`, optional agent-written `keywords`, and the envelope of library-wide `id`, `created`, `updated`, `revision` -- with no ontological fields: priority, tags, dependencies and recurrence live in `agent_notes` as prose, and any facet a program must read is a mixin file joined on id, so the schema never grows. Mixins bring the docket's mechanics as sibling files: triggers (when and how a matter gets heard: `once`, `cron` with a zone, or `on-signal`; a prose `assess` brief; a handler of `deliver`, `agent` at a weight, or `definition`), signals (facts recorded for whoever listens, the arc between actions, forming workflows no file authors), fire receipts (intent before acting, result after; the misfire rule, the watermark, and the claim in a shared scope), actors (owner handles; a dispatcher fires only what it owns or what is `any`), channels (`dm`, `broadcast`, always-present `pull`; `draft` by default) and grants (`auto` sending is a ledger entry in `durable/ledger/grants.md`, never the flag; in 0.11.0 honoured only on a `dm` to the trigger's owner). The dispatcher is a new librarian on the existing hourly cadence, created as a Claude Code Desktop local task with the cheapest model because it needs the local index and usually has nothing to do; Cowork's cloud tasks cannot host it, so a Cowork-only user gets the boot-time drain -- the boot skill runs the same due check at session start -- and the dashboard. `inbox-triage` becomes `backlog-sweep`; `docket-compact` joins the nightly cadence. The derived rule is reworded and made true: `exfu/derived/` holds text caches only (index, registry, log, `channels.json`, `due.json`), and the search index `library.sqlite` moves per machine outside the synced root to `~/.exfu/derived/<library-id>/`, rebuilt from the JSONL records incrementally by content hash, FTS5 over titles, notes and keywords, no embeddings and no install beyond the stdlib. `setup-docket` replaces `setup-reminders` and `setup-inbox`, generating one `<user>-docket` skill. Decision record: `planning/structured-worklist.md`.
- 2026-07-24 v13: Library migrations become a convention, and durable state gets a home (plugin 0.10.0). New top-level `durable/` is the library's permanent record: the append-only facts about the library itself that nothing can regenerate and that no refresh may overwrite. Its first tenant is the logbook at `durable/ledger/` (`migrations.md`, `install.md`). The container is deliberately more general than that tenant, because more stateful things will need to survive outside `exfu/` over time. Membership test, all three required: unregenerable (delete it, run every librarian twice, see if it returns -- cost is not part of the test), about the library rather than the world (domain records belong in a scope's `databases/`), and append-only human-readable text (which excludes SQLite, embeddings and mutable config by construction, and matters because libraries sync through Dropbox or git). The carve-out is stated positively and never as an exception list: a refresh replaces `exfu/`, and never touches `durable/`, `user/`, or `scopes/` -- an exception list grows silently wrong, and a live data-loss bug of exactly that kind was found and fixed in `exfu-migrate-to-dropbox`. Migrations themselves are boot-detected rather than scheduled: a plugin update does not touch the library, so there is no update hook to fire; the boot skill compares shipped migrations against the ledger and hands pending work to the `library-updater` librarian, applied with the user present. Three safety rules: fresh installs seed rather than replay, preconditions test actual structure rather than the ledger, and a library ahead of its surface's plugin blocks structural work (Claude Code and Cowork have separate plugin installs and either may auto-update). Decision records: `planning/library-migrations.md`.
- 2026-07-24 v11: The conventions lock moves to the contract rather than the folder (plugin 0.9.0). A convention version directory now holds `ontology.md` and nothing else; `readme.md`, `principles.md`, `librarians/`, and `skills/` move out to unversioned `exfu/` and travel with plugin releases. The deciding rule is mechanical: a file belongs in a version directory if and only if a `Follows:` line can anchor into it, and all 16 anchors point into the ontology. Base minted as `20260724-1749`; the root-layout depiction moved from the ontology to `exfu/readme.md`. Registry `source` paths stop breaking on every mint. A build gate (`build/check-conventions-lock.sh`) now enforces byte-identity of shipped versions, and `build/mint-conventions.sh` makes minting one command. Bases before `20260724-1749` keep the old shape; both coexist. Decision record: `planning/conventions-lock-boundary.md`.
- 2026-07-24 v10: The dashboard gains a front door. `dashboard.html` at the library root redirects to `exfu/visualisations/dashboard/index.html`, so users open the dashboard from the top of their library instead of remembering a four-deep path. It is a generated redirect page, not a symlink: sync layers handle symlinks unreliably (the same reason `exfu/latest.txt` is a text file), and browsers resolve relative URLs against the document URL, so a symlinked page would break the dashboard's own `../../../scopes/...` gallery links and view iframes. The dashboard bundle itself does not move.
- 2026-07-23 v9: Conventions versioning moved to timestamp identifiers (plugin 0.6.0). Convention base versions are now named by their release moment as shortened UTC timestamps (YYYYMMDD-HHMM, e.g. 20260723-1446) instead of v0.x labels; identifiers no longer share a naming surface with plugin release numbers, lexicographic order is chronological, and every release mints a fresh identifier so a version's contents never change under a stable name. v0.x is now the legacy scheme: any timestamp identifier is newer than any v0.x one. First timestamped base minted as 20260723-1446 (contents of the former shipped v0.3). Side-by-side model and per-scope pins unchanged.
- 2026-07-20 v8: Agent Library re-pitch (plugin 0.4.0). Added the two-register note: user-facing Agent Library / Agent Librarians vs internal substrate vocabulary, defined in ontology.md#vocabulary. Guard file and boot-skill references renamed substrate -> exfu-library. Connector access section rewritten for Dropbox (native delete/move, path addressing, revision history), replacing the Box workarounds; retired the _DELETED_ naming convention. Corrected the dashboard path to exfu/visualisations/dashboard/ and fixed the stale version header (previous edit logged v7 in the changelog but left the header at 6).
- 2026-06-10 v7: Convention base flattened to file-economy form: the core ontology is now ONE file (exfu/v0.3/ontology.md, anchor-addressed by Follows: lines) instead of fragmented ontology/ subfolders; shipped librarian definitions moved to exfu/v0.3/librarians/ (instances, not ontology); wow template ships at exfu/v0.3/skills/wow-template.md. Added scheduled/ folder-type and the ScheduledAgents concept: librarians and business agents share mechanics (definition format, registry, cadence sessions) and differ in remit; registry renamed to exfu/derived/agent-registry.json with kind field, log to agent-log.json, task to nightly-agents. Added materialise-on-demand rule (no empty folder scaffolding), the no-state rule for descriptors (agent.md/readme.md/scope.md), and the file-economy authoring principle (fewer, complete files; flat ontologies).
- 2026-06-09 v6: Rewritten for v0.3.0. Replaced orgs/, teams/, and personal-default layout with uniform scope model -- everything is a scope. Replaced _meta/ with exfu/ (convention base at exfu/v0.3/, generated output at exfu/derived/). Removed _trash/ and scratch/. Introduced 10 standard folder-types with store-or-point principle. Added scope.md format (YAML frontmatter with name, parent, exfu version pin). Replaced README.md convention with agent.md reference+delta pattern (Follows: line + local deviations). Added protective headers for scope.md and agent.md. Added librarians (autonomous maintenance agents with cadence-based scheduling). Added global index (exfu/derived/index.json) for whole-substrate discovery. Added versioning model (side-by-side convention versions, per-scope pins). Added user/ as a special unversioned scope. Replaced PII two-layer model with secrets-only ban. Added ontology resolution (parent-chain walk). Added substrate dashboard (exfu/derived/dashboard/).
- 2026-05-02 v5: Revised for v0.2.0. Added two-layer model (substrate proper vs PII layer). Added CLAUDE.md guard file at substrate root. Introduced top-level orgs/ and teams/ folders for multi-org and multi-team support (personal-default layout unchanged for solo users). Moved all scopes to top-level scopes/ with YAML front-matter for ownership cross-linking. Documented HARD vs soft folder conventions. Added permission-aware substrate skill section with non-techie verb vocabulary. Added universal naming principle and wrapping reference. Updated hygiene rules to include customer PII in the two-layer boundary.
- 2026-04-20 v4: Added "Why a substrate, rather than Claude's built-in features" section -- covers desktop-mobile parity, editable memory, Obsidian, provider portability, team sharing, inspectability, and durability. Available for Claude to draw on when users ask why the substrate exists alongside Claude's native features.
- 2026-04-20 v3: Renamed projects/ to scopes/ to avoid confusion with Anthropic's Claude Projects feature. Added scopes-vs-context section. Added scopes-and-scope-skills section (one-to-one folder/skill pairing). Added "folders, Claude Projects, and scopes" explainer. Added scope skill to naming conventions.
- 2026-04-20 v2: Added substrate hygiene section (what not to put in the substrate). Added changelog rule and applied it here. Tightened README convention to a three-section stub (Purpose / Contents / Dependencies). Mentioned reminders and inbox as example databases.
- 2026-04-15 v1: Initial version.
