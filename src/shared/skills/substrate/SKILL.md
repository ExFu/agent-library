---
name: substrate
description: Core substrate skill. Bootstraps any Claude session with awareness of the user's substrate — the persistent system of files, skills, connectors, and scheduled tasks that lets Claude have memory and context across sessions. Loads the ways-of-working guide, orients to the directory structure, pulls in relevant scope context, and surfaces anything due from reminders or inbox. Should load at the start of every substrate-aware conversation. Triggers on "substrate", "load my substrate", "check my setup", on fresh sessions, or when the personal `wow` skill delegates to it.
---

# Substrate skill

This skill connects you to the user's substrate — the persistent files, skills, connectors, and scheduled tasks that carry continuity across their Claude conversations. Without it, a fresh Claude session has no memory of who the user is, what they're working on, or how they work. With it, Claude can pick up where things left off.

This skill is generic — the same across all ExFu clients. The user's *personal* way of working lives in a separate skill called `wow`, which loads this skill first and then layers their specifics on top.

---

## What to do when this skill loads

### 1. Find the substrate

The substrate core lives in a Box knowledge base. Check whether the Box folder is mounted in this session (filesystem access available) or whether you need to use the Box MCP connector.

If you're not sure where the knowledge base is, check the Global Instructions — the path should be noted there. If it's not, ask the user.

### 2. Read the ways-of-working guide

Read `context/ways-of-working/substrate-guide.md` from the knowledge base. This is the durable reference — directory layout, conventions, access modes, naming rules, how to find things, and (critically) the difference between scopes and context.

If the file doesn't exist yet, the substrate may not be fully set up. Tell the user. A copy of the substrate guide is also available in the plugin resources at `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` — you can read it from there to orient the user on what to set up.

### 3. Read the current folder's README

If the conversation is happening inside a specific scope or context folder, read its README.md. Pay attention to the **Dependencies** section — it tells you what other parts of the substrate are relevant. Follow the chain: if a scope README points to team context, read that too.

### 4. Check reminders and inbox

If the `reminders` skill is installed, delegate to it: read the reminders file, surface anything due or overdue. If nothing is due, say nothing.

If the `inbox` skill is installed, delegate to it: check the count. If there are items, mention briefly ("Inbox has [n] items"). Don't force processing.

These checks are fast and quiet. Session start is not a ceremony.

### 5. Orient and proceed

You should now understand how the substrate is structured, what the user's conventions are, what context is relevant to the current conversation, and what (if anything) needs their attention.

If the user hasn't asked for anything specific yet, briefly confirm what you've loaded and ask what they'd like to work on.

---

## Core concepts (durable — every Claude should know these)

The substrate guide has the full reference. These are the concepts that come up most often and need to be internalised here so they're available even when the guide hasn't been loaded yet in a given conversation.

### Substrate

The combination of files, skills, connectors, and scheduled tasks that together give Claude persistent memory and context across sessions and devices. No single component is the substrate — it's the interplay. Files store information. Skills encode behaviour and conventions. Connectors make files and tools accessible from any Claude surface. Scheduled tasks run in the background for maintenance and proactive work.

### Skill

A named bundle of instructions and conventions that Claude loads on demand. Skills are how the user encodes their way of working so it survives across conversations. Every skill has a name, a description (which controls when it triggers), and a body of guidance. The description is what Claude matches against to decide whether to load the skill — so descriptions matter.

### Scope

A user-defined area of active work or attention. A scope is *where things happen* — plans, decisions-in-progress, drafts, working notes. It's project-like but not constrained to the Claude Desktop "Projects" feature. Each scope has a dedicated folder under `scopes/` and usually a paired skill named `scope-<scope-name>` that serves as its discoverability anchor.

A scope is flexible. It can be a client engagement, a product initiative, a team, a role, a domain of interest, a recurring event. The user decides. The one-to-one pairing of scope folder + scope skill is the convention; the internal structure of a scope is up to the user and what the work requires.

### Context

Persistent background information that describes the user, their people, their world, and their standing facts. It's read-often-write-rarely. Identity-level material. `context/` holds this.

### Scope vs context — the distinction

Context is *about* things. Scopes are *where things happen*.

Context answers "who/what is this?" Scopes answer "what am I doing here?"

Example: a company called Acme might appear in both. `context/work/acme.md` holds who Acme is, the relationship, standing facts. `scopes/acme-deal/` holds the active sales cycle — call notes, proposal drafts, decisions, follow-ups. Same entity, two different reasons to write about it. If either is missing, the substrate still functions — but they're not the same thing.

Fuzzy-zone test: if you'd read it to *orient*, it's context. If you'd read it to *pick up work*, it's a scope.

### Data tiers

- **Tier 1 — project files**: source code, documents, designs. Live wherever makes sense (GitHub, Google Drive, local folders). Referenced from the substrate but not stored in it.
- **Tier 2 — third-party tools**: SaaS platforms (task managers, CRMs, email, wikis). Accessed via MCP connectors.
- **Tier 3 — substrate core**: this Box knowledge base. Holds context, scopes, databases, instructions, ways of working.

### Access modes

When filesystem access is available (Cowork on Desktop with the knowledge base mounted), prefer it — faster, supports delete/move/rename. When it's not (mobile, unmounted sessions), use the Box MCP connector. The `box-filesystem-management` skill handles the details.

---

## Ongoing behaviour while loaded

- **Follow the substrate conventions** described in the ways-of-working guide (folder structure, naming, README maintenance, nothing casual in root).
- **Use the right access mode** — filesystem when mounted, Box connector when not.
- **Maintain discoverability** — if you create new folders or content, create/update READMEs with dependency links. If you create a new scope, set up or point to its scope skill.
- **Respect the scope/context distinction** when deciding where to save new material. When in doubt, ask, or put it in `scratch/` and flag it for later placement.
- **Don't assume context persists between sessions.** If you need information from the substrate, read it. Don't rely on memory or prior conversations — read the current state.
