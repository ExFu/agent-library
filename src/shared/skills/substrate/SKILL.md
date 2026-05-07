---
name: substrate
description: ExFu's substrate is the persistent system of files, skills, connectors, and scheduled tasks that gives Claude memory and working context across sessions — a knowledge base the user builds up over time, covering who they are, what they're working on, and how they operate. This skill bootstraps any Claude session with that context: it finds the knowledge base, reads the ways-of-working guide, orients to the directory structure, detects orgs and teams, surfaces the right verbs for git-backed substrates, and pulls in relevant scope context. Load it at the start of any substrate-aware conversation, or when the user's personal wow skill delegates to it. Triggers on "do you know who I am?", "can you pull up the Acme deal?", "where is my stuff?", "what do I have on this week?", "do you know about X?", "what's in my notes on Y?", "what have we got on Z?", "save this", "check for updates", or any other conversation where the user expects Claude to have standing context about them or their work.
---

# Substrate skill — v0.2.0

## Hard constraints

Read these before doing anything else. They apply for the entire session.

1. **Never write PII into the substrate proper.** Before writing any file to the substrate, check whether it contains identifiable personal information about someone other than the user (names, emails, contact details, health data, financial identifiers). If it does, route it to the PII layer connector instead (see the two-layer model section). If no PII layer is configured, refuse with a plain explanation and suggest the user set one up.

2. **Never fabricate org or team membership.** Only surface orgs and teams that are actually present in `orgs/` and `teams/` folders in the substrate. If neither folder exists, the user is in no orgs or teams. Do not invent structure.

3. **Never overwrite the CLAUDE.md guard without confirmation.** If a `CLAUDE.md` already exists at the substrate root, do not modify or replace it without the user explicitly asking. It is a safety guard, not content.

4. **Never surface admin verbs without confirmed admin permissions.** Do not show `approve change`, `review`, or `reject` vocabulary unless the permission lookup (see below) returns `admin` or `maintainer`. When in doubt, default to member rights.

5. **Respect the two-layer boundary at all times.** The substrate proper is for shareable, non-PII knowledge. The PII layer is for anything identifiable. This boundary is non-negotiable regardless of what the user asks.

---

## What to do when this skill loads

### Step 1 — Find the substrate root

The substrate core lives in a knowledge base (Box for solo installs, a git repository for team installs). Check whether the folder is mounted in this session (filesystem access available) or whether you need to use the connector.

If you're not sure where the knowledge base is, check the Global Instructions — the path should be noted there. If it's not, ask the user.

### Step 1.5 — Detect the storage backend

Read `_meta/storage-backend.md` if it exists. The install conversation writes this file to record what the user picked: one of `git`, `box`, or `local`. The detected backend determines which verb vocabulary to surface, whether sync logic applies, and which storage skill to delegate to.

If the file doesn't exist, infer:
- A `.git/` directory at the substrate root means git-backed.
- The substrate root path inside a Box mount or `~/Library/CloudStorage/Box-Box/...` style location means Box-backed.
- Otherwise, default to `local` (no automated sync layer; the user manages propagation).

Note the backend for the rest of the session. Subsequent steps adapt to it.

### Step 2 — Check for the CLAUDE.md guard

At the substrate root, check whether `CLAUDE.md` exists.

- If it exists, continue. It confirms you're in a substrate root.
- If it doesn't exist, you may be in an unguarded substrate (or this may be a first-time setup). See the CLAUDE.md guard section below for what to do.

### Step 3 — Read the substrate guide

Read `context/ways-of-working/substrate-guide.md` from the knowledge base. This is the durable reference for directory layout, conventions, access modes, naming rules, the scope/context distinction, and the two-layer model.

If the file doesn't exist yet, the substrate may not be fully set up. Tell the user. A copy of the guide is available in the plugin resources at `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` — read it from there to orient yourself on what to set up.

### Step 4 — Orient to the directory structure

Read `_meta/substrate-index.md` from the substrate root. This is the auto-generated folder map, updated nightly by the substrate-index scheduled task. It gives you a current, complete picture of every folder in the substrate with a one-line Purpose and Contents note for each.

If the file is not there, flag this to the user: either the substrate-index scheduled task has not been registered yet, or it has not run yet. Suggest registering it via the Cowork Scheduled tab (the task prompt is in `${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/TASK.md`), or running the script manually for an immediate first index:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <substrate-root>
```

The index is part of the substrate's expected baseline. In steady state, a substrate without `_meta/substrate-index.md` is missing a key orientation aid.

Read the top-level folder listing of the substrate root. You're looking for:

- `context/` — personal/default context
- `databases/` — personal/default structured data
- `scopes/` — all scopes (top-level only)
- `scratch/` — ephemeral working space (top-level only)
- `_meta/` — system infrastructure
- `_trash/` — soft-delete
- `orgs/` — present only if the user is in one or more orgs
- `teams/` — present only if the user is on one or more teams

Report honestly what's present. If `orgs/` and `teams/` are absent, the user is solo or hasn't set up team context yet.

### Step 5 — Orient to orgs and teams (if present)

**If `orgs/` exists:** list the org entries. For each, read `orgs/<org-name>/context/` to understand what org-wide context is available. Read `orgs/<org-name>/README.md` for the summary.

**If `teams/` exists:** list the team entries. For each, read `teams/<team-name>/context/` to understand team-specific context. Read `teams/<team-name>/README.md` for the summary, including any `parent_org:` front-matter that links the team to an org.

Tell the user plainly what you found. Example: "You're in 2 orgs and 3 teams. Here's what each holds: [summary per entry]." If both folders are absent, say so and move on.

### Step 6 — Check for a wrapping plugin

Check whether a wrapping plugin is active. Look for a `_meta/wrapper.json` or `_meta/wrapper.md` file at the substrate root, or a designated marker in `${CLAUDE_PLUGIN_ROOT}` that identifies the wrapper. If a wrapper is present:

- Defer to the wrapper for permission lookups.
- Defer to the wrapper for PII connector configuration.
- Defer to the wrapper for any org-specific verb vocabulary overrides.

If no wrapper is present, fall back to install-time-resolved values stored in `_meta/` (e.g. `_meta/permissions.md` or `_meta/pii-connector.md`). If neither exists, use safe defaults (member permissions, no PII layer).

### Step 7 — Permissions and verb surfacing

What this step does depends on the storage backend detected in Step 1.5.

**Git-backed substrates.** Determine the user's permission level via a provider-specific lookup. The lookup is resolved by the wrapping plugin or at install time. Contract:

```
lookup(remoteUrl: string) -> "admin" | "maintainer" | "member" | "read-only"
```

Configured by the wrapper or written into `_meta/permissions.md` at install time. When no lookup is configured, default to `"member"` and surface a brief note that permission detection wasn't available.

Surface verbs based on the result:

| Permission level | Verbs to surface |
|---|---|
| `admin` or `maintainer` | save, share for review, check for updates, fix clashes, approve change, review, reject |
| `member` | save, share for review, check for updates, fix clashes |
| `read-only` | check for updates only (explain that writes require someone with write rights to act on their behalf) |

Do not mention git commands at any point. Users interact through the verbs above.

**When checking for updates (git only):** prefer a non-LLM approach first. Compare the local HEAD commit hash against the remote HEAD hash. Only invoke a full sync process when there is a confirmed delta. Tokens are consumed only when needed.

**Box-backed substrates.** Box's own access controls determine what files the user can read and write; no separate permission lookup is needed. Surface a backend-appropriate verb set: `save` (write to the relevant Box folder), `check for updates` (rare; Box auto-syncs in most cases), `share for review` (notify a colleague to look — no built-in PR concept), `fix clashes` (walk the user through Box's version history if a sync conflict arose). The git-specific verbs (`approve change`, `review`, `reject`) do not apply.

**Local-only substrates.** The user has full rights to their local filesystem. No permission lookup, no fallback note. Verbs collapse to direct filesystem operations: `save` (write the file), `check for updates` (no remote to check; could mean "show me what changed since last session" if useful). Sharing-and-review verbs do not apply because there is no automated propagation layer; the user handles distribution manually.

### Step 8 — Read the current folder's README

If the conversation is happening inside a specific scope or context folder, read its `README.md`. Pay attention to the **Dependencies** section — it tells you what other parts of the substrate are relevant. Follow the chain: if a scope README points to team context, read that too.

### Step 9 — Check PII layer status

Check whether a PII layer connector is configured (wrapper or `_meta/pii-connector.md`). Note the status for the session:

- Connector configured: route PII writes to it automatically.
- No connector: if PII write is requested, refuse with explanation and offer to help the user set up a connector if they want one.

For solo installs without team context, there is typically no PII layer. That's expected. No action needed.

### Step 10 — Check reminders and inbox

If the `reminders` skill is installed, delegate to it: read the reminders file, surface anything due or overdue. If nothing is due, say nothing.

If the `inbox` skill is installed, delegate to it: check the count. If there are items, mention briefly ("Inbox has [n] items"). Don't force processing.

These checks are fast and quiet. Session start is not a ceremony.

### Step 11 — Orient and proceed

You should now understand: how the substrate is structured, which orgs and teams the user is in, what the current context and scope are, what permission level to operate at, and what (if anything) needs the user's attention.

If the user hasn't asked for anything specific yet, briefly confirm what you've loaded and ask what they'd like to work on.

---

## CLAUDE.md guard creation

The substrate root must contain a `CLAUDE.md` file. Its purpose is to prevent Claude from treating the substrate as a generic working folder when loaded in a session without the substrate skill.

**When this skill is called by an install skill at substrate creation time:**

1. Check whether `CLAUDE.md` exists at the root.
2. If it does not exist, write it immediately with the canonical content below.
3. If it does exist, do not overwrite it. Only modify it if the user explicitly asks.

Canonical content (copy this exactly):

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

The canonical content is also available as a reference in the substrate guide at `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`.

---

## Verb vocabulary (git-backed team substrates)

Users speak natural verbs to Claude in place of git terminology. Map each as follows:

| User says | What you do |
|---|---|
| save | Commit the change on the user's personal branch |
| share for review | Push the branch and open a pull request via the git provider API |
| check for updates | Check the remote HEAD hash; if there's a delta, pull from main |
| fix clashes | Walk the user through merge conflict resolution (guided, not technical) |
| approve change | Merge the pull request — only if permission level is `admin` or `maintainer` |
| review | Surface the open pull request for the user to read and respond to |
| reject | Close the pull request without merging — only if `admin` or `maintainer` |

Never expose git commands, branch names, or diff output directly to the user unless they ask. The above vocabulary is the interface.

**Lightweight sync before "check for updates":** before firing any sync process, compare local HEAD commit hash to remote HEAD commit hash using a non-LLM call. If they match, tell the user they're up to date — no further work needed. If there's a delta, proceed with the pull.

---

## Two-layer model

The substrate has two conceptual layers. The boundary is about what gets *stored*, not what Claude *sees*.

**Layer 1 — Substrate proper (this knowledge base).** Holds: skills, templates, context docs, structured non-PII data, configuration, sanitised test fixtures. Versioned, auditable, shareable, evolves slowly. Everything in the substrate's directory structure lives here.

**Layer 2 — PII layer (access-controlled store).** Holds: anything containing identifiable PII about other people — customer profiles, per-customer working memory, drafting feedback. Accessed at runtime via a guarded connector. The connector enforces access control; every query parameterised by user and subject. No general SELECT, no admin verbs from the rep-side connector.

**For solo installs:** there is typically no PII layer. That's expected and correct. If the user starts tracking third-party contact data and grows into a team context, this boundary becomes relevant.

**For team installs:** the PII layer connector is configured by the wrapping plugin or during the install conversation. The substrate skill expects either a configured connector or a "no PII layer" status noted in `_meta/`.

When asked to write data that may contain third-party PII:
1. Check whether the content contains identifiable information about others.
2. If yes, route to the PII layer connector (if configured) or refuse and explain why.
3. If no, write to the substrate normally.

When unsure whether something counts as PII, err on the side of caution. Ask the user, or put it in `scratch/` flagged for review.

---

## Multi-org / multi-team awareness

The substrate accommodates zero, one, or multiple orgs and teams. The folder structure is additive:

- A user in no orgs/teams has only the personal-default layout (`context/`, `databases/`, `scopes/`, `scratch/`, `_meta/`, `_trash/`).
- A user in one or more orgs has an `orgs/` folder with one entry per org.
- A user on one or more teams has a `teams/` folder with one entry per team.

Multiple entries under `orgs/` and `teams/` are fully supported. A manager spanning two departments would have two entries under `teams/`. A consultant working across two organisations would have two entries under `orgs/`.

When orienting, list each entry and give a one-line summary based on its README. Don't assume the user remembers the exact names of their orgs and teams — surface them.

**To find scopes belonging to a specific team or org:** search `scopes/` and filter by YAML front-matter. A scope's `README.md` carries `team: <team-name>` and/or `org: <org-name>`. Do not traverse into `teams/<team-name>/` looking for nested scopes — there are none. All scopes are top-level.

---

## Wrapping plugin awareness

The substrate skill operates in two modes depending on whether a wrapping plugin is active.

**With a wrapping plugin:** the wrapper provides the permission lookup function, the PII connector configuration, and any org-specific verb overrides. The substrate skill defers to the wrapper for these. The wrapper is detected via `_meta/wrapper.json` or a marker in `${CLAUDE_PLUGIN_ROOT}`.

**Without a wrapping plugin:** fall back to install-time-resolved values in `_meta/`. These were written during the install conversation when the user's setup was captured. If `_meta/` has no relevant files, use the safe defaults:

- Permission level: `member`
- PII layer: not configured
- Surface a note that permission detection wasn't available, and suggest the user run the install skill if they haven't yet

The substrate skill does not require a wrapping plugin to function. Wrappers are additive. Solo installs have no wrapper and that's correct.

---

## Core concepts

These are internalised here so they're available even when the guide hasn't been loaded yet in a given conversation.

**Substrate.** The combination of files, skills, connectors, and scheduled tasks that together give Claude persistent memory and context across sessions and devices. No single component is the substrate — it's the interplay.

**Skill.** A named bundle of instructions and conventions that Claude loads on demand. Every skill has a name, a description (which controls when it triggers), and a body of guidance. The description is what Claude matches against to decide whether to load the skill.

**Scope.** A user-defined area of active work or attention. Scopes are *where things happen* — plans, decisions-in-progress, drafts, working notes. Each scope has a dedicated folder under `scopes/` and usually a paired skill named `scope-<scope-name>`. All scopes are top-level in `scopes/` regardless of ownership.

**Context.** Persistent background information that describes the user, their people, their world, and their standing facts. Read-often, write-rarely. Identity-level material. `context/` holds this.

**Scope vs context.** Context is *about* things. Scopes are *where things happen*. Fuzzy-zone test: if you'd read it to orient, it's context. If you'd read it to pick up work, it's a scope.

**Data tiers.**
- Tier 1: project files — source code, documents, designs. Live in their natural home. Referenced from the substrate, not stored in it.
- Tier 2: third-party tools — SaaS platforms. Accessed via connectors.
- Tier 3: substrate core — this knowledge base. Holds context, scopes, databases, ways of working.

**Access modes.** When the filesystem is mounted in this session, use it directly. When it's not (mobile, unmounted sessions), use the connector. Filesystem is faster and supports delete, move, and rename.

---

## Ongoing behaviour while loaded

- **Follow substrate conventions.** Folder structure, naming (lowercase hyphen-separated, date-prefix for time-sensitive files), README maintenance, nothing casual at root.
- **Use the right access mode.** Filesystem when mounted, connector when not.
- **Delegate to the right storage skill.** For git-backed substrates, defer ongoing sync work to `git-substrate-sync`. For Box-backed substrates, defer file CRUD to `box-filesystem-management` and folder/sharing changes to `team-box-folders` (or `team-box-folder-provisioning` if it's a champion's initial setup). For local-only substrates, direct filesystem operations are sufficient.
- **Maintain discoverability.** When you create new folders or content, create or update READMEs with dependency links. When you create a new scope, set up or point to its scope skill.
- **Respect the scope/context distinction.** When deciding where to save new material, apply the fuzzy-zone test. When in doubt, put it in `scratch/` and flag it for later placement.
- **Don't assume context persists between sessions.** If you need information from the substrate, read it from the current state. Don't rely on memory from prior conversations.
- **Surface only what's actually there.** Don't invent orgs, teams, scopes, or permissions. Read the files and report what you find.
- **Keep git invisible.** For team substrates, all user-facing communication uses the verb vocabulary above. Git operations happen underneath; the user never needs to see them.
