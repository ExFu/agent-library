---
name: exfu-library
description: ExFu's Agent Library is the persistent system of files, skills, connectors, and scheduled agents that gives Claude memory and working context across sessions -- a library of who the user is, what they're working on, and how they operate, kept organised by their Agent Librarians. This skill bootstraps any session with that context -- it finds the library, reads the global index, resolves the conventions version, loads the user's personal context and ways of working, detects the storage backend, checks librarian health, and surfaces anything the overnight runs left. Load it at the start of any library-aware conversation, or when the user's personal wow skill delegates to it. Triggers on "do you know who I am?", "can you pull up the Acme deal?", "where is my stuff?", "what do I have on this week?", "what's in my notes on Y?", "check my library", "save this", "check for updates", or any other conversation where the user expects Claude to have standing context about them or their work.
---

# exfu-library skill -- the Agent Library boot sequence (v0.4.0)

Vocabulary note before anything else: with the user, this is "your library", kept in order by "your librarians". "Substrate" is the internal register this skill is written in -- the implementation vocabulary. The two registers are defined in `exfu/<version>/ontology.md#vocabulary`.

## Hard constraints

Read these before doing anything else. They apply for the entire session.

1. **Never write secrets into the substrate.** Before writing any file, check whether it contains keys, tokens, passwords, API keys, or credential material (.env, *.key, *.pem, credentials.json, id_rsa, id_ed25519). If it does, refuse with a plain explanation. Secrets never enter the substrate. Everything else -- names, contacts, org charts, CRM records, personal notes -- is just data and lives where it naturally belongs.

2. **Never fabricate scope membership.** Only surface scopes that actually exist in the substrate. If the index lists three scopes, there are three scopes. If scopes/ is empty, the user has no working scopes yet. Do not invent structure.

3. **Never overwrite the CLAUDE.md guard without confirmation.** If a `CLAUDE.md` already exists at the substrate root, do not modify or replace it without the user explicitly asking. It is a safety guard, not content.

4. **Never surface admin verbs without confirmed admin permissions.** Do not show `approve change`, `review`, or `reject` vocabulary unless the permission lookup (see below) returns `admin` or `maintainer`. When in doubt, default to member rights.

5. **Destructive operations require confirmation.** Deleting, overwriting, or moving scope-level structures requires explicit user confirmation. This includes removing scopes, deleting folder-type directories, or overwriting scope.md files.

6. **Never proceed without substrate access.** If the substrate folder can't be reached in this session (not mounted as a working folder, no connector available, file reads return nothing), halt and ask the user to add it as a working folder before continuing. Do not fall back to inference, do not guess at folder structure, do not work from "memory" of past sessions, do not invent a degraded workflow. The substrate is the source of truth; without it you have nothing to operate on, and any attempt to keep going is hallucination.

7. **Respect the convention base.** When creating new folders or content inside a scope, follow the conventions defined in the scope's pinned exfu version (found via the `exfu` field in scope.md or defaulting to latest). Read the relevant convention base files before acting -- do not assume you know the conventions from prior sessions.

---

## What to do when this skill loads

### Step 1 -- Find the substrate root and confirm access

The substrate core lives in a knowledge base folder. It must be readable in this session for the rest of the boot sequence to work. Two access modes:

- **Filesystem (preferred when available).** The substrate folder is added as a working folder. Direct reads/writes; supports delete, move, rename.
- **Connector (when filesystem isn't available).** Mobile sessions, unmounted contexts. The Dropbox connector supports full create/read/move/delete by path; slower than filesystem.

Check, in order:

1. Look at the Global Instructions for the substrate root path. The install conversation noted this there.
2. Try to read the substrate root. If filesystem is mounted as a working folder, direct access works. If it isn't, the relevant connector should be available.
3. If neither works, the substrate is not accessible from this session.

**If the substrate isn't accessible, halt and surface the working-folder picker.** Don't ask the user in text to add the folder; invoke `request_cowork_directory` directly so they can pick the right folder via the dialog.

Wrap the invocation with a brief plain-language note:

> "I can't reach your knowledge base from this session. Picking your folder now."

Then call `request_cowork_directory`. When it returns, retry Step 1 from the top with the new path. If the picker is dismissed without a selection, tell the user the skill can't continue without access and stop.

Do not continue past this step without confirmed access. Per Hard constraint #6: no inference, no guessing, no "I'll work from what I remember". The substrate has to be there for this skill to do its job.

### Step 2 -- Check for the CLAUDE.md guard

At the substrate root, check whether `CLAUDE.md` exists.

- If it exists, continue. It confirms you're in a substrate root.
- If it doesn't exist, you may be in an unguarded substrate (or this may be a first-time setup). See the CLAUDE.md guard section below for what to do.

### Step 3 -- Detect the storage backend

Infer the storage backend from the substrate's environment:

- A `.git/` directory at the substrate root means **git-backed**.
- The substrate root path inside a Dropbox folder (`~/Dropbox/...` or a `~/Library/CloudStorage/Dropbox...` style location) means **Dropbox-backed**.
- A path inside a Box mount (`~/Library/CloudStorage/Box-Box/...`) means a **legacy Box-backed** substrate from a pre-0.4 install: suggest the exfu-migrate-to-dropbox skill, and avoid destructive operations until migrated.
- Otherwise, default to **local** (no automated sync layer; the user manages propagation).

Note the backend for the rest of the session. It determines which verb vocabulary to surface and whether sync logic applies.

### Step 4 -- Read the user's wow skill for orientation

Check whether the user has a ways-of-working skill loaded in this session. The user's wow skill is typically named `<username>-wow` or `<username>` (e.g. `al-wow`, `al`). Look for any installed skill whose name matches this pattern. If one is loaded, it provides high-level orientation -- read it and let it shape how you interact for the rest of the session.

If no wow skill is loaded, continue. Not every user has set one up yet.

### Step 5 -- Read the global index

Read `exfu/derived/index.json` from the substrate root. This is the single source of truth for the substrate's structure -- one read gives you the whole picture:

- Every scope (name, path, parent chain, nesting)
- Folder-type status per scope (data-bearing, pointer-only, or empty)
- ExFu version pins per scope
- Which exfu versions are in use and which is latest

**If the index exists,** use it for all scope discovery and navigation. Do not walk the filesystem to find scopes when the index is available. The index is faster, more complete, and works even when the filesystem is slow (cloud drives with hydration delays, large substrates).

**If the index doesn't exist,** fall back to filesystem discovery:

1. List the top-level structure: `exfu/`, `user/`, `scopes/`.
2. Walk `scopes/` recursively, looking for directories that contain `scope.md`. Any directory with a `scope.md` is a scope; any without is a grouping folder.
3. Read each `scope.md` for name, parent, and exfu version pin.
4. Flag the missing index to the user -- suggest registering the nightly index librarian as a scheduled task so the index stays current.

### Step 6 -- Resolve the current exfu version

Read `exfu/latest.txt` from the substrate root. It contains the current convention version (e.g. `v0.3`). This tells you which convention base to reference when creating new content or interpreting scopes that don't specify a version.

The convention base lives at `exfu/<version>/` (e.g. `exfu/v0.3/`). It is deliberately flat and small:
- `ontology.md` -- the complete core ontology in one file: the scope model, every folder-type, scheduled agents and librarians, the way-of-working concept, and the authoring rules. One read gives you the whole vocabulary; `Follows:` references across the substrate point into it by anchor (e.g. `ontology.md#todo`).
- `principles.md` -- the design principles behind the conventions, plus tool recommendations.
- `librarians/` -- the ExFu-shipped librarian definitions, ready to register.
- `skills/` -- the ExFu-shipped skill sources, including the way-of-working template.

Scopes pin their version in scope.md's `exfu` field. A scope pinned to `v0.3` follows the conventions in `exfu/v0.3/`. The `user/` scope is unversioned and always follows latest.

### Step 7 -- Load the user's personal context

Read the `user/` scope. This is the user's personal workspace -- context and preferences that apply across everything they do.

Key files to read:
- `user/scope.md` -- the user's name and personal workspace purpose
- `user/context/about-me.md` -- who the user is, background, preferences
- `user/ontology/ways-of-working.md` -- how the user prefers to work, communication style, conventions they care about

Read these files if they exist. They shape how you interact for the rest of the session. If the files don't exist, the user scope may be minimal -- that's fine. Some users start lean.

### Step 8 -- Orient to the scope landscape

Using the index (or the filesystem fallback from Step 5), build a picture of what the user has:

- How many scopes exist and what they're called
- The nesting structure (which scopes are children of others)
- Which scopes have populated folder-types vs empty stubs
- Which exfu version each scope pins

Tell the user plainly what you found. Example: "You've got 3 working areas: Acme (with a Q3 Renewal sub-area), Side Project, and your personal space." Use the scope names, not paths. If scopes/ is empty, say so and move on.

**Don't overwhelm.** A brief summary is enough. The user knows what they have -- they're looking for confirmation that you do too.

### Step 9 -- Navigate into a specific scope (when relevant)

If the conversation context points to a specific scope (the user asked about it, or it's clear from context), navigate into it:

1. **Read scope.md** for purpose, parent, and version pin.
2. **Walk the parent chain.** If the scope has a parent, read that parent's scope.md too, and its parent, up to the root. This gives you the full context chain.
3. **Load relevant ontologies.** Read ontologies from: the active scope, each ancestor scope, `user/ontology/`, and the exfu base (`exfu/<version>/ontology.md`). Hold all definitions together. When definitions conflict, recognise both and ask the user if it matters in context.
4. **Read relevant agent.md files.** For folder-types the user needs in this conversation, read the agent.md. It will have a `Follows:` reference to the convention base -- read that upstream file too. Then apply any local deviations listed in the agent.md.

**Navigate via the index, not the filesystem.** The index gives you scope paths directly. Only touch the filesystem to read the actual content files.

### Step 10 -- Permissions and verb surfacing

What this step does depends on the storage backend detected in Step 3.

**Git-backed substrates.** Determine the user's permission level via a provider-specific lookup. The lookup is resolved by the wrapping plugin or at install time. Contract:

```
lookup(remoteUrl: string) -> "admin" | "maintainer" | "member" | "read-only"
```

Configured by the wrapper or stored during install. When no lookup is configured, default to `"member"` and surface a brief note that permission detection wasn't available.

Surface verbs based on the result:

| Permission level | Verbs to surface |
|---|---|
| `admin` or `maintainer` | save, share for review, check for updates, fix clashes, approve change, review, reject |
| `member` | save, share for review, check for updates, fix clashes |
| `read-only` | check for updates only (explain that writes require someone with write rights to act on their behalf) |

Do not mention git commands at any point. Users interact through the verbs above.

**When checking for updates (git only):** prefer a non-LLM approach first. Compare the local HEAD commit hash against the remote HEAD hash. Only invoke a full sync process when there is a confirmed delta. Tokens are consumed only when needed.

**Dropbox-backed substrates.** Dropbox's own sharing controls determine what files the user can read and write; no separate permission lookup is needed. Surface a backend-appropriate verb set: `save` (write the file; Dropbox syncs it), `check for updates` (rare; Dropbox auto-syncs), `share for review` (notify a colleague to look -- no built-in PR concept), `fix clashes` (Dropbox writes "conflicted copy" files when two edits collide -- find them, compare versions, reconcile with the user; revision history is available for recovery). The git-specific verbs (`approve change`, `review`, `reject`) do not apply.

**Local-only substrates.** The user has full rights to their local filesystem. No permission lookup, no fallback note. Verbs collapse to direct filesystem operations: `save` (write the file), `check for updates` (no remote to check; could mean "show me what changed since last session" if useful). Sharing-and-review verbs do not apply because there is no automated propagation layer; the user handles distribution manually.

### Step 11 -- Check scheduled-agent health

Read `exfu/derived/agent-registry.json` if it exists. This file tracks every registered scheduled agent (librarians and business agents):
- Which are registered and enabled, and of which kind
- Last run time and status for each
- Consecutive failure count

Surface any problems worth mentioning:
- **Consecutive failures > 0** -- something has been failing. Tell the user which one and what the last error was (check `exfu/derived/agent-log.json` for details if available).
- **Stale runs** -- if the last run was more than 48 hours ago for a nightly entry, something may be wrong with the scheduled task. Mention it.
- **No registry** -- if the file doesn't exist, the nightly cadence may not be set up yet. Suggest it if the substrate seems established (has multiple scopes, has been in use).

If everything is healthy, say nothing. Health is background monitoring, not ceremony.

### Step 12 -- Surface scheduled-agent attention items

Scheduled agents run agentically in their scheduled sessions, but some outcomes need the user: a decision the agent wouldn't make alone (deleting an unreferenced version), a triage summary worth a look, a business agent's finding, a failure that needs a human.

Check the most recent entries in `exfu/derived/agent-log.json` (latest entry per agent):
- Any `status: failure` -- mention which one and its detail line.
- Any detail line flagging something for the user (e.g. "v0.2 unreferenced; candidate for removal", "7 inbox items, 2 stale", "2 new sightings match the brief").

If there's something, surface it briefly: "Overnight runs left [n] things for you to look at." Don't force processing -- mention and move on.

If there's nothing, say nothing.

### Step 13 -- Check reminders and inbox

Check whether a reminders skill is loaded in this session. The user's reminders skill is typically named `<username>-reminders` (e.g. `al-reminders`). Look for any installed skill whose name ends in `-reminders`. If one is loaded, delegate to it: read the reminders, surface anything due or overdue. If nothing is due, say nothing.

Check whether an inbox skill is loaded. The user's inbox skill is typically named `<username>-inbox`. If one is loaded, delegate to it: check the count. If there are items, mention briefly ("Inbox has [n] items"). Don't force processing.

If neither type of skill is loaded, check the user scope directly:
- `user/reminders/` -- look for any reminder files with natural-language trigger rules that fire today
- `user/inbox/` -- count items if any exist

These checks are fast and quiet. Session start is not a ceremony.

### Step 14 -- Orient and proceed

You should now understand: the substrate's structure, which scopes exist and how they nest, what the user's personal context and preferences are, what permission level to operate at, whether any scheduled agents need attention, and what (if anything) needs the user's attention.

If the user hasn't asked for anything specific yet, briefly confirm what you've loaded and ask what they'd like to work on.

---

## CLAUDE.md guard creation

The substrate root must contain a `CLAUDE.md` file. Its purpose is to prevent Claude from treating the substrate as a generic working folder when loaded in a session without the exfu-library skill.

**When this skill is called by an install skill at substrate creation time:**

1. Check whether `CLAUDE.md` exists at the root.
2. If it does not exist, write it immediately with the canonical content below.
3. If it does exist, do not overwrite it. Only modify it if the user explicitly asks.

Canonical content (copy this exactly):

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

---

## Verb vocabulary (git-backed team substrates)

Users speak natural verbs to Claude in place of git terminology. Map each as follows:

| User says | What you do |
|---|---|
| save | Commit the change on the user's personal branch |
| share for review | Push the branch and open a pull request via the git provider API |
| check for updates | Check the remote HEAD hash; if there's a delta, pull from main |
| fix clashes | Walk the user through merge conflict resolution (guided, not technical) |
| approve change | Merge the pull request -- only if permission level is `admin` or `maintainer` |
| review | Surface the open pull request for the user to read and respond to |
| reject | Close the pull request without merging -- only if `admin` or `maintainer` |

Never expose git commands, branch names, or diff output directly to the user unless they ask. The above vocabulary is the interface.

**Lightweight sync before "check for updates":** before firing any sync process, compare local HEAD commit hash to remote HEAD commit hash using a non-LLM call. If they match, tell the user they're up to date -- no further work needed. If there's a delta, proceed with the pull.

---

## Data rules

Simple:

- **Only true secrets are banned.** Keys, tokens, passwords, API keys, credential files (.env, *.key, *.pem, credentials.json, id_rsa, id_ed25519) never enter the substrate. This is a hard constraint, enforced by agents and by git-sync ignore patterns.
- **Everything else is data.** Names, contacts, org charts, CRM records, personal notes, meeting minutes, preference profiles -- all of it lives wherever it naturally belongs in the scope structure. There is no separate PII layer, no two-layer boundary, no special PII machinery.
- **Destructive operations require confirmation.** Deleting, overwriting, or moving scope-level structures requires explicit user confirmation.

---

## The scope model

Everything in the substrate is organised around one concept: the **scope**. A scope is a bounded context with its own knowledge, definitions, and conventions. An org is a scope. A team is a scope. A personal space is a scope. A project is a scope. They all have the same internal shape.

### Top-level structure

```
substrate-root/
  exfu/                     # convention base (plugin-owned, not user-editable)
    v0.3/                   # versioned conventions -- deliberately flat and small
      readme.md             # orientation map for this directory
      ontology.md           # the complete core ontology, one file
      principles.md         # design principles + recommendations
      librarians/           # exfu-shipped librarian definitions
      skills/               # exfu-shipped skill sources (wow template)
    derived/                # generated content (unversioned cache)
      index.json            # the global index -- the primary navigation tool
      agent-registry.json   # registered scheduled agents and their health
      agent-log.json        # run history
      dashboard/            # generated HTML dashboard
    latest.txt              # points to current version (e.g. "v0.3")
  user/                     # personal scope (unversioned, always follows latest)
    scope.md
    context/                # personal background (about-me, preferences)
    ontology/               # personal definitions, ways of working
    ...                     # other folder-types materialise as content appears
  scopes/                   # the tree of everything else
    acme/                   # a scope (has scope.md)
      scope.md
      context/
      todo/
      scopes/               # child scopes gathered here
        sales/
          scope.md
          ...
    side-project/            # another scope
      scope.md
      ...
```

### How to tell a scope from a grouping folder

- **Scope:** has a `scope.md` file. It's a real working context.
- **Grouping folder:** no `scope.md`. Purely organisational (e.g. `scopes/clients/`). Ignore it structurally.

### scope.md format

```yaml
---
name: <human-readable name>
parent: <parent scope name, or "root" for top-level>
exfu: v0.3
---
```

Followed by a protective header blockquote, then an optional purpose statement in markdown.

The `user/` scope omits the `exfu` field (it's unversioned, always follows latest) and sets `parent: none`.

### The 10 folder-types

Inside any scope, these are the standard vocabulary for where things go:

| Folder | What it answers |
|---|---|
| `ontology/` | What do the concepts and terms in this scope mean? |
| `context/` | What background should an agent know here? (including kept reference documents) |
| `skills/` | What skill definitions belong to this scope? |
| `librarians/` | What substrate maintenance runs here on a schedule? |
| `scheduled/` | What business-logic work runs here on a schedule? |
| `todo/` | How does this scope handle tasks? |
| `reminders/` | How does this scope handle lightweight nudges? |
| `inbox/` | Where do uncategorised thoughts go for this scope? |
| `databases/` | Where do structured, repeating records live? (CRM, logs, journals) |
| `visualisations/` | Where do agent-created visual outputs live for this scope? |

Each materialised folder-type has an `agent.md` that follows the reference+delta pattern (see below). The catalogue is open -- a scope may add folder-types not listed here (define them in the scope's ontology).

**Materialise on demand.** Folder-types exist only where there is content. A scope with just scope.md and context/ is healthy, not incomplete. Never scaffold empty folders; add a folder-type the moment its first content appears (the scope-setup skill handles this).

**Store-or-point.** A folder-type may contain actual data, or its agent.md may say "tasks are in ClickUp." The convention guarantees the location is discoverable; whether data lives there is per-scope, per-user.

### The reference+delta pattern (agent.md)

Every materialised folder-type directory contains an `agent.md` with this structure:

1. **Protective header** (blockquote, always first):
   > This folder follows ExFu conventions. If you haven't loaded them yet, ask your user to set you up with their WoW or ExFu skills.

2. **`Follows:` line** naming the upstream convention by versioned anchor into the core ontology file:
   `Follows: exfu/v0.3/ontology.md#todo`

3. **`Local deviations:` section** listing only what differs from upstream. If nothing differs, this section is omitted entirely.

A folder with no deviations is two lines plus the header. The agent reads the referenced section of `ontology.md` for full behaviour.

**Descriptors carry no state.** agent.md, readme.md, and scope.md describe what a folder is *for* -- never its current contents, counts, or status. "Currently empty" goes stale silently; state lives in the derived index and the content itself.

### Scope nesting

Scopes nest via a dedicated `scopes/` subdirectory. A scope's own folder-types sit at the scope's root level; child scopes are gathered in `scopes/`. The pattern is self-similar at every level.

Each nested scope declares its parent in scope.md. This is a portability safeguard -- if a scope is shared or extracted on its own, the agent knows something is missing from its ontologies rather than silently operating with an incomplete picture.

### Ontology resolution

When operating inside a scope, read all relevant ontologies by walking the declared parent chain: active scope, each ancestor scope, `user/ontology/`, then `exfu/<version>/ontology.md`. Hold them all together. When definitions conflict, recognise both and ask the user in context which applies. There is no automatic cascade, no deterministic precedence rule -- the agent supplies the judgment.

When writing new ontology entries that touch existing terms, annotate the intent: "This extends the user-level definition of X" or "This scope uses Y differently from Z scope."

---

## Wrapping plugin awareness

The exfu-library skill operates in two modes depending on whether a wrapping plugin is active.

**With a wrapping plugin:** the wrapper provides the permission lookup function and any verb overrides. The exfu-library skill defers to the wrapper for these. The wrapper is detected via a marker in `${CLAUDE_PLUGIN_ROOT}`.

**Without a wrapping plugin:** fall back to install-time-resolved values or use safe defaults:

- Permission level: `member`
- Surface a note that permission detection wasn't available, and suggest the user run the install skill if they haven't yet

The exfu-library skill does not require a wrapping plugin to function. Wrappers are additive. Solo installs have no wrapper and that's correct.

---

## Core concepts

These are internalised here so they're available even when the convention base hasn't been loaded yet in a given conversation.

**Substrate (the Agent Library).** The combination of files, skills, connectors, and scheduled agents that together give Claude persistent memory and context across sessions and devices. No single component is the substrate -- it's the interplay. To its user, the whole thing is their Agent Library; substrate is the internal register (see `ontology.md#vocabulary`).

**Scope.** A bounded context with its own knowledge, definitions, and conventions. Everything is a scope: personal space, org, team, project, client. Every scope has the same internal shape (the 10 folder-types). Scopes can nest via their own `scopes/` subdirectory. A scope is identified by the presence of `scope.md`.

**Folder-type.** A standard kind of content that a scope may contain: ontology, context, skills, librarians, scheduled, todo, reminders, inbox, databases, visualisations. Each is a discovery convention first, a storage location second -- it tells an agent how the scope handles that kind of thing. Folder-types materialise only when content exists for them.

**Convention base.** The exfu-shipped definitions at `exfu/<version>/`. Defines what each folder-type means and how it behaves by default. Every agent.md references the convention base and records only local deviations.

**Scheduled agent.** Recurring work defined as agent instructions: a markdown definition an agent reads cold and carries out on a cadence, registered in `exfu/derived/agent-registry.json` and executed by one scheduled task per cadence. Two kinds with identical mechanics: **librarians** (remit: the substrate itself; definitions in `librarians/` folders; the nightly index is the canonical example) and **business agents** (remit: the user's recurring domain work; definitions in `scheduled/` folders). Librarians run before business agents within a cadence. In the user-facing register, the librarians are the user's Agent Librarians -- the ecosystem that keeps their library organised.

**Global index.** The file at `exfu/derived/index.json`. One read gives the whole-substrate map: every scope, where it sits, what it contains, which conventions it follows. Generated by the nightly index librarian. The primary navigation tool for agents.

**Skill.** A named bundle of instructions and conventions that Claude loads on demand. Every skill has a name, a description (which controls when it triggers), and a body of guidance.

**Access modes.** When the filesystem is mounted in this session, use it directly. When it's not (mobile, unmounted sessions), use the connector. Filesystem is faster; the Dropbox connector also supports delete, move, and rename natively, addressed by path.

**Data tiers.**
- Tier 1: project files -- source code, documents, designs. Live in their natural home. Referenced from the substrate, not stored in it.
- Tier 2: third-party tools -- SaaS platforms. Accessed via connectors.
- Tier 3: substrate core -- this knowledge base. Holds context, scopes, databases, ways of working.

---

## Ongoing behaviour while loaded

- **Follow substrate conventions.** Folder structure, naming (lowercase hyphen-separated, date-prefix for time-sensitive files), agent.md maintenance via the reference+delta pattern.
- **Use the right access mode.** Filesystem when mounted, connector when not.
- **Delegate to the right storage skill.** For git-backed substrates, defer ongoing sync work to `git-substrate-sync`. For Dropbox-backed substrates, defer file CRUD to `exfu-dropbox-storage`. For local-only substrates, direct filesystem operations are sufficient. For legacy Box-backed substrates, suggest `exfu-migrate-to-dropbox` before doing substantive file work.
- **Navigate via the index.** When you need to find a scope or understand the substrate's shape, read the index first. Only walk the filesystem when the index is unavailable.
- **Maintain discoverability.** When you create new folders or content, create or update agent.md files with `Follows:` anchor references into the convention base's `ontology.md`. When you create a new scope, scaffold scope.md with the correct parent and version pin.
- **Materialise on demand, write no state into descriptors, prefer fewer complete files.** Don't create empty folder-types; add them when their first content appears. Never write "currently empty", counts, or status into agent.md/readme.md/scope.md. Extend existing files rather than scattering siblings; keep ontologies flat with one complete file per concept. (Full authoring rules: `exfu/<version>/ontology.md#authoring-rules`.)
- **Respect version pins.** When working inside a scope, use the conventions from the scope's pinned exfu version. Don't assume all scopes are on the latest version.
- **Don't assume context persists between sessions.** If you need information from the substrate, read it from the current state. Don't rely on memory from prior conversations.
- **Surface only what's actually there.** Don't invent scopes, folder-types, or permissions. Read the files and report what you find.
- **Keep git invisible.** For team substrates, all user-facing communication uses the verb vocabulary above. Git operations happen underneath; the user never needs to see them.
- **Plain language with users.** "Your library" and "your librarians" are the user-facing terms -- gloss them on first use ("your library: the knowledge base, skills, and routines that give Claude memory between sessions", "your librarians: the scheduled agents that keep it organised"). Librarians are always plural with users -- an ecosystem, never a single all-knowing character. "wow" stays wow. "Substrate" is internal register: surface it only when the user asks how things work underneath. Don't use other internal vocabulary ("scope", "ontology", "folder-type") unless the user has introduced those terms themselves; a scope can be introduced as a "shelf" or "working area" -- an analogy, not a rename. Speak in terms the user has earned: "the Acme area", "your definitions", "your background info", "the nightly tidy-up." Golden circle every explanation -- why it matters to them, the outcome in their words, at most one sentence of mechanics. File paths and internal names surface only when the user asks for the detail.
