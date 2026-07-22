---
name: exfu-guides
description: ExFu is a Claude setup tool that installs an Agent Library -- a persistent knowledge base kept organised by Agent Librarians, implemented as a scope-based substrate with folder-types, scheduled agents, and convention versioning. This skill answers questions about how that setup works. Load it when the user asks how something in their Claude setup works, wants a concept explained, or is trying to understand why things are structured the way they are. Triggers on "how does this all work?", "what is the Agent Library?", "what are librarians?", "what is the substrate?", "what is a scope?", "what are folder-types?", "how do librarians work?", "what is a scheduled agent?", "what is the convention base?", "what does store-or-point mean?", "what is wow?", "how does versioning work?", "what is the global index?", "how do I add a new scope?", "what is the user scope?", "what's the dashboard?", or any other question about the substrate's design or architecture.
---

# ExFu Guides -- reference for the v0.3 scope-based substrate

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

For convention base content (the canonical definitions agents follow):

- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/ontology.md` -- the complete core ontology in ONE file: the scope model and scope.md format, every folder-type (with anchors like `#todo`), scheduled agents and librarians, the way-of-working concept, and the authoring rules. This is the canonical source for nearly every structural question.
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/principles.md` -- the design principles and tool recommendations.
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/librarians/` -- the shipped librarian definitions (nightly-index, inbox-triage, dashboard-generator, version-cleanup).
- `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/skills/wow-template.md` -- the way-of-working template.

## The v0.3 concepts

These are the ten concepts the substrate is built on. Know them cold. When a question touches one, read the canonical source before answering -- don't rely on this summary alone.

### 1. Scopes

A scope is a bounded working context. Not an org chart entry -- a container for everything an agent needs to operate in one area of work. A scope could be a client, a project, a team, a department, or anything else the user treats as a distinct context.

Every scope has a `scope.md` with YAML frontmatter (`name`, `purpose`, `parent`, `exfu` version pin). Inside it, a scope can contain up to 10 standard folder-types. Scopes nest via a `scopes/` subdirectory -- a scope never holds child scopes loose among its own working folders.

The substrate has three zones at the top level: `exfu/` (plugin-owned definitions; not a scope -- no scope.md), `user/` (the personal scope, unversioned, parent: none), and `scopes/` (everything else). Everything under `scopes/` is either a real scope (has `scope.md`) or a grouping folder (no `scope.md`, purely organisational).

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/ontology.md` (Scope section)

### 2. Folder-types

The 10 standard folder-types are the vocabulary of "where things go" inside a scope:

| Folder | What it answers |
|---|---|
| `ontology/` | What do the concepts and terms in this scope mean? |
| `context/` | What background should an agent know? (including kept reference documents) |
| `skills/` | What skill definitions belong to this scope? |
| `librarians/` | What substrate maintenance runs here on a schedule? |
| `scheduled/` | What business-logic work runs here on a schedule? |
| `todo/` | How does this scope handle tasks? |
| `reminders/` | How does this scope handle lightweight nudges? |
| `inbox/` | Where do uncategorised thoughts go? |
| `databases/` | Where do structured, repeating records live? |
| `visualisations/` | Where do agent-created visual outputs live? |

The catalogue is open -- a scope can add its own types and define them in its `ontology/`. Folder-types materialise only when content exists for them: a scope with just scope.md and context/ is healthy, not incomplete. Each materialised folder-type has an `agent.md` whose `Follows:` line anchors into the core ontology (e.g. `Follows: exfu/v0.3/ontology.md#todo`) and lists only local deviations. Descriptors never carry state ("currently empty" is banned -- it goes stale).

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/ontology.md` (Folder-types section)

### 3. Convention base

The convention base lives at `exfu/v0.3/` inside the substrate. It contains the default definitions for all folder-types, the scope model docs, and the librarian definitions. It is the single canonical source for "how does this folder-type behave by default?"

Scopes reference the convention base via `Follows:` lines in their `agent.md` files, anchored into the single ontology file (`Follows: exfu/v0.3/ontology.md#context`). A standard folder with no deviations is tiny -- the protective header plus that one line. The convention base itself ships with the plugin at `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/` and gets installed into the user's substrate. It is deliberately flat and small (one ontology file, one principles file, shipped librarians, the wow template) so it can be ingested in a handful of reads.

### 4. Store-or-point

Every folder-type either stores data locally (markdown files in the folder) or points to an external tool. A `todo/` folder might contain task files, or its `agent.md` might say "tasks are in ClickUp -- use the ClickUp MCP connector." A `reminders/` folder might hold trigger rules, or it might say "reminders live in Apple Reminders."

Both are equally valid. The convention guarantees the location is discoverable -- an agent always knows where to ask about tasks, reminders, context, etc. for any scope. Whether the data lives there is per-scope, per-user.

This is visible in the global index: each folder-type shows as `data` (files here), `pointer` (data elsewhere), or `empty` (folder exists but nothing in it yet).

### 5. Scheduled agents (librarians and business agents)

Scheduled agents are recurring jobs defined as agent instructions: a markdown definition file an agent reads cold and carries out on a cadence, calling scripts as tools where the definition says to. Two kinds share identical mechanics and differ only in remit:

- **Librarians** maintain the substrate itself (sweep the inbox, regenerate the index, flag stale versions). Definitions live in `librarians/` folders.
- **Business agents** do the user's recurring domain work (scan listings, draft a weekly digest, watch a mailbox). Definitions live in `scheduled/` folders.

Cadences: nightly, weekly, hourly, or on-demand. The nightly index is the canonical librarian -- it walks the entire substrate and regenerates `exfu/derived/index.json`.

The registry at `exfu/derived/agent-registry.json` tracks all registered scheduled agents, their kind, cadence, last run times, and status. One scheduled task per cadence runs them: librarians first, then business agents, then dependency order. Each outcome is recorded to `exfu/derived/agent-log.json`. A definition that exists but isn't registered does nothing -- registration (via the install-scheduled-agent skill) is what makes it live.

ExFu ships four librarian definitions: nightly-index, inbox-triage, dashboard-generator, and version-cleanup.

Canonical source: `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/ontology.md` (Scheduled agents section), shipped definitions in `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/librarians/`

### 6. Versioning

Convention base versions sit side-by-side: `exfu/v0.3/`, `exfu/v0.6/`, etc. Each scope pins to a version via the `exfu:` field in its `scope.md`. New scopes default to whatever `exfu/latest.txt` points to (currently `v0.3`). Existing scopes keep their pin until explicitly migrated.

Migration is per-scope, not all-at-once. A substrate can have scopes on different versions simultaneously. The global index tracks which version each scope uses.

Special case: the `user/` scope has no `exfu:` field -- it always reads through `latest`.

### 7. The global index

`exfu/derived/index.json` -- generated nightly by the index librarian. One read gives the whole substrate map:

- Every scope, its tree position, and parent relationships
- Folder-type status per scope (data / pointer / empty)
- ExFu version pins per scope
- Which convention base versions are in use

The index serves two consumers: agents (fast orientation without walking the filesystem) and the dashboard (visual rendering). It is never hand-edited -- it's regenerated on every nightly run.

### 8. The user/ scope

The personal scope. Always exists at the substrate root alongside `exfu/` and `scopes/`. Contains about-me context, ways of working, personal preferences, and personal ontology that apply across every scope.

`user/` is not a working scope -- it's who the user is. It has no `exfu:` version pin (always reads through `latest`), no `parent` (it sits at the root), and its content travels with the user across every context.

### 9. The wow skill

The user's personal navigation map and thin always-on kernel. Generated during install by the `exfu-create-wow` skill, updated as the substrate evolves.

`wow` does two things: (1) maps out where the substrate is laid out so a new session can find everything without being told, and (2) carries a small set of universal instructions (communication preferences, formatting rules, always-on behaviours).

It's a living document. Small updates happen directly; substantial changes (new scopes, restructured folders) warrant a full regeneration via `exfu-create-wow`.

### 10. The dashboard

When available, a static HTML page at `exfu/derived/dashboard/` that renders the global index into a visual substrate map. Shows the scope tree, folder-type status, ontology chains, and librarian health. Read from the index, not by walking the filesystem live -- so it's fast and works offline.

Target audience is non-technical users. The dashboard is generated as part of the nightly index run or on-demand.

## How to handle common question types

**"What is the substrate?"**
Read the primer or the guide intro. Give a one-paragraph answer in plain language. Offer to go deeper on any part.

**"What is a scope?" / "How do I create one?"**
Summarise: a bounded working context with a predictable internal shape. Has `scope.md` with frontmatter, contains folder-types, nests via `scopes/`. The three top-level zones are `exfu/`, `user/`, and `scopes/`. Read the Scope section of `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/ontology.md` for the format spec. Creating one is the scope-setup skill's job.

**"What are folder-types?" / "What goes where?"**
The 10 standard types answer "how does this scope handle this kind of thing?" Walk through the table above. Emphasise that each is a discovery convention -- the data might live locally or in an external tool.

**"How does store-or-point work?"**
A folder either stores data or says where the data actually lives. Both are valid. The point is that an agent always knows where to ask. Use todo/ as the clearest example -- most users already have a task manager.

**"How do librarians work?" / "What's a scheduled agent?"**
Recurring jobs defined as agent instructions, run by one scheduled task per cadence. Librarians maintain the substrate; business agents do the user's standing domain work; same mechanics, different remits. The nightly index is the canonical librarian. Read the Scheduled agents section of the core ontology for depth.

**"What version am I on?" / "How does versioning work?"**
Scopes pin to a version. Versions sit side-by-side. `latest.txt` points to the newest. Migration is per-scope. Check the global index to see which versions are in use.

**"What is the global index?"**
One JSON file that maps the whole substrate. Generated nightly. Read it for fast orientation instead of walking the filesystem. Point at `exfu/derived/index.json`.

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
