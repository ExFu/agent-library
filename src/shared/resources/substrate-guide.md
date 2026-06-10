# Substrate Guide

version: 6

This is the reference for how this user's Claude substrate works. Read this whenever you need to understand the structure, conventions, or philosophy behind the way things are organised.

---

## What is a substrate?

A Claude substrate is the combination of files, skills, connectors, and scheduled tasks that together create a persistent way of working with Claude across sessions and devices.

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

The substrate root is a single folder. Inside it, exactly three things plus a guard file:

```
[root]/
  CLAUDE.md               # guard file -- read this first
  exfu/                   # convention base and generated artefacts (not a scope)
  user/                   # special scope: personal context and global defaults
  scopes/                 # the tree of everything else
```

This layout is the same for solo users and team setups. There are no separate `orgs/` or `teams/` directories. Organisational structure is expressed through scopes -- an org is a scope, a team is a scope, a project is a scope.

### The exfu/ directory

Not a scope itself (no `scope.md`). This is the convention base and generated-output home, owned by the ExFu plugin. Contains:

```
exfu/
  latest.txt              # single line: the current convention version (e.g. "v0.3")
  v0.3/                   # convention base for v0.3
    ontology/             # base vocabulary (what is a scope, folder-type, librarian, etc.)
      folder-types/       # one definition file per folder-type
      scope/              # scope format, nesting rules, version resolution
      librarian/          # what librarians are, built-in librarian specs
    context/              # ExFu principles, recommendations
    ...                   # other folder-types as needed
  derived/                # generated output (never hand-edited)
    index.json            # the global index -- whole-substrate map
    librarian-log.json    # librarian run history
    librarian-registry.json
    dashboard/            # substrate visualisation (HTML)
      index.html
```

**Versioning is side-by-side.** When a new convention version ships (e.g. v0.6), it appears as `exfu/v0.6/` alongside `exfu/v0.3/`. Existing scopes keep their version pin until explicitly migrated. The `latest.txt` file points to the current default for new scopes.

### The user/ scope

A real scope (has `scope.md`) for personal context, definitions, and defaults that apply across everything the user does.

```
user/
  scope.md                # no exfu version pin -- always current
  ontology/               # personal definitions, ways of working
  context/                # personal background, preferences, about-me
  skills/                 # personal skill definitions or drafts
  todo/                   # personal tasks (or a pointer to a task tool)
  reminders/              # personal reminders
  inbox/                  # quick capture, unsorted thoughts
  ...                     # any other folder-types as needed
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
    todo/
    databases/
    scopes/               # acme's child scopes, gathered here
      sales/              # a sub-scope
        scope.md
        ontology/
        todo/
      eng/                # another sub-scope
        scope.md
  clients/                # a grouping folder (no scope.md)
    ...
  side-project/           # another scope
    scope.md
    context/
    inbox/
```

**Scopes nest via their own `scopes/` directory.** A scope never holds child scopes loose among its own working folders. It gathers them in a dedicated `scopes/` subdirectory, keeping the scope's own folder-types clean and predictable. The pattern is self-similar: the root has `scopes/`, a scope can have `scopes/`, and so on.

---

## The CLAUDE.md guard file

The substrate root contains a file named `CLAUDE.md`. Its purpose is to prevent Claude from treating the substrate as a generic working folder when the substrate skill is not loaded.

Canonical content:

```
# Don't use this folder

This is a substrate root.

Do not read, write, or otherwise interact with the contents of this folder
unless your session has loaded the substrate skill (or a derivative
that knows the substrate conventions).

If you've accidentally been pointed here, stop and ask the user to either:
- Load the appropriate substrate skill, or
- Work in a different location.

This protects the substrate from being treated as a generic working folder.
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
exfu: v0.3
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
- Status, dates, progress tracking (those belong in `todo/` or the global index)
- Arrays of related skills or dependencies (scope.md is a boundary marker, not a knowledge store)

**The protective header** (the blockquote) appears in both `scope.md` and every `agent.md`. Its job is to catch agents that wander into the substrate without having loaded ExFu skills. The exact wording is consistent across every file.

---

## Folder-types -- the standard vocabulary

Inside any scope, the folder-types are the standard vocabulary of "where things go." Each is a discovery convention first, a storage location second. Its job is to tell an agent *how the user handles this kind of thing for this scope* -- whether the data lives here, or somewhere else entirely.

The base catalogue (defined canonically in `exfu/v0.3/ontology/folder-types/`):

| Folder | What it answers | Analogy |
|---|---|---|
| `ontology/` | What do the concepts and terms in this scope mean? | A glossary |
| `context/` | What background should an agent know about this scope? | A wiki |
| `docs/` | Where are captured documents that need keeping? | A drawer |
| `skills/` | What skill definitions or drafts relate to this scope? | Functions |
| `librarians/` | What scheduled maintenance should happen here? | Cron jobs |
| `todo/` | How does this scope handle tasks? | A task type |
| `reminders/` | How does this scope handle lightweight nudges? | A data type |
| `inbox/` | Where do uncategorised thoughts go for this scope? | A catch-all |
| `databases/` | Where is structured data with schemas for this scope? | Structured records |
| `visualisations/` | Where do agent-created visual outputs live for this scope? | A gallery |

**The catalogue is open.** Any scope may add a folder-type not listed here. If it does, it should define the new type in that scope's `ontology/` so an agent can make sense of it.

### Store-or-point

Store-or-point is a first-class choice for every folder-type. A `todo/` folder may contain actual task files, or its `agent.md` may simply say "tasks are in ClickUp." A `reminders/` folder may hold a markdown file with trigger rules, or it may say "reminders live in Apple Reminders."

The convention guarantees the *location is discoverable*; whether data lives there is per-scope, per-user. The global index tracks the status of each folder-type as `data` (contains files), `pointer` (points elsewhere), or `empty`.

### Scopes only need the folder-types they use

Not every scope uses every folder-type. Most scopes start with just `context/` and maybe `todo/` or `inbox/`. Additional folder-types are created as the work demands them. Don't scaffold more than you need.

---

## The agent.md / readme.md convention -- reference+delta

Every folder-type directory inside a scope contains two files:

### agent.md (for agents)

Follows the reference+delta pattern: reference the upstream convention, then list only local deviations. Structure:

1. **Protective header** (blockquote, always first)
2. **`Follows:` line** naming the upstream convention by versioned path
3. **`Local deviations:` section** listing only what differs from upstream. If nothing differs, omit this section entirely.

A folder with no deviations:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/context.md
```

That's it. Two lines plus the header. The agent reads the upstream convention file for full behaviour.

A folder with deviations:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/todo.md

Local deviations:
- Tasks are tracked in ClickUp, not stored locally
- Use the ClickUp MCP connector for read/write
- Tag all tasks with scope name "acme-sales"
```

The canonical behaviour of each folder-type lives once, in `exfu/v0.3/ontology/folder-types/`. This keeps the substrate lean and prevents convention drift across scopes.

### readme.md (for humans)

The same information, for human eyes. Can be even shorter:

```markdown
Context for the Acme account. See ExFu conventions for details.
```

### When to read agent.md files

- At the start of a session, read the `agent.md` of whatever folder the user is working in
- Before creating content, read the target folder's `agent.md` to understand conventions
- When an `agent.md` has a `Follows:` line, read the upstream convention file too
- When the user references something that might exist elsewhere, check `agent.md` files for cross-references

### Maintaining agent.md and readme.md

When you create a new folder-type directory in a scope, create both files immediately. The `agent.md` needs at minimum the protective header and a `Follows:` line. When you add a local deviation, add it to the `Local deviations:` section.

---

## Ontology and concept resolution

### What an ontology folder is

A collection of definitions -- "here is what this concept means in this scope." Each definition is a file (or a section in a file, depending on density).

- `exfu/v0.3/ontology/` defines the structural vocabulary the entire substrate runs on: what a scope is, what a librarian is, the difference between a todo and a reminder, what each folder-type means.
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
  todo/
  scopes/
    sales/
      scope.md            # name: Sales, parent: Acme
      ontology/
      todo/
      scopes/
        q3-renewal/
          scope.md        # name: Q3 Renewal, parent: Sales
          context/
          todo/
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
- `scopes/acme/todo/` -- the active tasks: follow-ups, proposal drafts, decisions.
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
2. **The substrate dashboard.** The HTML visualisation at `exfu/derived/dashboard/index.html` renders the index into a visual map for non-technical users.

---

## Librarians

Librarians are autonomous maintenance agents that keep the substrate tidy so the user doesn't have to. A librarian is a *definition* of maintenance work that runs on a cadence (typically nightly). The definition lives in a scope's `librarians/` folder-type. The *actual scheduling* is done by the platform -- a Claude scheduled task, or whatever the user's AI platform provides. The librarian file is the spec; the platform is the cron.

### What librarians do, by example

- **Nightly index** (exfu-owned) -- walks the entire substrate and regenerates `exfu/derived/index.json`. This is the foundation librarian; everything else depends on it.
- **Inbox triage** -- sweeps the inbox and routes captured thoughts to where they belong (context, a todo, an ontology note, a doc), or leaves them if that's the user's preference.
- **Reminder check** -- reads every in-scope `reminders/` folder and surfaces the ones whose trigger rules fire today.
- **Archive and collapse** -- retires stale material, folds redundant repetitions together.

What a librarian does is scope-dependent -- it reads that scope's ontology, the user's preferences, and the ExFu defaults to determine its behaviour.

### Librarian definitions

Librarian definitions are markdown files with natural-language instructions -- rich enough for a platform-scheduled agent to read cold and know what to do, but not so procedural that they become brittle scripts. The canonical librarian specs live in `exfu/v0.3/ontology/librarian/`.

Run history is logged at `exfu/derived/librarian-log.json` and the registry of all active librarians lives at `exfu/derived/librarian-registry.json`.

---

## The substrate skill and user vocabulary

For git-backed team substrates, users interact with Claude using natural verbs. The substrate skill maps these to the underlying git operations. No git terminology surfaces to the user.

| User says | What happens |
|---|---|
| save | commit on personal branch |
| share for review | push branch and open a pull request via the git API |
| check for updates | pull from main |
| fix clashes | guided merge conflict resolution |
| approve change | merge the pull request (authorised users only) |

Terms not used with users: branch, draft space, sandbox, fetch, diff, show my changes.

### Permission-aware behaviour

The substrate skill is a single skill, not separate admin and non-admin variants. When it loads, it checks what permissions the current user has on the substrate repository. Users with admin or maintainer rights see the review and approval vocabulary. Users without those rights see only the personal vocabulary (save, share for review, check for updates).

The git repository's own permission model is the gatekeeper. No separate Claude-side permission scaffolding is needed.

The specific permission lookup -- which git provider, which API, which identity integration -- is resolved by the wrapping plugin or the installing Claude. See `cross-cut-extension-and-wrapping.md`.

### Lightweight sync

For team substrates, sync defaults to a script that checks the remote HEAD commit hash against local. Claude wakes only when there is an actual delta. Tokens are consumed only when needed.

---

## Access modes

### Filesystem (preferred on desktop)

When the knowledge base is mounted in a session, use filesystem tools directly. This is faster and supports all operations including delete, move, and rename.

### Connector (universal)

When filesystem access isn't available (mobile, unmounted sessions), use the connector. Limitations:
- No delete -- use the `_DELETED_` prefix convention (see box-filesystem-management skill if installed)
- No move -- copy to destination, mark original as deleted
- Folders are identified by numeric ID, not path -- store frequently used IDs in `user/context/`

---

## Naming conventions

- Lowercase, hyphen-separated: `meeting-notes-2026-04-15.md`
- Date-prefix for time-sensitive files: `YYYY-MM-DD-filename`
- No spaces in filenames
- Deleted files (pending cleanup): `_DELETED_YYYY-MM-DD_original-filename`

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

**Custom folder-types** -- A scope can define folder-types beyond the standard ten. Define the new type in that scope's `ontology/` so agents can make sense of it.

**Custom skills** -- Draft skills in the user's `skills/` folder-type or a scope's `skills/`, test them, then install as proper skills. Skills can encode any repeated workflow, convention, or way of working.

**Custom librarians** -- Define maintenance agents in a scope's `librarians/` folder-type. Librarians can automate any recurring tidying, checking, or routing work.

**Substrate visualisation** -- The dashboard at `exfu/derived/dashboard/index.html` renders the global index into a visual map of the entire substrate. The user opens it in a browser and sees the full scope tree, folder-type status, and ontology chain. It's regenerated nightly.

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

- 2026-06-09 v6: Rewritten for v0.3.0. Replaced orgs/, teams/, and personal-default layout with uniform scope model -- everything is a scope. Replaced _meta/ with exfu/ (convention base at exfu/v0.3/, generated output at exfu/derived/). Removed _trash/ and scratch/. Introduced 10 standard folder-types with store-or-point principle. Added scope.md format (YAML frontmatter with name, parent, exfu version pin). Replaced README.md convention with agent.md reference+delta pattern (Follows: line + local deviations). Added protective headers for scope.md and agent.md. Added librarians (autonomous maintenance agents with cadence-based scheduling). Added global index (exfu/derived/index.json) for whole-substrate discovery. Added versioning model (side-by-side convention versions, per-scope pins). Added user/ as a special unversioned scope. Replaced PII two-layer model with secrets-only ban. Added ontology resolution (parent-chain walk). Added substrate dashboard (exfu/derived/dashboard/).
- 2026-05-02 v5: Revised for v0.2.0. Added two-layer model (substrate proper vs PII layer). Added CLAUDE.md guard file at substrate root. Introduced top-level orgs/ and teams/ folders for multi-org and multi-team support (personal-default layout unchanged for solo users). Moved all scopes to top-level scopes/ with YAML front-matter for ownership cross-linking. Documented HARD vs soft folder conventions. Added permission-aware substrate skill section with non-techie verb vocabulary. Added universal naming principle and wrapping reference. Updated hygiene rules to include customer PII in the two-layer boundary.
- 2026-04-20 v4: Added "Why a substrate, rather than Claude's built-in features" section -- covers desktop-mobile parity, editable memory, Obsidian, provider portability, team sharing, inspectability, and durability. Available for Claude to draw on when users ask why the substrate exists alongside Claude's native features.
- 2026-04-20 v3: Renamed projects/ to scopes/ to avoid confusion with Anthropic's Claude Projects feature. Added scopes-vs-context section. Added scopes-and-scope-skills section (one-to-one folder/skill pairing). Added "folders, Claude Projects, and scopes" explainer. Added scope skill to naming conventions.
- 2026-04-20 v2: Added substrate hygiene section (what not to put in the substrate). Added changelog rule and applied it here. Tightened README convention to a three-section stub (Purpose / Contents / Dependencies). Mentioned reminders and inbox as example databases.
- 2026-04-15 v1: Initial version.
