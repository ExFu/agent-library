# Substrate Guide

version: 4

This is the reference for how this user's Claude substrate works. Read this whenever you need to understand the structure, conventions, or philosophy behind the way things are organised.

---

## What is a substrate?

A Claude substrate is the combination of files, skills, connectors, and scheduled tasks that together create a persistent way of working with Claude across sessions and devices.

No single component is the substrate. It's the interplay between them:
- **Skills** tell Claude how to behave and what conventions to follow
- **Files** in the knowledge base store context, instructions, plans, and data
- **Connectors** (like the Box MCP connector) make files accessible from any Claude surface
- **Scheduled tasks** handle maintenance, monitoring, and proactive work
- **The local filesystem** (via Box Drive) gives Claude Desktop faster access and capabilities connectors lack

Everything cross-references everything else. Skills reference files. Files reference other files and skills. Scheduled tasks maintain the filesystem. That interdependence is the substrate.

Without it, every Claude conversation starts from zero. With it, Claude has memory, context, instructions, and continuity.

---

## Why a substrate, rather than Claude's built-in features

A fair question comes up often enough to answer here: Claude has Projects, Claude has memory, Claude has Dispatch. Why all this extra scaffolding?

The honest answer is that Anthropic is moving in this direction, and over time some of what the substrate does will become native. Treat the substrate as filling real *current* gaps — not as a permanent need for everything it does today.

The main current gaps:

**Desktop–mobile parity.** Claude Cowork on desktop and the Claude mobile app don't interoperate cleanly. Dispatch exists, but it's fiddly — more a hack for techies than something that "just works" for most people. For anyone whose day spans both surfaces, this is a deal-breaker on its own. The substrate's file-based approach bridges it: the same files are visible from either surface, via Box.

**Memory the user can see and edit.** Claude Projects has a memory concept, but the memories it creates are hidden, not user-editable, and don't transfer between devices. With the substrate, the "memory" is a folder of plain-text files. The user can read it, correct it, extend it, and move it. If Claude gets something wrong, you can open the file in any text or markdown editor and fix it directly.

**Obsidian and similar tools.** Obsidian is popular among edge adopters for a reason — its graph view adds a discoverability layer worth having. Native integration isn't clean yet (the same desktop–mobile gap shows up there). When it matures, the substrate can absorb Obsidian-style front-matter and graph navigation without migration, because it's already just markdown files.

**Portability across AI providers.** Claude Projects is Claude's. The substrate's core — the files — is platform-agnostic. If the user ever wants to try Gemini, or run multiple assistants against the same knowledge base, only the skills need porting. The substance is preserved.

Further points, if the user probes:

**Team-shared substrates.** Box supports proper sharing and collaboration at folder level. Multiple humans can work against the same substrate with appropriate access scoping. Claude Projects is a single-user container tied to one surface.

**Inspectability.** When Claude behaves oddly, the user (or Claude) can open the files and see exactly what context is being read. Nothing is opaque. This matters for debugging, and for trust.

**Durability.** Markdown files survive tool changes, vendor changes, and company changes. If Box went away tomorrow, the substrate moves to another cloud drive in an afternoon.

### How to handle this in conversation

Don't volunteer this section unprompted. If the user asks "why not just use Claude Projects / memory / Dispatch?", or shows scepticism about the setup, acknowledge that there are real current reasons and offer to go into whichever one matters to them. Don't recite the whole list.

---

## Folders, Claude Projects, and scopes — three things people confuse

When people start using Claude seriously, they encounter three similar-sounding concepts. Getting the distinction straight early saves a lot of confusion later.

**A folder** is the classical thing — a directory on a filesystem (or in a cloud drive like Box) that holds files. The substrate lives in a folder. Scopes and context each live in folders. Nothing special.

**A Claude Project** is an Anthropic product feature in the Claude Desktop/web app. It's a container Anthropic created to group related conversations and give them shared instructions and uploaded files. Useful, but limited to that surface and not portable across devices or other tools.

**A scope** is a substrate concept. It's a user-defined area of active work or attention that has its own folder under `scopes/` and usually a paired skill named `scope-<scope-name>`. A scope is more flexible than a Claude Project and lives at the substrate level — available wherever the substrate is available (Desktop, mobile, scheduled tasks, any Claude surface).

The short version: a Claude Project is Anthropic's UI-level grouping. A scope is *your* substrate-level grouping. A folder is just a folder.

---

## Data tiers

The substrate organises data into three tiers. Understanding this helps you decide where things live and how to access them.

### Tier 1: Project files

The actual work product — source code, presentations, documents, assets. These live wherever makes sense for the project (GitHub, Google Drive, a local folder). Claude Desktop accesses them via the filesystem. They must be locally mounted, not accessed through connectors. If they're cloud-synced, mobile access comes via that sync service.

### Tier 2: Third-party tools

SaaS platforms the user works in — task managers, CRMs, email, wikis. Connected via MCP connectors. No local mounting. Interaction is limited to what each connector supports.

### Tier 3: The substrate core (this knowledge base)

The persistent brain. This Box knowledge base is tier 3. It holds instructions, memory, context, scope planning, databases, and ways of working. It is accessible from every Claude surface:

- **Box MCP connector** — universal read/write from any Claude instance (Desktop or mobile)
- **Box Drive** (local mount) — faster access on Desktop, plus delete/move/rename that the connector can't do
- **Scheduled tasks** — daily maintenance via the local filesystem

When filesystem access is available, prefer it. When it's not (mobile, or unmounted sessions), use the connector. The box-filesystem-management skill handles this decision.

---

## Directory structure

```
[root]/
  _meta/              # System infrastructure
  _trash/             # Soft-delete, 60-day recovery
  context/            # Background info and persistent context
    me/               # Personal
    work/             # Professional
    ways-of-working/  # Substrate conventions (this document lives here)
    [flexible]/       # Add whatever scopes fit (teams, clients, etc.)
  scopes/             # Active work areas — plans, decisions, drafts, notes
  scratch/            # Ephemeral work — drafts, experiments, temp files
  databases/          # Claude-managed structured data
```

### Folder purposes

**`_meta/`** — Infrastructure that supports the substrate. Cleanup scripts, schema files for databases, configuration. Not content — plumbing.

**`_trash/`** — Where deleted files go. Mirrors the source directory hierarchy so recovery is obvious (the path inside `_trash/` tells you where the file came from). Files are permanently deleted after 60 days by the cleanup task. To recover a file, move it back to its original location.

**`context/`** — Persistent background information. Things Claude should know across sessions. Standing facts, identity, relationships, preferences. `me/` and `work/` are starting points — add whatever scoping makes sense. A team context folder, a client-specific context folder, anything. The structure is flexible; the convention is that context is *about* the person or group, read to orient, and changes slowly.

**`scopes/`** — Active work areas. Each scope gets a subfolder with whatever structure the work needs: planning, decisions, notes, drafts, ongoing thinking. One scope might be a client engagement, another a product initiative, another a personal domain like "health". The actual deliverables (code, designs) live in Tier 1 locations and are referenced from here. See the scopes section below for more.

**`scratch/`** — Working space. Anything ephemeral, casual, or in-progress that doesn't yet have a home. Skill drafts, document drafts, temporary analysis, experiments. The key rule: nothing casual goes in the root folder. If it's not structural, it goes in `scratch/`.

**`databases/`** — When the user asks Claude to manage structured data (contacts, a pipeline, meeting logs, reminders, inbox captures, whatever) without a dedicated SaaS tool, the data lives here. Each database gets its own subfolder. Internal structure is Claude's responsibility — the user interacts with the data through conversation, not by browsing files. Schema files (describing the database structure) should live in `_meta/` so they're discoverable independently of the data itself.

The `reminders` and `inbox` skills (if installed) each own a subfolder here: `databases/reminders/` and `databases/inbox/`. Other databases follow the same pattern — a dedicated subfolder, a README, and whatever data files the owning skill manages.

### The root folder rule

The root level of the knowledge base is structural only. Every entry at root level is one of the defined folders above. Do not create files or folders at root level casually. If the user asks you to save something and it doesn't clearly belong in an existing folder, put it in `scratch/` and discuss proper placement later.

---

## Scopes: what they are and how they work

A scope is a user-defined area of active work or attention. It's the substrate's flexible, portable equivalent to a Claude Project — but living at the substrate level rather than inside a single product surface.

### What makes something a scope

Scopes are for areas where *work is being done* — there are decisions being made, notes being kept, drafts in progress, ongoing thinking that benefits from continuity. Not every topic needs a scope. Identity-level information (who the user is, who their people are, standing preferences) lives in `context/` instead. See the next section for the distinction.

Common things that become scopes:
- Client engagements or deals
- Product initiatives or launches
- Teams the user belongs to or leads
- Research threads or domains of interest
- Recurring events (conferences, programmes)
- Major life projects (house build, career transition)

### Scope folders

Each scope has a dedicated folder under `scopes/`. Internal structure is up to the user and the work. Some scopes need multiple subfolders; some just need a README and a few notes. The substrate doesn't prescribe a shape — it prescribes discoverability.

Every scope folder must have a `README.md` with Purpose, Contents, and Dependencies sections (same convention as everywhere else in the substrate).

### Scope skills

Each scope is paired with a skill named `scope-<scope-name>`. The skill's job is discoverability: when the user mentions the scope (or the conversation drifts into its territory), the skill triggers, and Claude learns that there's a folder with relevant context and how to find it.

The skill itself is short. It names the scope, describes what it's for, and points Claude at the scope folder. The substance of the scope lives in the folder, not the skill.

This pairing is the convention. A scope without a skill risks being invisible to Claude. A scope skill without a folder doesn't make sense (the skill would have nowhere to point). One scope, one folder, one skill.

Users should understand: a scope is the *area of work* (flexible, can hold anything), and the scope skill is the *anchor* that makes it discoverable. The skill is not the scope. The folder is not the scope. The scope is the user's mental model area — the folder and skill together serve it.

---

## Scope vs context — the distinction

This one trips people up, so it's worth making explicit.

**Context is *about* things. Scopes are *where things happen*.**

Context answers "who/what is this?" Scopes answer "what am I doing here?"

Context is identity-level, standing information — who the user is, who their people are, their preferences, facts about their company or team that don't change often. Read-often-write-rarely. You read context to *orient*.

Scopes are active working material — plans, decisions-in-progress, drafts, call notes, thinking. Read-often-write-often during live work, then quieter when the work is done. You read a scope to *pick up work*.

### Example: same entity, two different reasons to write about it

An imaginary company, Acme:

- `context/work/acme.md` — who Acme is, the relationship, their business, standing facts about them. Rarely changes.
- `scopes/acme-deal/` — the active sales cycle with Acme: call notes, proposal drafts, decisions, follow-ups. Lives and dies with the deal.

Both can coexist. They're not duplicates — they serve different purposes. If the deal closes, the scope might archive while the context endures. If the company gets acquired, the context changes while the (now-historical) scope stays as a record.

### Fuzzy-zone test

If you'd read it to *orient yourself*, it's context. If you'd read it to *pick up the work*, it's a scope.

### When something could go either way

If a topic is mostly standing facts with occasional active work, put it in context and use `scratch/` for the rare bits of active thinking. If it becomes ongoing, promote it to a scope.

If a topic starts as active work, put it in a scope. If standing facts accumulate that are useful across other scopes too, extract them to context and reference from the scope.

---

## Discoverability

There is no central index. The substrate is self-organising.

### README convention

Every folder must have a `README.md` with three sections in this order:

1. **Purpose** — one or two sentences on what this folder is for
2. **Contents** — an overview of what's inside (or what kinds of things go here)
3. **Dependencies** — a list of other folders or files in the substrate that are related or required

Keep it short. Plain language. No clever formatting. The Purpose and Contents sections can be a sentence each if that's all the folder needs.

This is how Claude discovers relevant context. When working in a scope folder, read its README. The Dependencies section tells you what else to load. Follow the chain.

### When to read READMEs

- At the start of a session, read the README of whatever folder the user is working in
- Before creating content, read the README of the target folder to understand conventions
- When the user references something that might exist elsewhere, check READMEs for cross-links

### Maintaining READMEs

When you create a new folder, create a README immediately. When you add content that creates a new dependency (e.g. a scope that relies on team context), update the READMEs on both sides of the link.

Keep READMEs simple. No complex formatting. Plain language a non-technical person could read and understand.

---

## Access modes

### Filesystem (preferred on Desktop)

When the knowledge base is mounted in a Cowork session, use filesystem tools directly. This is faster and supports all operations including delete, move, and rename. Box Drive syncs changes automatically.

### Box MCP connector (universal)

When filesystem access isn't available (mobile, unmounted sessions), use the Box connector. Limitations:
- No delete — use the `_DELETED_` prefix convention (see box-filesystem-management skill)
- No move — copy to destination, mark original as deleted
- Folders are identified by numeric ID, not path — store frequently used IDs in `_meta/folder-ids.md`

The box-filesystem-management skill has full details on workarounds and conventions for both modes.

---

## Naming conventions

- Lowercase, hyphen-separated: `meeting-notes-2026-04-15.md`
- Date-prefix for time-sensitive files: `YYYY-MM-DD-filename`
- No spaces in filenames
- Underscore-prefixed folders for system use: `_meta/`, `_trash/`
- Deleted files (pending cleanup): `_DELETED_YYYY-MM-DD_original-filename`
- Scope skills: `scope-<scope-name>` (e.g. `scope-acme-deal`)

---

## Access scoping: personal, work, team, shared

The substrate supports multiple access scopes. The structure keeps them separable:

- **Personal** — `context/me/`, personal scope folders
- **Professional** — `context/work/`, work scope folders
- **Team/shared** — additional context folders (e.g. `context/team-x/`), shared scope folders

Box supports shared folders (collaborations) anywhere in the tree. A shared scope folder can live inside `scopes/` alongside private ones. Team context can live under `context/`. No forced top-level separation.

The key principle: access scope is determined by where things live and who has access, not by a rigid hierarchy. The structure accommodates whatever the user's situation requires.

(Terminology note: "access scope" here refers to access/visibility boundaries. The substrate `scopes/` folder uses "scope" in a different sense — areas of work. Both uses of "scope" are natural English; this is the one place they overlap.)

---

## Extending the substrate

The substrate is designed to grow. Here are things it can support that may not be set up yet:

**Custom databases** — Ask Claude to manage structured data (contacts, CRM, task lists, anything). It creates and maintains the data in `databases/`. The user interacts through conversation.

**Custom skills** — Draft skills in `scratch/`, test them, then install as proper skills. Skills can encode any repeated workflow, convention, or way of working.

**Skill versioning** — Teams can store shared skills in a context folder (e.g. `context/team-x/skills/`) with version numbers. A scheduled task can compare installed versions against the latest and notify when updates are available.

**Daily briefings** — A scheduled task that gathers updates from across the substrate and presents a summary. Can be per-user or per-team.

**Inter-agent communication** — Agents for different team members can exchange information via email, Slack, or messages within the substrate. The pattern is defined by the team's way of working; the implementation medium is flexible.

These are all built using the same building blocks: files, skills, connectors, and scheduled tasks. The substrate doesn't need to be extended by a specialist — the user and their Claude can build these features using the conventions documented here.

---

## Substrate hygiene: what not to put here

Box encrypts data in transit and at rest, but it's still cloud storage and the substrate is where Claude reads and writes routinely. A few things don't belong:

- **Credentials, API keys, passwords, access tokens.** Use a password manager. If an operation needs a secret, keep it in the secret store and pass it in at the moment of use.
- **Government identifiers and financial account details.** SSNs, driver's licence numbers, passport numbers, full credit card numbers, bank account numbers.
- **Raw health and medical records.** Diagnoses, test results, therapy notes. Summaries and context are fine — the raw files belong in a purpose-built system.
- **Other people's private information without consent.** Especially anything that would embarrass or harm them if the substrate leaked.

Context, summaries, preferences, decision history, anonymised references — all fine. The line is roughly: "would it matter if this appeared in a breach?"

---

## Evolving this document

This guide is a starting point. The user and their team should modify it as their way of working develops. When making changes:

1. Update the version number at the top
2. Append a changelog entry at the bottom with date, new version, and a one-line summary of what changed and why
3. If the change affects other folders or skills, update their READMEs and dependencies too

### Changelog rule (applies to any versioned file in the substrate)

Any file that carries a `version:` line also carries a `## Changelog` section at the bottom. When you bump the version, append an entry to the changelog on the same edit:

```
- YYYY-MM-DD v[N]: one-line summary of what changed and why.
```

Newest entries at the top of the Changelog section. Append-only. Don't rewrite history.

---

## Changelog

- 2026-04-20 v4: Added "Why a substrate, rather than Claude's built-in features" section — covers desktop–mobile parity, editable memory, Obsidian, provider portability, team sharing, inspectability, and durability. Available for Claude to draw on when users ask why the substrate exists alongside Claude's native features.
- 2026-04-20 v3: Renamed `projects/` to `scopes/` to avoid confusion with Anthropic's Claude Projects feature. Added scopes-vs-context section. Added scopes-and-scope-skills section (one-to-one folder/skill pairing). Added "folders, Claude Projects, and scopes" explainer. Added scope skill to naming conventions.
- 2026-04-20 v2: Added substrate hygiene section (what not to put in the substrate). Added changelog rule and applied it here. Tightened README convention to a three-section stub (Purpose / Contents / Dependencies). Mentioned reminders and inbox as example databases.
- 2026-04-15 v1: Initial version.
