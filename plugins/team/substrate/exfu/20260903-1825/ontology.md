# ExFu core ontology -- 20260903-1825

This is the complete structural vocabulary of an ExFu substrate, in one file. Read it top to bottom once and you know how everything here is organised: what a scope is, what each folder-type means, how scheduled agents and librarians work, and the authoring rules that keep the substrate ingestible.

It is one file by design. Agents ingest a single complete read far more reliably than a folder of fragments, so the core ontology lives here rather than sharded across many small files. `Follows:` references elsewhere in the substrate point into this file using heading anchors, e.g. `Follows: exfu/20260903-1825/ontology.md#docket`.

**This file is the whole of the versioned contract.** A version directory contains this file and nothing else: a file belongs here if and only if a `Follows:` line can anchor into it. Everything else the plugin ships -- the orientation readme, the principles, the shipped librarian definitions, the skill templates -- lives unversioned at `exfu/` and moves with plugin releases. That boundary is what lets conventions stay frozen while everything around them evolves.

---

## Two registers: library and substrate {#vocabulary}

The same system has two vocabularies, used deliberately.

**User-facing: the Agent Library.** To its user, this whole installation is their library -- ExFu Agent Library: the place their AI's knowledge, skills, and working files live. The scheduled agents that keep it organised are their **Agent Librarians** -- always plural. Not a single all-knowing character: an ecosystem. The library is an edifice; the user appeals to the librarians to fetch things and to do things on their behalf. When teaching new users, a scope may be introduced as a "shelf" -- an analogy, never a rename.

**Internal: the substrate.** Everything below this line is the substrate register: how the library is actually implemented -- scopes, folder-types, the index, the conventions. Agents use this vocabulary with each other and in files. With users they speak library language, and reach for substrate terms only when the user asks how it works underneath.

---

## The substrate

A substrate is the persistent system that gives an AI collaborator memory and working context across sessions: a knowledge base of files (this folder tree), plus skills, connectors, and scheduled agents. No single component is the substrate -- it's the interplay. To its user, the whole thing is their Agent Library.

Structurally it is a root holding the plugin-owned `exfu/` directory, the `durable/` permanent record, the special `user/` scope, and a `scopes/` tree containing everything else. For a depiction of the layout as it appears on disk, see `exfu/readme.md` -- that is orientation material and lives outside the versioned contract so it can track what the plugin actually ships.

---

## The permanent record {#durable}

`durable/` at the substrate root holds the small set of append-only facts **about this library itself** that nothing can regenerate and that no update, refresh, copy, or migration may overwrite. It is not a scope (no scope.md) and not a folder-type, and it exists exactly once, at the root.

It exists because every other home is categorically wrong. `exfu/` is plugin-owned and replaced wholesale on update, so anything kept there can be destroyed by a routine refresh. `exfu/derived/` is explicitly a disposable cache, safe to delete and regenerate. `user/` and `scopes/` hold the user's own material, not the library's record of itself.

Naming: `derived` is rebuilt, `durable` is kept. The two words are deliberately opposites, and between them they state the whole rule.

### The membership test {#durable-test}

> **A path belongs in `durable/` if and only if it is an append-only text record about the library itself that no shipped generator can produce.**

Three conditions, all of which must hold:

1. **Unregenerable.** No librarian or script can reproduce it from material that still exists. The check is concrete: delete it, run every librarian twice, and see whether it comes back. Regeneration *cost* is explicitly not part of the test, so "expensive to recompute" belongs in `exfu/derived/`, not here.
2. **About the library, not about the world.** The record only means anything as a fact about this library's installation, migration, decisions, or operation. A record whose subject is a person, company, deal, or a day in the user's life is domain data and belongs in a scope's [databases/](#databases).
3. **Append-only, human-readable text.** Markdown or JSONL, every entry dated and carrying a stable id, never rewritten in place. A wrong entry is corrected by a later entry saying so.

Condition 3 is what keeps the other two honest: it excludes databases, embeddings, mutable counters, and config files by construction rather than by judgement.

### The carve-out, stated positively {#durable-carveout}

Every skill that refreshes, copies, or migrates a library states the rule in this form, and never as a list of exceptions:

> **A refresh replaces `exfu/`. It never touches `durable/`, `user/`, or `scopes/`.**

An exception list grows silently wrong: each new durable thing is a fresh chance to forget an entry, and a forgotten entry destroys the one category of file that cannot be recovered. Naming what a refresh *may* replace has no such failure mode.

### What lives here

| Path | What it records |
|---|---|
| `ledger/` | The library's logbook (see below) |
| `readme.md` | The membership test and the never-delete rule |

**Materialise on demand applies.** `durable/` ships holding `ledger/` and `readme.md` and gains nothing else until a second genuine tenant exists.

The second tenant is `ledger/grants.md`, the record of consent a user gave for a channel to send on their behalf without asking (see [Grants](#grants)): a decision about the library that nothing can regenerate. Things that plausibly qualify later: other decisions the user was asked to make and gave (consent for a destructive migration, a folder-type declined), which scheduled agents the user enabled or paused (the enabled flag is a human decision; the rest of the registry is a rescan away and stays derived), and records of destructive acts, which afterwards are the only evidence that a missing file was removed on purpose. Idempotence watermarks for the docket's triggers do **not** live here: they are [fire receipts](#fires) inside the scope, because a shared scope must carry its own record of what fired.

**Excluded, with destinations.** No databases, SQLite, vector stores, embeddings, or binary blobs: a library syncs through Dropbox or git, where `-wal` and `-shm` sidecars sync independently and out of order, smart-sync can dehydrate a file mid-transaction, and two surfaces produce a conflicted copy with no merge. Putting that in the one directory whose contents cannot be regenerated is self-defeating. If a fast lookup is genuinely needed it is built per-machine **outside the synced root**, at `~/.exfu/derived/<library-id>/` (see [Version resolution](#versions)), rebuilt by the scheduled runs, and never treated as a source of truth. Text caches and anything rescannable as text go to `exfu/derived/`; the user's own records go to a scope's `databases/` or `docket/`; rendered output goes to `visualisations/`; connector ids and endpoints go in `Local deviations:` on the owning folder-type's agent.md. Secrets are banned from the substrate entirely and that does not change here, which matters more than usual: a directory advertised as never deleted is the most tempting wrong home for a token in the whole tree.

**Conflicted copies.** Append-only is not conflict-free. Two surfaces appending on the same day still produce a conflicted copy, inside the one directory every skill is told not to touch. The merge rule: entries carry stable ids, union them, dedupe by id, order by timestamp, and never delete the conflicted file without appending a record that it was merged.

In the user-facing register this is the library's **permanent record**. Librarians say "permanent record" to users and never say "durable".

### The ledger {#ledger}

`durable/ledger/` is the library's logbook: what has been done to it, when, and by which plugin version.

| File | What it records |
|---|---|
| `migrations.md` | Every migration considered, and its outcome (see [Migrations](#migrations)); per-scope progress journals for migrations that work scope by scope |
| `install.md` | When the library was created, by which plugin version, on which surface |
| `grants.md` | Consent given, and revoked, for a channel to send automatically (see [Grants](#grants)) |
| `readme.md` | What the logbook is, and the append-only rule |

Every directory under `durable/` carries its own `readme.md` stating the rules that govern it, `durable/readme.md` included. These are the one thing here that a plugin update may refresh, because they are shipped explanation rather than recorded fact.

---

## Migrations {#migrations}

A migration moves an existing library from one shape to a newer one. Releases change structure; something has to carry installed libraries across, and that work has to be recorded so any later agent can tell what state a library is actually in.

**Migrations are detected at boot, not scheduled.** A plugin update does not touch the library -- it changes what is installed alongside it. There is no update hook, so nothing can run at update time. The first opportunity to notice is the next session that loads the library boot skill, which compares the migrations the plugin ships against the ledger. Execution then proceeds with the user's consent; it is never an unattended cadence run.

### Definition format

A migration is a markdown file at `exfu/migrations/<id>.md`, using the [scheduled-agent definition format](#scheduled-agents) with migration-specific frontmatter. The id is the filename stem: `<YYYYMMDD-HHMM>-<slug>`, so lexicographic order is application order -- the same property version identifiers rely on.

```yaml
---
name: move-widgets
id: 20260801-0900-move-widgets
kind: migration
cadence: on-update
description: One line saying what shape changes
plugin: "0.11.0 -> 0.12.0"
conventions: "20260903-1825 -> 20260801-0900"   # omit when no conventions change
applies_when: <scope>/widgets/ does not exist    # the TARGET, never the old shape
requires_user_decision: false
reversible: true
---
```

The frontmatter above is deliberately fictional. The real shipped migrations live at `exfu/migrations/`, which is unversioned and moves with plugin releases, while this file is frozen at ship -- so an illustration copied from a real migration would drift out of date and teach the wrong thing. Read the shipped files for real examples; read this for the format.

**A migration's `id` never changes.** It is the migration's own authoring identity, not a pointer at the current conventions, and the filename stem must always equal it. Once a migration ships, libraries record that id in their ledger; re-stamping it would silently orphan those records and make an applied migration look pending. `conventions:` moves freely, because that field records which version movement the migration performs, not what the migration *is*.

`conventions:` appears only when the migration accompanies a new convention version -- its presence marks a deep version upgrade, its absence a general update. The body is the instructions a cold agent carries out, exactly as for any scheduled agent: `scripts:` for deterministic legwork, judgment for the rest.

### Applying

1. **Pending is `shipped` minus `applied`**, in id order, filtered by `applies_when`.
2. **`applies_when` is evaluated against actual library state, never against the ledger alone.** The ledger says what is believed; the filesystem says what is true. When they disagree, report the discrepancy and stop -- do not interpret a way past it.

   Write the condition as **the absence of what the migration produces**, not the presence of what it replaces. Many migrations deliberately leave the old shape in place (superseded convention versions stay readable for scopes still pinned to them), so "the old thing is still there" can remain true forever and re-trigger on every check. Testing for the target makes the condition false once the migration has run, which is what makes it safe to evaluate on a library whose ledger is missing.
3. **A fresh install seeds, it does not replay.** A newly created library is already in the target shape, so install records every shipped migration as `not-applicable`. Without this, every new library would run the entire history of migrations against a shape it never had.
4. **Every outcome is written to `durable/ledger/migrations.md`** -- including `not-applicable` and `failed`, and including any decision the user was asked to make, so a later agent does not re-ask a settled question.
5. **Destructive steps report first and require confirmation.** A migration marked `requires_user_decision: true` must never run unattended.
6. **A migration that works scope by scope keeps a journal.** It inventories every candidate scope first, records each scope's outcome (`converted`, `skipped`, `failed`) as it goes in `durable/ledger/migrations.md` under the migration's heading, makes every step idempotent so a failed scope can be resumed, and records the library-wide outcome as `applied` only when every selected scope verifies. A scope the user or the managing agent declines is `skipped` and may stay on the old shape indefinitely; the deprecated shape remains readable. A migration may write inside `user/` and `scopes/` only where its `writes:` declares it and only after consent; the updater refuses undeclared writes.

### Surfaces and version skew

The same library may be opened from more than one surface (e.g. Claude Code and Cowork), each with its own plugin install, and plugin auto-update can move either of them without the user noticing. The ledger is what makes this safe:

- **Library behind the plugin** -- pending migrations exist. Surface them; offer to apply.
- **Library ahead of the plugin** -- the ledger records migrations this plugin does not ship, so another surface has already moved it forward. **Do not attempt structural work.** Say plainly that this surface's plugin is older and needs updating first.

### Retirement

The plugin ships migrations back to a documented floor, not forever. A library older than the floor is told to reinstall rather than migrated through the full history.

---

## Scope

A scope is a bounded working context. It is the single structural concept in the substrate -- everything is a scope. A project is a scope. A client is a scope. A team is a scope. Your personal workspace is a scope.

A directory is a scope if and only if it contains a `scope.md` file. That file is the boundary marker.

**What a scope is not:** not an org chart (scopes map to whatever contexts you actually work in), not permanent (create, archive, delete as work evolves), not isolated (a scope declares its parent and can draw on ancestor definitions).

### scope.md format {#scope-md}

Minimal by design. The rich picture lives in the global index, not here.

```yaml
---
name: <human-readable name>
purpose: <one-line purpose>
parent: <parent scope name, or "root" for top-level scopes>
exfu: 20260903-1825
---
```

Followed by the protective header (see [Authoring rules](#authoring-rules)) and an optional two-to-three sentence elaboration of purpose.

- **name** -- human-readable; usually matches the directory name but doesn't have to.
- **purpose** -- one sentence, enough for an agent to decide whether to read deeper.
- **parent** -- the parent scope's name, or `root`. A portability safeguard: if the scope is shared or extracted alone, the agent knows context is missing above it.
- **exfu** -- which convention version this scope follows. New scopes pin whatever `latest.txt` says at creation time; pins only change by explicit migration.
- **status** (optional) -- a lifecycle assertion. The only recognised value is `stale`: a deliberate declaration that this scope's content is no longer kept current and should be read with that caveat. Absent means active -- never write `status: active`. Set it when a scope winds down but isn't ready to archive; remove the line to reactivate. The index carries it and the dashboard shows it.

scope.md does NOT contain state, dates, entity lists, or dependencies. Those live in folder-types or the derived index. The `status: stale` assertion is not state in that sense: it is a deliberate declaration that only changes when someone changes it, not a snapshot that drifts out of date on its own.

**Special cases:** the `user/` scope has `parent: none` and no `exfu:` field (it is unversioned and always follows latest). The `exfu/` directory has no scope.md at all -- it is the convention base, not a scope.

### Nesting {#nesting}

Scopes nest through a dedicated `scopes/` subdirectory; the pattern is self-similar at every depth.

1. A scope's own folder-types sit at its root level.
2. Child scopes appear ONLY inside a `scopes/` subdirectory.
3. `scopes/` is structural, not a folder-type: no agent.md, no readme.md.
4. Grouping folders (directories without scope.md, e.g. `scopes/clients/`) may appear inside `scopes/` purely for organisation. Agents ignore them structurally.
5. Depth is unlimited; practical use rarely exceeds three levels.

```
acme/
  scope.md            # parent: root
  context/
  docket/
  scopes/
    q3-renewal/
      scope.md        # parent: Acme
      context/
```

Without the `scopes/` boundary, an agent couldn't tell folder-types (known conventions) from child scopes (independent structure). The boundary makes it unambiguous.

### Version resolution {#versions}

- Every pinned scope reads its conventions from `exfu/<pin>/`.
- The `user/` scope reads through `exfu/latest.txt` (a plain text file naming the current version; used instead of a symlink because sync layers don't handle symlinks reliably).
- Convention versions are identified by their release moment: a shortened UTC timestamp to the minute, `YYYYMMDD-HHMM` (e.g. `20260903-1825`). No seconds, no timezone suffix (always UTC), no ISO punctuation. Every release mints a fresh identifier, so a version directory's contents never change under a stable name -- and plain lexicographic order is chronological order. Version identifiers deliberately share no naming surface with plugin release numbers.
- Early releases used `v0.x` identifiers (`v0.2`, `v0.3`) -- the legacy scheme. Any timestamp identifier is newer than any `v0.x` identifier; never compare the two schemes by raw string sort (digits sort before `v`, which gets the order backwards).
- Convention versions install side by side (`exfu/20260723-1446/`, `exfu/20260903-1825/`). Old scopes keep their pins until explicitly migrated; both bases stay fully functional.
- **A version directory holds `ontology.md` and nothing else.** The plugin's other shipped content -- `exfu/readme.md`, `exfu/principles.md`, `exfu/librarians/`, `exfu/skills/` -- is unversioned and refreshed by plugin updates. The test for what gets frozen: a file belongs in a version directory if and only if a `Follows:` line can anchor into it. Bases shipped before 20260903-1825 also carry those four inside the version directory; that is the older shape, and migration lifts them out.
- `exfu/derived/` is unversioned generated content -- the global index, the scheduled-agent registry and log, the connector availability map (`channels.json`), and the due view (`due.json`). It is a cache of **text** files: never hand-edited, safe to delete and regenerate, and readable from any surface including a phone through the storage connector. (The dashboard itself lives in `exfu/visualisations/dashboard/`; only its data sources live here.)
- **Binary indexes live per machine, outside the synced root**, at `~/.exfu/derived/<library-id>/` (override with `EXFU_DERIVED_DIR`), where `library-id` is a short hash of the library's resolved root path. The search index `library.sqlite` lives there. It is rebuilt from the text records, incrementally by content hash, and is never a source of truth: a moved library simply rebuilds. Nothing binary is ever written inside the library.

---

## Folder-types

Inside any scope, these eight folder-types are the standard vocabulary for where things go:

| Folder | What it answers |
|---|---|
| `ontology/` | What do this scope's concepts and terms mean? |
| `context/` | What background should an agent know here? |
| `skills/` | What skill definitions belong to this scope? |
| `librarians/` | What substrate maintenance runs here on a schedule? |
| `scheduled/` | What business-logic work runs here on a schedule? |
| `docket/` | What is open here: tasks, reminders, and things left for agents, and when and how they get heard? |
| `databases/` | Where do structured, repeating records live? |
| `visualisations/` | Where do visual outputs live? |

Three folder-types from earlier versions, `todo/`, `reminders/` and `inbox/`, are **deprecated**: `docket/` replaces all three. Existing scopes that have them keep working and every reader still understands them (see [Deprecated folder-types](#deprecated)); no new scope creates them.

Three rules govern all of them:

**Materialise on demand.** Create a folder-type only when there is content to put in it, or the user has explicitly asked for it. Never scaffold empty folders "for completeness" -- an empty folder with boilerplate descriptors is noise that every future read pays for. Any agent can add a folder-type to an existing scope later: create the directory, add its `agent.md` with the right `Follows:` line, done. The catalogue guarantees *where things go when they exist*, not that everything exists.

**Store or point.** A folder-type may hold actual data, or its agent.md may say the data lives elsewhere ("tasks are in ClickUp"). The convention guarantees the location is *discoverable*; whether data is stored locally is per-scope, per-user. Pointer folders record the external tool and any connection details as `Local deviations:` in agent.md.

**The catalogue is open.** A scope may add a folder-type not listed here if it genuinely needs one. Define it in the scope's ontology so future agents know what it means.

### ontology/ {#ontology}

The scope's shared vocabulary: definitions of what concepts and terms mean here. Analogy: a glossary.

- Agents read the ontology when entering a scope, and check it before asking the user about an ambiguous term.
- **Ontologies are flat lists of complete files.** One file per concept (or one file for the whole ontology if it's small), each file the *complete* definition of its concept. Never shard a concept across many small files and never nest subfolders of fragments -- completeness-per-file is what makes ingestion reliable.
- Ontology holds *concepts*, not instances. "What a weekly report is" belongs here; an actual weekly report does not. If a thing is an instance of an existing concept, it goes in the folder-type that concept prescribes (a librarian definition goes in librarians/, a record goes in databases/), never in ontology/.
- When a definition touches a term defined elsewhere (parent scope, user/, or this file), annotate the relationship: extension, override, or orthogonal use of the same word.
- Boundaries: background information goes in context/; open matters in docket/; capability definitions in skills/.

### context/ {#context}

Background an agent should know about this scope -- the briefing material that makes an agent useful rather than generic. Analogy: a wiki plus a filing drawer.

- Personal background, project history, stakeholders, situational awareness, decisions and their reasoning.
- **Reference documents live here too**: PDFs, spreadsheets, email transcripts, exported reports, meeting notes worth keeping. A captured document is context with a file extension, sitting beside the prose that gives it meaning. Use subfolders if volume warrants; a flat set of well-named files is fine.
- Context doesn't need to be comprehensive. A few paragraphs that improve an agent's decisions beat an exhaustive wiki nobody maintains.
- Boundaries: definitions of terms go in ontology/; structured repeating records go in databases/; tasks, reminders and things for agents go in docket/.

### skills/ {#skills}

Skill definitions belonging to this scope: the *source of truth* markdown for skills the user installs into their AI platform. Analogy: functions.

- A skill here knows the scope's ontology and conventions rather than duplicating them.
- The user scope's skills/ typically holds the source of the user's personal generated skills -- their way-of-working skill and their docket skill. Edit the source here, then repackage and reinstall (the skill-packaging skill handles that).
- ExFu's own shipped skill sources live at `exfu/skills/` (e.g. the way-of-working template) -- unversioned, because they ship and move with the plugin. Scope skills/ folders hold scope-specific ones.
- Boundaries: scheduled work goes in librarians/ or scheduled/; one-off background goes in context/.

### librarians/ {#librarians}

Scheduled agents whose remit is the substrate itself: keeping this scope tidy, current, and ingestible. Analogy: cron jobs for housekeeping. In the user-facing register these are the user's Agent Librarians -- the ecosystem that keeps their library organised.

- Sweeping the agent backlog, regenerating the index, compacting the docket, dispatching due triggers, archiving stale context, flagging unreferenced versions.
- Each librarian is one definition file in the scheduled-agent format (see [Scheduled agents](#scheduled-agents)). Definitions are *instances*, and they live here -- not in ontology/ (a librarian definition is not a concept).
- ExFu ships its own librarians at `exfu/librarians/` (nightly-index, backlog-sweep, docket-compact, dispatcher, dashboard-generator, version-cleanup, library-updater) -- unversioned, because each one describes a plugin-owned script and moves with it. Registry `source` paths therefore stay stable across convention mints. Scope librarians/ folders hold scope-specific ones.
- Boundaries: work whose remit is the *user's domain* rather than the substrate goes in scheduled/. Ad hoc capabilities go in skills/.

### scheduled/ {#scheduled}

Scheduled agents whose remit is the user's business logic: recurring domain work that runs without the user asking. Analogy: a standing brief given to an assistant.

- Scanning listings sites for a car that matches a brief. Drafting a weekly progress digest. Watching a mailbox for invoices and filing them. Monitoring a dashboard and flagging anomalies.
- Same definition format, same registry, same cadence sessions as librarians -- the mechanics are identical (see [Scheduled agents](#scheduled-agents)). The difference is the remit: librarians maintain the substrate; agents do the user's work.
- Boundaries: if the job's purpose is keeping the substrate itself healthy, it's a librarian and goes in librarians/. If a capability should run only when invoked in conversation, it's a skill.

### docket/ {#docket}

What is open in this scope, and when and how it gets heard. Analogy: a court's docket -- the list of matters to be heard. In the user-facing register it is simply "your docket".

A docket holds three kinds of entry, one JSONL file each, all sharing one record shape (see [Records](#records)):

| File | Holds |
|---|---|
| `todo.jsonl` | Tasks: things with a completion state |
| `reminders.jsonl` | Nudges: things with a surface time or condition |
| `agent-backlog.jsonl` | Things the user leaves **for agents** to attend to -- a queue of work for agents to pull from, never the user's own in-tray |

Beside them, materialised on demand, live the docket's mechanics -- `triggers.jsonl`, `signals.jsonl`, `fires.jsonl`, `channels.jsonl` (see [Docket mechanics](#docket-mechanics)) -- and `archive.jsonl`, where compacted entries go. A `legacy/` subfolder holds a scope's pre-docket folders if it was migrated.

- **One file per collection, not one file per entry.** An agent reads a whole collection in one call from any surface, including through the storage connector on a phone. Entries are appended or rewritten in place under the [record envelope](#records); the active files stay small because the compaction librarian moves `done` and `archived` entries to `archive.jsonl` after 30 days.
- **Store or point, per file.** The pointer pattern is the common case for tasks: most users already have a task tool (ClickUp, Linear, Todoist). A line in agent.md's `Local deviations:` such as `todo: tracked in ClickUp, not stored locally` means there is no `todo.jsonl` while the other files stay local. The folder's value is that an agent always knows *where to ask*.
- **Materialise on demand** still holds: a file appears on its first entry, the folder on its first file. A scope with only `agent.md` and `reminders.jsonl` is a healthy docket.
- **A reminder is an entry with a trigger.** The entry says what; the [trigger](#triggers) says when and how it is surfaced. An entry may have several triggers; a trigger need not point at an entry at all.
- **The agent backlog is not storage.** Its entries get attended to and routed to their real home (context/, todo, databases/...); the backlog-sweep librarian summarises and suggests, the user decides. Anything already categorisable goes straight to its home.
- Boundaries: recurring scheduled work goes in librarians/ or scheduled/; structured repeating records in databases/; background in context/.

### Deprecated folder-types {#deprecated}

`todo/`, `reminders/` and `inbox/` were separate folder-types before `docket/`. They are deprecated, not removed: a scope that has them keeps working, every shipped reader (the boot skill, the index, the dashboard, the daily briefing) still understands their markdown forms, and the docket migration offers to convert them scope by scope when the managing agent judges it doable. No new scope creates them; `scope-setup` offers only `docket/`. Their anchors are kept so existing `Follows:` lines still resolve.

#### todo/ (deprecated) {#todo}

Tasks as markdown checkbox lines (`- [ ]` / `- [x]`) in one or more files, or a pointer to an external tool. Superseded by `docket/todo.jsonl`.

#### reminders/ (deprecated) {#reminders}

Natural-language reminder rules in markdown, one per line, the surface date first. Superseded by `docket/reminders.jsonl` with a trigger per dated reminder.

#### inbox/ (deprecated) {#inbox}

One markdown file per captured item. Superseded by `docket/agent-backlog.jsonl`, which also renames the concept: the queue was always for agents, not the user's in-tray.

### databases/ {#databases}

Structured data with repeating records and consistent fields. Analogy: a spreadsheet or record store.

- Contacts, CRM records, opportunity pipelines, inventories, sightings logs -- and **recurring personal records like daily logs or journals**: anything written repeatedly with the same shape is a database, even when each record is prose. The test: "will there be another one of these next week, with the same fields?"
- Each database is a subfolder (or single file) with a `schema.md` describing the record shape; record filenames are the natural keys (so wikilinks resolve).
- Pointer form names the external system and its schema ("contacts live in HubSpot; fields: name, company, role, last-contact").
- Boundaries: one-off reference documents go in context/; unstructured captures for agents go in the docket's agent backlog.

### visualisations/ {#visualisations}

Visual outputs produced by agents for this scope: HTML pages, dashboards, charts, diagrams. Analogy: a gallery.

- Each visualisation in its own subfolder with all of its assets, named for what it shows.
- The ExFu-shipped example is the substrate dashboard, generated nightly at `exfu/visualisations/dashboard/index.html` -- the root's own gallery. It reads its data from `exfu/derived/`; the rendered page lives in the gallery because visual outputs are what this folder-type is for.
- Boundaries: source data goes in databases/; the thing that *generates* a recurring visualisation is a librarian or agent.

---

## Docket mechanics {#docket-mechanics}

The docket's entries are deliberately thin. Everything that makes them *do* something -- fire at a time, react to an event, reach a person -- is a separate, structured file joined to the entry by id. This section is the contract for those files. Programs read them; agents write them; prose remains the source of intent throughout.

### Records and the envelope {#records}

Every docket entry is one JSON object on one line:

```json
{"id":"20260903T141200Z-7F3A9QK2MB",
 "title":"Chase the Acme security questionnaire",
 "notes":"Sent 20 Aug, Priya said end of month.",
 "agent_notes":"Only surface after the Acme call has happened. If no reply by Friday, suggest escalating to Mark.",
 "status":"open",
 "created":"2026-09-03T14:12:00Z","updated":"2026-09-03T14:12:00Z","revision":1,
 "keywords":["acme","security questionnaire","priya"]}
```

- `title`; `notes` for humans; `agent_notes` -- freeform instructions for agents (timing, conditions, dependencies, "only show when"); `status` one of `open | done | archived` (done means completed; archived means closed without doing, or aged out of view); `keywords`, optional, written by the saving agent as the search layer that needs no model.
- **No ontological fields.** No priority, tags, dependency or recurrence columns. They live in `agent_notes` as prose so agents can wire things together without the schema anticipating them. A facet that a *program* must read arrives as a [mixin](#mixins), never as a column.
- **Ids are library-wide**: a UTC timestamp to the second plus at least ten random base32 characters, checked against the index for collisions. Any file may reference any record by id alone.
- **The envelope for mutable rows** is `id`, `created`, `updated`, `revision` (an integer the writer increments) and an optional `deleted: true` tombstone. Sync conflicts produce a `(conflicted copy)` text sibling; the fold unions rows by `id`, keeps the highest `revision`, then the latest `updated`, then the lexically lowest writer handle, and removes the sibling. Signals and fire receipts are immutable and never fold: a conflicted copy is unioned by id and that is the whole rule.
- **The archive envelope** is the entry plus `kind: todo | reminder | agent-backlog`, so `archive.jsonl` can hold all three.

### Mixins {#mixins}

A mixin is a JSONL file whose rows decorate other records by reference. It is how the docket grows facets without growing its schema, and it can attach to anything with an identity:

```json
"target": {"type": "docket-entry", "scope": "acme", "id": "20260903T141200Z-7F3A9QK2MB"}
```

`type` is `docket-entry | document | record | scope`; documents and database records are addressed by path relative to their scope, scopes by name. Referential integrity across files is the cost: the compaction librarian removes a mixin row 30 days after its target closes or disappears, and the index flags orphans until then. Triggers are the first mixin; a responsibilities mixin for shared scopes that need a full RACI grid would be another.

### Triggers {#triggers}

A trigger is a scope's statement that at some moment, or on some occurrence, something should be assessed by an agent, together with how that assessment is to be handled. A reminder is an entry with a trigger; an email check, a follow-up chase, or "see whether the build passed" is a trigger with no entry at all. `docket/triggers.jsonl`:

```json
{"id":"20260903T150200Z-A91CQ7ZP4R",
 "target":{"type":"docket-entry","scope":"acme","id":"20260903T141200Z-7F3A9QK2MB"},
 "assess":"Surface the Acme questionnaire chase if the Acme call has happened; otherwise leave it.",
 "when":{"mode":"cron","spec":"0 9 * * 1-5","tz":"Europe/London"},
 "on":null,
 "handler":{"kind":"agent","weight":"light","ref":null},
 "channel":"slack-dm",
 "owner":"al",
 "status":"armed",
 "created":"2026-09-03T15:02:00Z","updated":"2026-09-03T15:02:00Z","revision":1}
```

- `assess` is prose: the brief handed to whatever handles the trigger.
- `when` is a [schedule mode](#schedule-modes); `tz` is an IANA zone name on every time-based trigger. `on` names a [signal](#signals). A trigger may carry both: "on that signal, but only inside this schedule's window".
- `handler.kind` is `deliver` (send the target entry, or `assess` when there is none, through the channel), `agent` (spin up a sub-agent of the given `weight` with `assess` as its brief), or `definition` (run a registered scheduled-agent or librarian named by `ref`). `weight` is `light | medium | heavy`, mapped at dispatch to the cheapest, a mid, and the strongest model available. How a trigger is handled always travels with the trigger, inline or by reference.
- `channel` names a [channel](#channels); absent means pull. `owner` is an [actor](#actors) handle or `any`.
- `status` is `armed | paused | disarmed`. A `once` trigger is disarmed after its receipt is written; a trigger is paused, not disarmed, after three consecutive failed fires.
- **A trigger row is authored, and near-immutable.** The dispatcher never writes to it except to disarm a `once` or pause a failing one. Everything that happens to a trigger is a [fire receipt](#fires). Watermarks on the trigger row would make this the most-written file in a synced library while the conflict fold runs nightly.

### Signals {#signals}

A signal is a fact an agent recorded about the world at a moment, addressed to whoever is listening. Signals are the arc between actions: a fired trigger's handler reports the signals it observed or produced, the dispatcher appends them to `docket/signals.jsonl`, and any trigger may be armed on a signal name. "Check email for the Acme reply, and report `acme-reply-seen` if there is one" plus "on `acme-reply-seen`, draft the follow-up" is a two-step workflow that neither trigger knows about. The graph is implied, rendered by the dashboard from the index, never authored.

```json
{"id":"20260904T090340Z-S1GN4LQ8WD","name":"acme-reply-seen","at":"2026-09-04T09:03:40Z","scope":"user","source":"<trigger id>","payload":"Priya replied 09:01, attached the questionnaire."}
```

- **Names are library-global strings**; `scope` records where the signal was emitted. A `user/` email check may feed an Acme-scope follow-up.
- **Append-only and immutable**, with a flat 30-day retention swept by the compaction librarian. Nothing is "consumed": the producer does not know who listens.
- **Each trigger watermarks the signals it has seen** through its receipts and scans forward from the last one. A signal id is the idempotency key: one trigger fires at most once per signal.
- **The handler reports; the dispatcher never assumes.** A trigger declares nothing about what it will emit.
- **Payload** is prose plus optional small JSON. Shape changes are more prose.
- **Silent failure is designed out**: the index flags a trigger armed on a name nothing has ever emitted. **Loops are bounded across ticks**: at most five fires per signal name per 24 hours, beyond which the dispatcher suppresses and surfaces the trigger. **Latency is stated**: an `on` trigger resolves within one dispatcher cadence tick, not in real time.

Signals are scope data: synced, small, authored. Not `durable/` (about the world, regenerable in principle); not `exfu/derived/` (authored, not rebuilt).

### Fire receipts {#fires}

`docket/fires.jsonl` is the append-only record of triggers firing. It lives beside the triggers because a shared scope must carry its own record of what fired. Two immutable rows per occurrence:

```json
{"id":"...","occurrence":"<trigger id>@2026-09-04T09:00+01:00","trigger":"<trigger id>","phase":"intent","actor":"al","machine":"al-mbp","at":"2026-09-04T09:03:11Z"}
{"id":"...","occurrence":"<trigger id>@2026-09-04T09:00+01:00","trigger":"<trigger id>","phase":"result","status":"delivered","signals":["acme-chase-surfaced"],"idempotency_key":"...","at":"2026-09-04T09:03:40Z"}
```

- The occurrence id is the trigger id plus the scheduled instant, or plus the signal id for `on` triggers.
- **Intent before acting, result after.** A crash between the two leaves a visible half-receipt that the next run treats as "attempted, outcome unknown" and does not blindly repeat. Where a connector accepts an idempotency key it is passed and recorded; where it does not, delivery is at-least-once and the receipt says so.
- `status` is `delivered | drafted | failed | skipped | suppressed`. Three consecutive `failed` results pause the trigger, reusing the registry's flag-after-three convention.
- **Misfire policy, one rule:** at most once per trigger per dispatcher run, never backfill; a run that finds several elapsed occurrences fires the most recent and records the rest as `skipped`.
- Receipts are the audit trail, the "last delivered" watermark, the per-trigger signal watermark, and the claim in a shared scope (see [Actors](#actors)). Retention: 90 days.

### Actors {#actors}

An actor is a person or an agent with a handle. A solo library's actor is the one `durable/ledger/install.md` names. In a shared scope each participant's handle is whatever their own library's `install.md` says, and the scope's `docket/agent.md` lists the participants under `Local deviations:`.

- Every trigger carries `owner`, defaulting to the library's actor. A dispatcher fires only triggers it owns or that are `any`. Ownership is the first line of defence against double-firing and needs no coordination.
- For `any` triggers in a shared scope, **the claim is the intent receipt**: before acting, a dispatcher appends `intent` naming its actor and machine, re-reads `fires.jsonl`, and if another actor's `intent` for the same occurrence is present, the lexically lower handle proceeds and the other records `skipped`. Sync latency leaves a small window in which both may act; dispatcher start times are jittered by handle to shrink it, and the residual risk is stated as at-least-once for `any` triggers, which is why outward `auto` channels are never `any`-fireable.
- Full RACI, if a scope ever needs it, is a `responsibilities.jsonl` mixin.

### Channels {#channels}

A channel is a way the library reaches a person. `docket/channels.jsonl`, declared by any scope; `user/` is where most people declare their default:

```json
{"id":"20260903T160000Z-CH4NN3LQ2A","name":"slack-dm","kind":"dm","via":"slack","target":"@al","send":"auto","created":"...","updated":"...","revision":1}
{"id":"20260903T160100Z-CH4NN3LQ2B","name":"acme-team","kind":"broadcast","via":"slack","target":"#acme-project","send":"draft","created":"...","updated":"...","revision":1}
```

- `kind`: `pull` (the dashboard and session start; always present, never declared), `dm` (reaches one named actor), `broadcast` (reaches several people or an unspecified audience). Reach is by who receives, not by medium: a message to a colleague's agent is `dm` to that actor.
- `via` is the connector that sends; `target` the address, never a secret; `send` is the consent attribute (see [Grants](#grants)).
- A trigger names a channel; resolution walks the scope chain (own scope, parents, `user/`). An unresolvable name degrades to pull, and the undelivered count surfaces at session start as well as on the dashboard.
- Which connectors are actually present on this surface is regenerable and lives in `exfu/derived/channels.json`.

### Grants {#grants}

Whether the dispatcher may send unattended is decided per channel. `send: draft` is the default: the handler prepares the message where the connector keeps drafts, or on the dashboard's "ready to send" list, and a person sends it. `send: auto` means the dispatcher sends without waiting, which is the whole point of a `dm` to oneself and is legitimate for pre-authorised working relationships.

- **The grant is authoritative, not the flag.** Elevation is an append-only entry in `durable/ledger/grants.md` (who, when, which channel id; revoked when). The dispatcher validates an active grant before every `auto` send; editing `send: auto` in place grants nothing.
- **Caps bound one misread rule**: a per-channel daily send cap and a per-run cap; a tripped cap degrades to `draft` and records `suppressed`.
- Until the outward mechanism is complete, `auto` is honoured only on a `dm` whose target is the trigger's owner; outward `auto` is declared, granted and shown, but drafted.

### Schedule modes {#schedule-modes}

| mode | meaning | next occurrence | after firing |
|---|---|---|---|
| `once` | dump-and-done | `when.at`, an instant, with `tz` | disarmed |
| `cron` | a 5-field cron spec (minute hour day-of-month month day-of-week; standard ranges and lists; no seconds, no `@` aliases), evaluated in `when.tz` | computed by the dispatcher from the spec and the last `result` receipt | armed |
| `on-signal` | fire when the signal named by `on` appears, optionally only inside a `when` window | none; the signal is the moment | armed; at most once per signal id |

- Natural-language rules ("every other Monday", "first working day of the month") are resolved **once, at authoring time**, by the agent that saves the trigger, into a `cron` spec or a `once` instant; the original wording is kept in `assess` so a person can see what was meant and correct the spec.
- "Re-arm when the task is completed" is `on-signal` on `entry-completed:<entry id>`, which the compaction librarian and the personal docket skill emit whenever an entry's status changes.
- DST is handled by the zone: an occurrence that does not exist on a spring-forward day is skipped; one that exists twice on a fall-back day fires once. Misfires follow the fire-receipt rule.

### The dispatcher {#dispatcher}

One shipped librarian, on the `hourly` cadence, using the cheapest model available. It never boots the library and never reads anything extraneous: it refreshes the index incrementally, reads the due view (one query, or `exfu/derived/due.json` where the index is unavailable, rejecting a stale one), and for each due trigger it owns or that is `any`: writes the intent receipt, does what the handler says, writes the result receipt with the signals the handler reported, and exits. It never opens `todo.jsonl`, `context/`, or the user's wow. The boot skill runs the same due-view check at session start and delivers pull-channel items in the session, so a person in Claude several times a day is served faster than any cron. The dispatcher runs where it has the local filesystem and can choose a sub-agent's model, which today means a Claude Code Desktop local scheduled task; a surface without those gets the boot-time check and the dashboard.

---

## Scheduled agents {#scheduled-agents}

A scheduled agent is recurring work defined as *agent instructions*: a markdown file an AI session reads cold and carries out with judgment, on a cadence, without the user asking. Scheduled agents come in two classes with identical mechanics and different remits:

- **Librarians** maintain the substrate itself. They live in `librarians/` folders.
- **Agents** (business agents) do the user's recurring domain work. They live in `scheduled/` folders.

### Definition format

A definition is a markdown file with YAML frontmatter. Required: `name`, `cadence`, `description`. The body below the frontmatter is the work itself -- instructions a cold agent can follow.

```yaml
---
name: nightly-index
cadence: nightly          # nightly | weekly | hourly | on-demand
description: Walks the substrate and regenerates the global scope index
scripts:                  # optional: deterministic tools the body tells you to run
  - scheduled-tasks/substrate-index/index.py
reads: ["*/scope.md"]     # optional: what it touches, for conflict checks and the dashboard
writes: ["exfu/derived/index.json"]
depends_on: []            # optional: agents that must run first within the same cadence
---
```

Where a definition references a script, the script is a *tool* -- deterministic legwork like walking a tree or rendering HTML. Run it, check the result, apply judgment to what comes back. The script never replaces the agentic work. A definition with no scripts is fully agentic.

Definitions should be idempotent: running one twice produces the same result as running it once.

### Registry and execution

Registration is what makes a definition live. The registry at `exfu/derived/agent-registry.json` lists every registered scheduled agent: name, `kind` (`librarian` or `agent`), cadence, source path, enabled flag, and run health (last run, last status, consecutive failures). A definition file that exists but isn't registered does nothing -- which is also how you stage work for the user to approve.

One scheduled task per cadence (e.g. `nightly-agents`, created in the user's AI platform) is the execution environment. The `hourly` cadence hosts the docket's [dispatcher](#dispatcher) and should be created as a local task with the cheapest model selected. In that session, Claude asks the helper what is due, then for each due definition: reads it, does the work, and records the outcome before moving on. Within a cadence, librarians run before business agents (the substrate gets tidied and the index refreshed before domain work consumes them), then dependency order applies.

The run log lives at `exfu/derived/agent-log.json`. Both files are derived cache: managed by the registration skill and the cadence sessions, never hand-edited.

---

## Way of working (wow) {#wow}

A way of working is ExFu's concept for a person's standing operating manual: how their substrate is laid out (the navigation map) and the thin kernel of always-on instructions that apply to every session (communication style, decision defaults, hard constraints).

- It materialises as a personal skill ("wow") generated from the template at `exfu/skills/wow-template.md`, installed into the user's AI platform, and loaded at the start of every session.
- The skill's source of truth lives in the substrate at `user/skills/wow/`; the installed copy is a packaged artefact. Edit the source, repackage, reinstall.
- A wow is a *map plus kernel*, never a workflow engine. Workflow logic belongs in skills, scheduled agents, or scope content. If the wow grows past a few screens, something is in the wrong place.

---

## Authoring rules {#authoring-rules}

These apply to every file an agent writes inside the substrate.

### File economy

Fewer, more complete files. Every extra file is a read a future agent might skip; a concept split across five fragments will be half-ingested. Prefer one complete file over a folder of shards; prefer extending an existing file over creating a sibling; create subfolders only when volume genuinely demands it. This is why this ontology is one file.

### The agent.md reference+delta pattern {#agent-md}

Every materialised folder-type directory contains an `agent.md`:

1. **Protective header** (always first, verbatim):

   ```
   > This folder follows ExFu conventions. If you haven't loaded them yet,
   > ask your user to set you up with their WoW or ExFu skills.
   ```

2. **`Follows:` line** naming the convention it implements, by versioned anchor into this file:

   `Follows: exfu/20260903-1825/ontology.md#docket`

3. **`Local deviations:`** -- a bullet list of only what differs from the convention (e.g. "Tasks are tracked in ClickUp, folder 901514259169"). Omit the section entirely when nothing differs.

A folder with no deviations is the header plus one line. A sibling `readme.md` with a single human-friendly sentence is optional and conventional.

### Descriptors carry no state

agent.md, readme.md, and scope.md describe what a folder or scope *is for* -- static facts that stay true. They never capture state: no "currently empty", no item counts, no "last updated", no status notes. State is only true at write time and goes stale silently, misleading every later reader. Current state belongs in the derived index, the dashboard, and the content itself.

The one exception is scope.md's optional `status: stale` assertion (see [scope.md format](#scope-md)). It passes because it is a declaration, not a snapshot: it stays true until someone deliberately removes it, so it cannot drift out of date silently.

### Naming

Lowercase, hyphen-separated filenames (`who-i-am.md`). Date-prefix time-sensitive files (`2026-06-10-skill-drafts.md`). Database record filenames are their natural keys, kept stable so wikilinks resolve.

### Annotate intent

Real knowledge is messy and won't always fit the "right" place. When placement is a judgment call, say *why* in the file or its agent.md deviations -- an agent that knows why something lives somewhere can work with imperfect placement; one that only knows where, cannot.
