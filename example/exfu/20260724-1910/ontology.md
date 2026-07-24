# ExFu core ontology -- 20260724-1910

This is the complete structural vocabulary of an ExFu substrate, in one file. Read it top to bottom once and you know how everything here is organised: what a scope is, what each folder-type means, how scheduled agents and librarians work, and the authoring rules that keep the substrate ingestible.

It is one file by design. Agents ingest a single complete read far more reliably than a folder of fragments, so the core ontology lives here rather than sharded across many small files. `Follows:` references elsewhere in the substrate point into this file using heading anchors, e.g. `Follows: exfu/20260724-1910/ontology.md#todo`.

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

Things that plausibly qualify later: decisions the user was asked to make and gave (consent for a destructive migration, a folder-type declined), which scheduled agents the user enabled or paused (the enabled flag is a human decision; the rest of the registry is a rescan away and stays derived), idempotence watermarks recording how far a recurring agent has already read, and records of destructive acts, which afterwards are the only evidence that a missing file was removed on purpose.

**Excluded, with destinations.** No databases, SQLite, vector stores, embeddings, or binary blobs: a library syncs through Dropbox or git, where `-wal` and `-shm` sidecars sync independently and out of order, smart-sync can dehydrate a file mid-transaction, and two surfaces produce a conflicted copy with no merge. Putting that in the one directory whose contents cannot be regenerated is self-defeating. If a fast lookup is genuinely needed it is built per-machine outside the synced root, rebuilt by the nightly run, and never treated as a source of truth. Search indexes and anything rescannable go to `exfu/derived/`; the user's own records go to a scope's `databases/`; rendered output goes to `visualisations/`; connector ids and endpoints go in `Local deviations:` on the owning folder-type's agent.md. Secrets are banned from the substrate entirely and that does not change here, which matters more than usual: a directory advertised as never deleted is the most tempting wrong home for a token in the whole tree.

**Conflicted copies.** Append-only is not conflict-free. Two surfaces appending on the same day still produce a conflicted copy, inside the one directory every skill is told not to touch. The merge rule: entries carry stable ids, union them, dedupe by id, order by timestamp, and never delete the conflicted file without appending a record that it was merged.

In the user-facing register this is the library's **permanent record**. Librarians say "permanent record" to users and never say "durable".

### The ledger {#ledger}

`durable/ledger/` is the library's logbook: what has been done to it, when, and by which plugin version.

| File | What it records |
|---|---|
| `migrations.md` | Every migration considered, and its outcome (see [Migrations](#migrations)) |
| `install.md` | When the library was created, by which plugin version, on which surface |
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
conventions: "20260724-1910 -> 20260801-0900"   # omit when no conventions change
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
exfu: 20260724-1910
---
```

Followed by the protective header (see [Authoring rules](#authoring-rules)) and an optional two-to-three sentence elaboration of purpose.

- **name** -- human-readable; usually matches the directory name but doesn't have to.
- **purpose** -- one sentence, enough for an agent to decide whether to read deeper.
- **parent** -- the parent scope's name, or `root`. A portability safeguard: if the scope is shared or extracted alone, the agent knows context is missing above it.
- **exfu** -- which convention version this scope follows. New scopes pin whatever `latest.txt` says at creation time; pins only change by explicit migration.

scope.md does NOT contain state, status, dates, entity lists, or dependencies. Those live in folder-types or the derived index.

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
  todo/
  scopes/
    q3-renewal/
      scope.md        # parent: Acme
      context/
```

Without the `scopes/` boundary, an agent couldn't tell folder-types (known conventions) from child scopes (independent structure). The boundary makes it unambiguous.

### Version resolution {#versions}

- Every pinned scope reads its conventions from `exfu/<pin>/`.
- The `user/` scope reads through `exfu/latest.txt` (a plain text file naming the current version; used instead of a symlink because sync layers don't handle symlinks reliably).
- Convention versions are identified by their release moment: a shortened UTC timestamp to the minute, `YYYYMMDD-HHMM` (e.g. `20260724-1910`). No seconds, no timezone suffix (always UTC), no ISO punctuation. Every release mints a fresh identifier, so a version directory's contents never change under a stable name -- and plain lexicographic order is chronological order. Version identifiers deliberately share no naming surface with plugin release numbers.
- Early releases used `v0.x` identifiers (`v0.2`, `v0.3`) -- the legacy scheme. Any timestamp identifier is newer than any `v0.x` identifier; never compare the two schemes by raw string sort (digits sort before `v`, which gets the order backwards).
- Convention versions install side by side (`exfu/20260723-1446/`, `exfu/20260724-1910/`). Old scopes keep their pins until explicitly migrated; both bases stay fully functional.
- **A version directory holds `ontology.md` and nothing else.** The plugin's other shipped content -- `exfu/readme.md`, `exfu/principles.md`, `exfu/librarians/`, `exfu/skills/` -- is unversioned and refreshed by plugin updates. The test for what gets frozen: a file belongs in a version directory if and only if a `Follows:` line can anchor into it. Bases shipped before 20260724-1910 also carry those four inside the version directory; that is the older shape, and migration lifts them out.
- `exfu/derived/` is unversioned generated content -- the global index, the scheduled-agent registry and log. It is a cache: never hand-edited, safe to delete and regenerate. (The dashboard itself lives in `exfu/visualisations/dashboard/`; only its data sources live here.)

---

## Folder-types

Inside any scope, these ten folder-types are the standard vocabulary for where things go:

| Folder | What it answers |
|---|---|
| `ontology/` | What do this scope's concepts and terms mean? |
| `context/` | What background should an agent know here? |
| `skills/` | What skill definitions belong to this scope? |
| `librarians/` | What substrate maintenance runs here on a schedule? |
| `scheduled/` | What business-logic work runs here on a schedule? |
| `todo/` | How does this scope handle tasks? |
| `reminders/` | How does this scope handle time-based nudges? |
| `inbox/` | Where do uncategorised captures go? |
| `databases/` | Where do structured, repeating records live? |
| `visualisations/` | Where do visual outputs live? |

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
- Boundaries: background information goes in context/; task conventions in todo/; capability definitions in skills/.

### context/ {#context}

Background an agent should know about this scope -- the briefing material that makes an agent useful rather than generic. Analogy: a wiki plus a filing drawer.

- Personal background, project history, stakeholders, situational awareness, decisions and their reasoning.
- **Reference documents live here too**: PDFs, spreadsheets, email transcripts, exported reports, meeting notes worth keeping. A captured document is context with a file extension, sitting beside the prose that gives it meaning. Use subfolders if volume warrants; a flat set of well-named files is fine.
- Context doesn't need to be comprehensive. A few paragraphs that improve an agent's decisions beat an exhaustive wiki nobody maintains.
- Boundaries: definitions of terms go in ontology/; structured repeating records go in databases/; tasks go in todo/.

### skills/ {#skills}

Skill definitions belonging to this scope: the *source of truth* markdown for skills the user installs into their AI platform. Analogy: functions.

- A skill here knows the scope's ontology and conventions rather than duplicating them.
- The user scope's skills/ typically holds the source of the user's personal generated skills -- their way-of-working skill, reminders skill, inbox skill. Edit the source here, then repackage and reinstall (the skill-packaging skill handles that).
- ExFu's own shipped skill sources live at `exfu/skills/` (e.g. the way-of-working template) -- unversioned, because they ship and move with the plugin. Scope skills/ folders hold scope-specific ones.
- Boundaries: scheduled work goes in librarians/ or scheduled/; one-off background goes in context/.

### librarians/ {#librarians}

Scheduled agents whose remit is the substrate itself: keeping this scope tidy, current, and ingestible. Analogy: cron jobs for housekeeping. In the user-facing register these are the user's Agent Librarians -- the ecosystem that keeps their library organised.

- Sweeping the inbox, regenerating the index, reconciling todo/ with an external tracker, archiving stale context, flagging unreferenced versions.
- Each librarian is one definition file in the scheduled-agent format (see [Scheduled agents](#scheduled-agents)). Definitions are *instances*, and they live here -- not in ontology/ (a librarian definition is not a concept).
- ExFu ships its own librarians at `exfu/librarians/` (nightly-index, inbox-triage, dashboard-generator, version-cleanup) -- unversioned, because each one describes a plugin-owned script and moves with it. Registry `source` paths therefore stay stable across convention mints. Scope librarians/ folders hold scope-specific ones.
- Boundaries: work whose remit is the *user's domain* rather than the substrate goes in scheduled/. Ad hoc capabilities go in skills/.

### scheduled/ {#scheduled}

Scheduled agents whose remit is the user's business logic: recurring domain work that runs without the user asking. Analogy: a standing brief given to an assistant.

- Scanning listings sites for a car that matches a brief. Drafting a weekly progress digest. Watching a mailbox for invoices and filing them. Monitoring a dashboard and flagging anomalies.
- Same definition format, same registry, same cadence sessions as librarians -- the mechanics are identical (see [Scheduled agents](#scheduled-agents)). The difference is the remit: librarians maintain the substrate; agents do the user's work.
- Boundaries: if the job's purpose is keeping the substrate itself healthy, it's a librarian and goes in librarians/. If a capability should run only when invoked in conversation, it's a skill.

### todo/ {#todo}

How this scope handles tasks -- things with a completion state. Analogy: a task list.

- The pointer pattern is the common case: most users already have a task tool (ClickUp, Linear, Todoist). The folder's value is that an agent always knows *where to ask* about tasks for this scope.
- Stored form: task files or a task list in markdown, each task with at least a description and completion state.
- Boundaries: time-based nudges without a completion state go in reminders/; fleeting thoughts in inbox/.

### reminders/ {#reminders}

Lightweight time-based or condition-based nudges, with no completion state. Analogy: a notification list.

- "Flag the VAT return from the 20th of the month." "Chase if no reply within 3 days." One markdown file of natural-language rules covers most scopes; pointer form names the external tool (Apple Reminders, calendar).
- A reminder may *trigger* a todo, but the reminder is the trigger, not the task.
- Boundaries: recurring scheduled work goes in librarians/ or scheduled/; tasks in todo/.

### inbox/ {#inbox}

Quick capture for things that don't have a home yet. Analogy: an inbox tray.

- Deliberately unstructured; its job is to lower the friction of capture. One file per captured item, named by date or topic.
- Inbox is not storage. Items get triaged into their real home (context/, todo/, databases/...) -- the inbox-triage librarian sweeps and suggests; the user decides.
- Boundaries: anything already categorisable goes straight to its folder-type.

### databases/ {#databases}

Structured data with repeating records and consistent fields. Analogy: a spreadsheet or record store.

- Contacts, CRM records, opportunity pipelines, inventories, sightings logs -- and **recurring personal records like daily logs or journals**: anything written repeatedly with the same shape is a database, even when each record is prose. The test: "will there be another one of these next week, with the same fields?"
- Each database is a subfolder (or single file) with a `schema.md` describing the record shape; record filenames are the natural keys (so wikilinks resolve).
- Pointer form names the external system and its schema ("contacts live in HubSpot; fields: name, company, role, last-contact").
- Boundaries: one-off reference documents go in context/; unstructured captures in inbox/.

### visualisations/ {#visualisations}

Visual outputs produced by agents for this scope: HTML pages, dashboards, charts, diagrams. Analogy: a gallery.

- Each visualisation in its own subfolder with all of its assets, named for what it shows.
- The ExFu-shipped example is the substrate dashboard, generated nightly at `exfu/visualisations/dashboard/index.html` -- the root's own gallery. It reads its data from `exfu/derived/`; the rendered page lives in the gallery because visual outputs are what this folder-type is for.
- Boundaries: source data goes in databases/; the thing that *generates* a recurring visualisation is a librarian or agent.

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

One scheduled task per cadence (e.g. `nightly-agents`, created in the user's AI platform) is the execution environment. In that session, Claude asks the helper what is due, then for each due definition: reads it, does the work, and records the outcome before moving on. Within a cadence, librarians run before business agents (the substrate gets tidied and the index refreshed before domain work consumes them), then dependency order applies.

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

   `Follows: exfu/20260724-1910/ontology.md#todo`

3. **`Local deviations:`** -- a bullet list of only what differs from the convention (e.g. "Tasks are tracked in ClickUp, folder 901514259169"). Omit the section entirely when nothing differs.

A folder with no deviations is the header plus one line. A sibling `readme.md` with a single human-friendly sentence is optional and conventional.

### Descriptors carry no state

agent.md, readme.md, and scope.md describe what a folder or scope *is for* -- static facts that stay true. They never capture state: no "currently empty", no item counts, no "last updated", no status notes. State is only true at write time and goes stale silently, misleading every later reader. Current state belongs in the derived index, the dashboard, and the content itself.

### Naming

Lowercase, hyphen-separated filenames (`who-i-am.md`). Date-prefix time-sensitive files (`2026-06-10-skill-drafts.md`). Database record filenames are their natural keys, kept stable so wikilinks resolve.

### Annotate intent

Real knowledge is messy and won't always fit the "right" place. When placement is a judgment call, say *why* in the file or its agent.md deviations -- an agent that knows why something lives somewhere can work with imperfect placement; one that only knows where, cannot.
