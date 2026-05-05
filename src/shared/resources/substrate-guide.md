# Substrate Guide

version: 5

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

**Desktop–mobile parity.** Claude on desktop and the Claude mobile app don't interoperate cleanly. For anyone whose day spans both surfaces, this is a deal-breaker on its own. The substrate's file-based approach bridges it: the same files are visible from either surface.

**Memory the user can see and edit.** Claude Projects has a memory concept, but the memories it creates are hidden, not user-editable, and don't transfer between devices. With the substrate, the "memory" is a folder of plain-text files. The user can read it, correct it, extend it, and move it. If Claude gets something wrong, you can open the file in any text or markdown editor and fix it directly.

**Portability across AI providers.** The substrate's core — the files — is platform-agnostic. If the user ever wants to try another assistant, or run multiple assistants against the same knowledge base, only the skills need porting. The substance is preserved.

**Team-shared substrates.** Multiple humans can work against the same substrate with appropriate access scoping. Claude Projects is a single-user container tied to one surface.

**Inspectability.** When Claude behaves oddly, the user (or Claude) can open the files and see exactly what context is being read. Nothing is opaque.

**Durability.** Markdown files survive tool changes, vendor changes, and company changes.

### How to handle this in conversation

Don't volunteer this section unprompted. If the user asks "why not just use Claude Projects / memory?" or shows scepticism about the setup, acknowledge that there are real current reasons and offer to go into whichever one matters to them.

---

## Folders, Claude Projects, and scopes — three things people confuse

**A folder** is the classical thing — a directory on a filesystem or cloud drive that holds files.

**A Claude Project** is an Anthropic product feature in the Claude desktop/web app. It's a container to group related conversations and give them shared instructions and uploaded files. Useful, but limited to that surface.

**A scope** is a substrate concept. It's a user-defined area of active work or attention that has its own folder under `scopes/` and usually a paired skill named `scope-<scope-name>`. A scope is more flexible than a Claude Project and lives at the substrate level — available wherever the substrate is available.

The short version: a Claude Project is Anthropic's UI-level grouping. A scope is *your* substrate-level grouping. A folder is just a folder.

---

## The two-layer model

The substrate is conceptually two layers. Understanding this boundary is important for deciding what gets stored versus what Claude reads.

### Layer 1 — Substrate proper (file-based, versioned)

Holds: skills, templates, context docs (brand voice, policies, conventions), structured non-PII data, configuration, sanitised test fixtures. Versioned, auditable, shareable, evolves slowly.

This is what the substrate guide describes. Everything in the directory structure below lives here.

### Layer 2 — PII layer (access-controlled store)

Holds: anything containing identifiable PII — customer profiles, per-customer working memory, drafting feedback. Implementation is typically an access-controlled database accessed via a guarded connector. Skills in Layer 1 talk to Layer 2 through the connector.

**Why the split:** PII in versioned shared substrate is durable, replicable, escapable — wrong threat model. PII at runtime is unavoidable (Claude has to read emails to do its job; emails contain PII). The substrate's job is *persistence*; the boundary is what gets *stored*, not what Claude *sees*.

For solo installs, there is typically no PII layer. The split is most relevant in team contexts where substrate files are shared and version-controlled.

The PII layer connector, schema, and access-control model are resolved by the wrapping plugin or the installing Claude — not prescribed by the substrate guide itself. See `cross-cut-extension-and-wrapping.md` for the wrapping principle.

---

## Data tiers

The substrate organises data into three tiers.

### Tier 1: Project files

The actual work product — source code, presentations, documents, assets. These live wherever makes sense for the project. Claude Desktop accesses them via the filesystem. They must be locally mounted.

### Tier 2: Third-party tools

SaaS platforms the user works in — task managers, CRMs, email, wikis. Connected via MCP connectors. No local mounting.

### Tier 3: The substrate core (this knowledge base)

The persistent brain. This knowledge base is tier 3. It holds instructions, memory, context, scope planning, databases, and ways of working. It is accessible from every Claude surface via connector and/or local filesystem access.

---

## Directory structure

### Personal-default (solo, or the personal layer in a team setup)

```
[root]/
  CLAUDE.md             # guard file — read this first
  _meta/                # system infrastructure
  _trash/               # soft-delete (60-day recovery)
  context/              # personal/default context (read to orient)
  databases/            # personal/default structured data
  scratch/              # ephemeral — TOP-LEVEL ONLY
  scopes/               # ALL scopes — TOP-LEVEL ONLY
```

This top-level layout is unchanged from v4. Solo users work entirely within this shape.

### Extended layout (when the user is in one or more orgs or teams)

The `orgs/` and `teams/` folders appear as siblings alongside the personal-default folders. They are only created when the user is actually in one or more orgs or teams.

```
[root]/
  CLAUDE.md
  _meta/
  _trash/
  context/
  databases/
  scratch/
  scopes/
    <scope-name>/
      context/          # HARD convention
      planning/         # soft
      generated/        # soft
      databases/        # soft
      README.md         # YAML front-matter linking to org/team
  orgs/                 # one entry per org (omit if user is in no orgs)
    <org-name>/
      context/          # HARD convention
      databases/        # soft
      README.md
  teams/                # one entry per team (omit if user is on no teams)
    <team-name>/
      context/          # HARD convention
      databases/        # soft
      README.md         # YAML front-matter: parent_org
```

Multiple orgs and multiple teams are both supported. Add entries under `orgs/` and `teams/` as needed — the structure accommodates any combination without further adaptation.

### Convention rules

**HARD conventions** (always create when the parent folder exists):
- `context/` inside `orgs/<org>/`
- `context/` inside `teams/<team>/`
- `context/` inside `scopes/<scope>/`

**Soft conventions** (create when needed):
- `planning/`, `generated/`, `databases/` inside scope folders
- `databases/` inside org and team folders

**Top-level only** (do not create these nested):
- `scratch/` — stops Claude dumping ephemeral content into sub-folders
- `scopes/` — all scopes live here regardless of ownership

**Scope ownership via front-matter, not folder hierarchy.** A scope's `README.md` carries YAML front-matter such as `team: <team-name>` and `org: <org-name>`. A team's `README.md` carries `parent_org: <org-name>`. To find "scopes for team X", Claude searches `scopes/` filtered by `team: X` in front-matter. No hierarchy traversal. Org/team membership can change without moving files.

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

## Folder purposes

**`_meta/`** — Infrastructure that supports the substrate. Cleanup scripts, schema files for databases, configuration. Not content — plumbing.

**`_trash/`** — Where deleted files go. Mirrors the source directory hierarchy so recovery is obvious. Files are permanently deleted after 60 days by the cleanup task.

**`context/`** — Persistent background information. Things Claude should know across sessions. Standing facts, identity, relationships, preferences. The convention is that context is *about* the person or group, read to orient, and changes slowly.

**`scopes/`** — All active work areas, regardless of ownership. Each scope gets a subfolder with a `context/` folder (hard convention) plus whatever structure the work needs. The actual deliverables (code, designs) live in Tier 1 locations and are referenced from here.

**`scratch/`** — Working space. Anything ephemeral, casual, or in-progress that doesn't yet have a home. The key rule: nothing casual goes in the root folder. If it's not structural, it goes in `scratch/`.

**`databases/`** — When the user asks Claude to manage structured data without a dedicated SaaS tool, the data lives here. Each database gets its own subfolder. Schema files should live in `_meta/`.

**`orgs/<org-name>/`** — Org-wide context and data. The `context/` subfolder (hard convention) holds brand voice, org-wide policies, conventions that apply across all teams in the org.

**`teams/<team-name>/`** — Team-wide context and data. The `context/` subfolder (hard convention) holds the team's CRM taxonomy, working conventions, shared reference material. The `README.md` carries `parent_org:` front-matter linking to `orgs/`.

### The root folder rule

The root level of the knowledge base is structural only. Every entry at root level is one of the defined folders above (or `CLAUDE.md`). Do not create files or folders at root level casually. If the user asks you to save something and it doesn't clearly belong in an existing folder, put it in `scratch/` and discuss proper placement later.

---

## Scopes: what they are and how they work

A scope is a user-defined area of active work or attention. It's the substrate's flexible equivalent to a Claude Project, living at the substrate level and available wherever the substrate is available.

### What makes something a scope

Scopes are for areas where *work is being done* — decisions being made, notes being kept, drafts in progress, ongoing thinking that benefits from continuity. Not every topic needs a scope. Identity-level information lives in `context/` instead.

Common things that become scopes:
- Client engagements or deals
- Product initiatives or launches
- Teams the user belongs to or leads
- Research threads or domains of interest
- Recurring events (conferences, programmes)
- Major life projects (house build, career transition)

### Scope folders

Each scope has a dedicated folder under `scopes/`. The `context/` subfolder is required (hard convention). Internal structure beyond that is up to the user and the work.

Every scope folder must have a `README.md` with Purpose, Contents, and Dependencies sections.

For scopes tied to an org or team, the `README.md` carries YAML front-matter:

```yaml
---
team: <team-name>
org: <org-name>
---
```

Include only the fields that apply. A personal scope carries no team or org front-matter.

### Scope skills

Each scope is paired with a skill named `scope-<scope-name>`. The skill's job is discoverability: when the user mentions the scope, the skill triggers and Claude learns there's a folder with relevant context and how to find it.

One scope, one folder, one skill. A scope without a skill risks being invisible to Claude. A scope skill without a folder doesn't make sense.

---

## Scope vs context — the distinction

**Context is *about* things. Scopes are *where things happen*.**

Context answers "who/what is this?" Scopes answer "what am I doing here?"

Context is identity-level, standing information — read-often-write-rarely. You read context to *orient*.

Scopes are active working material — plans, decisions-in-progress, drafts, call notes. You read a scope to *pick up work*.

### Fuzzy-zone test

If you'd read it to *orient yourself*, it's context. If you'd read it to *pick up the work*, it's a scope.

### Example: same entity, two different reasons to write about it

An imaginary company, Acme:

- `context/work/acme.md` — who Acme is, the relationship, their business, standing facts. Rarely changes.
- `scopes/acme-deal/` — the active sales cycle: call notes, proposal drafts, decisions, follow-ups.

Both can coexist. They serve different purposes.

---

## Discoverability

There is no central index. The substrate is self-organising.

### README convention

Every folder must have a `README.md` with three sections in this order:

1. **Purpose** — one or two sentences on what this folder is for
2. **Contents** — an overview of what's inside
3. **Dependencies** — a list of other folders or files in the substrate that are related or required

Keep it short. Plain language. No clever formatting.

This is how Claude discovers relevant context. When working in a scope folder, read its README. The Dependencies section tells you what else to load. Follow the chain.

### When to read READMEs

- At the start of a session, read the README of whatever folder the user is working in
- Before creating content, read the README of the target folder to understand conventions
- When the user references something that might exist elsewhere, check READMEs for cross-links

### Maintaining READMEs

When you create a new folder, create a README immediately. When you add content that creates a new dependency, update the READMEs on both sides of the link.

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

The specific permission lookup — which git provider, which API, which identity integration — is resolved by the wrapping plugin or the installing Claude. See `cross-cut-extension-and-wrapping.md`.

### Lightweight sync

For team substrates, sync defaults to a script that checks the remote HEAD commit hash against local. Claude wakes only when there is an actual delta. Tokens are consumed only when needed.

---

## Access modes

### Filesystem (preferred on desktop)

When the knowledge base is mounted in a session, use filesystem tools directly. This is faster and supports all operations including delete, move, and rename.

### Connector (universal)

When filesystem access isn't available (mobile, unmounted sessions), use the connector. Limitations:
- No delete — use the `_DELETED_` prefix convention (see box-filesystem-management skill if installed)
- No move — copy to destination, mark original as deleted
- Folders are identified by numeric ID, not path — store frequently used IDs in `_meta/folder-ids.md`

---

## Naming conventions

- Lowercase, hyphen-separated: `meeting-notes-2026-04-15.md`
- Date-prefix for time-sensitive files: `YYYY-MM-DD-filename`
- No spaces in filenames
- Underscore-prefixed folders for system use: `_meta/`, `_trash/`
- Deleted files (pending cleanup): `_DELETED_YYYY-MM-DD_original-filename`
- Scope skills: `scope-<scope-name>` (e.g. `scope-acme-deal`)

---

## Substrate hygiene: what not to put here

The substrate is shareable and may be version-controlled. A few things don't belong:

- **Credentials, API keys, passwords, access tokens.** Use a password manager or a dedicated secrets store.
- **Government identifiers and financial account details.** SSNs, passport numbers, full credit card numbers, bank account numbers.
- **Raw health and medical records.** Diagnoses, test results, therapy notes. Summaries and context are fine — the raw files belong in a purpose-built system.
- **Customer or contact PII.** Names, emails, and contact details for people other than yourself belong in the PII layer (Layer 2), not in the shareable substrate. See the two-layer model section above.
- **Other people's private information without consent.**

Context, summaries, preferences, decision history, anonymised references — all fine. The line is: would it matter if this appeared in a breach?

---

## Universal naming in this guide

This guide does not name specific git providers, specific cloud drives, or specific tools. The substrate conventions are universal; clients and installs vary. The wrapping plugin or the installing Claude resolves provider-specific decisions. See `cross-cut-extension-and-wrapping.md`.

---

## Extending the substrate

The substrate is designed to grow.

**Custom databases** — Ask Claude to manage structured data (contacts, CRM, task lists, anything). It creates and maintains the data in `databases/`. The user interacts through conversation.

**Custom skills** — Draft skills in `scratch/`, test them, then install as proper skills. Skills can encode any repeated workflow, convention, or way of working.

**Skill versioning** — Teams can store shared skills in a context folder with version numbers. A scheduled task can compare installed versions against the latest and notify when updates are available.

**Daily briefings** — A scheduled task that gathers updates from across the substrate and presents a summary.

**Inter-agent communication** — Agents for different team members can exchange information via the available connectors. The pattern is defined by the team's way of working.

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

- 2026-05-02 v5: Revised for v0.2.0. Added two-layer model (substrate proper vs PII layer). Added CLAUDE.md guard file at substrate root. Introduced top-level `orgs/` and `teams/` folders for multi-org and multi-team support (personal-default layout unchanged for solo users). Moved all scopes to top-level `scopes/` with YAML front-matter for ownership cross-linking. Documented HARD vs soft folder conventions. Added permission-aware substrate skill section with non-techie verb vocabulary. Added universal naming principle and wrapping reference. Updated hygiene rules to include customer PII in the two-layer boundary.
- 2026-04-20 v4: Added "Why a substrate, rather than Claude's built-in features" section — covers desktop–mobile parity, editable memory, Obsidian, provider portability, team sharing, inspectability, and durability. Available for Claude to draw on when users ask why the substrate exists alongside Claude's native features.
- 2026-04-20 v3: Renamed `projects/` to `scopes/` to avoid confusion with Anthropic's Claude Projects feature. Added scopes-vs-context section. Added scopes-and-scope-skills section (one-to-one folder/skill pairing). Added "folders, Claude Projects, and scopes" explainer. Added scope skill to naming conventions.
- 2026-04-20 v2: Added substrate hygiene section (what not to put in the substrate). Added changelog rule and applied it here. Tightened README convention to a three-section stub (Purpose / Contents / Dependencies). Mentioned reminders and inbox as example databases.
- 2026-04-15 v1: Initial version.
