---
name: scope-setup
description: Guided setup for creating new scopes in an ExFu substrate, and for adding folder-types to existing scopes later. Use when someone says "create a scope", "new project", "set up a workspace", "add a scope for X", "I've got a new client", "add a docket to this scope", "give this area somewhere for tasks and reminders", "this scope needs a database", or when the install conversation delegates scope creation. Handles both the user/ scope during first install and working scopes for projects, clients, or areas of focus. Asks a few questions, scaffolds only what has content, and wires up the folder-types the user actually needs.
---

# Scope setup

You create scopes -- the structural unit of active work in an ExFu substrate -- and you add folder-types to scopes that already exist. A scope is a directory with a `scope.md` boundary marker and folder-types inside it. This skill guides the user through both jobs conversationally.

You are called in three situations:
1. The install conversation delegates here (for user/ and the first working scope).
2. The user invokes you directly ("I've got a new client, create a scope").
3. A scope needs a folder-type it doesn't have yet ("let's track sightings for this" -- the scope needs databases/; "remind me about this next week" in a scope with no docket -- the scope needs docket/).

---

## Hard constraints

1. **Materialise on demand -- never scaffold empty folders.** Create a folder-type only when you have actual content to put in it right now, or the user has explicitly asked for it (e.g. a docket whose tasks point at their task tool). An empty folder with boilerplate descriptors is noise every future read pays for. There is no minimum set: a scope with only scope.md is valid. Folder-types are added later, the moment content for them first appears -- that's situation 3, and it's the normal way scopes grow.
2. **Documents are context; repeating records are databases.** Reference documents (PDFs, spreadsheets, transcripts, exports, anything "filed for keeping") live in `context/`, beside the prose that gives them meaning; anything with a repeating shape lives in `databases/`. This routing holds during migrations too -- an old vault's document piles become context.
3. **No state in descriptors.** scope.md, agent.md, and readme.md describe what a folder *is for* -- static facts that stay true. Never write "currently empty", item counts, "last updated", or any other snapshot of current state into them. State goes stale silently and misleads every later reader. One carve-out: scope.md may carry the `status: stale` lifecycle assertion (see below) -- a deliberate declaration, not a snapshot.
4. **Fewer, more complete files.** When writing ontology entries, one complete file per concept (or one file for the whole ontology while it's small) -- never a nest of fragments. When capturing context, extend an existing file before creating a sibling.
5. **Ontology holds concepts, not instances.** A definition of what something *means* goes in ontology/. An instance of a known concept goes where that concept prescribes: a librarian definition in librarians/, a business agent in scheduled/, records in databases/, reference documents in context/. If you're about to put a file in ontology/ ask: "is this a new kind of thing, or a thing of a known kind?"
6. **Never use em-dashes.** Use " -- " (space-dash-dash-space) instead.
7. **Conversational, not a form.** Ask questions naturally. Don't present a checkbox list of folder-types. Weave the questions into the flow based on what the user has told you.
8. **Outcome-first, plain language.** You are often talking to a brand-new user mid-install. Golden circle every explanation: why it matters to them, what they get, and at most one plain sentence of how. Say "an area for your Acme work", not "a scope"; "a place for what's open here", not "a docket folder-type"; "a reminder rule", not "a cron trigger"; "send automatically" or "prepare only", not "auto" or "draft"; report what they now have, never which files you wrote. Internal terms arrive one at a time, only after the user has the thing they name -- "your docket" is fine once they have one.
9. **Always read `exfu/latest.txt` from the substrate root** to get the current version string for the `Follows:` references and scope.md frontmatter. Never hard-code a version.
10. **Use the templates from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/`** as the source for scaffolding, and `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/` for sane-default content.

---

## Flow A -- creating a scope

### Step 1 -- Name and purpose

Ask for the scope name and what it's for. One natural question covers both:

> "What's this scope for? Give me a name and a line on what it covers."

The name becomes the directory name (lowercase, hyphen-separated). The purpose becomes the one-liner in scope.md.

If the user gives you enough in their opening message (e.g. "create a scope for my Acme project -- it's our biggest client account"), pull the name and purpose from that. Don't re-ask what you already know.

### Step 2 -- Parent

Determine where this scope lives:

- If the user is already inside an existing scope's `scopes/` directory, infer the parent from that scope's `scope.md`. Confirm with the user: "Looks like this would be nested under [parent]. That right?"
- If the install conversation is calling you for a top-level working scope, the parent is `root` and the location is `scopes/<scope-name>/`.
- Otherwise ask: "Is this top-level, or does it sit inside an existing scope?" If top-level, parent is `root`. If nested, ask which parent scope, and place it under `<parent-scope>/scopes/<scope-name>/`.

### Step 3 -- What content exists right now?

This step decides which folder-types materialise. The question is never "which folders do you want?" -- it's "what do you have, and what do you do, in this area?" Map their answers to folder-types and create only those.

- The user describes background, stakeholders, history, or hands you documents -> **context/** (this also covers reference documents: PDFs, spreadsheets, transcripts -- a kept document is context with a file extension).
- The scope has its own jargon or terms that need defining -> **ontology/** (one complete file per concept; usually starts as a single file).
- The scope is active work: the user tracks tasks here, has deadlines, obligations or check-in patterns, or generates unsorted input they want their agents to deal with -> **docket/**. In plain language: a place for what is open here -- tasks, reminders, and things you leave for your agents. One folder, three files, each materialising on its first entry; tasks are almost always a pointer to their existing tool (see Step 4).
- Structured repeating records: contacts, pipeline, sightings, logs, journal entries -> **databases/** (with a schema.md per database).
- Recurring work the user wants done without asking -- scanning, digesting, watching -> **scheduled/** (a scheduled business agent; write its definition here, then hand to the install-scheduled-agent skill to register it).
- Maintenance this scope itself needs on a schedule -> **librarians/**.
- Skill sources belonging to this scope -> **skills/**.
- Visual outputs to keep -> **visualisations/**.

Don't rattle off this list to the user. Listen to what they tell you about the scope, propose the two or three folder-types their answers imply, and confirm. If only context exists right now, the scope gets scope.md and context/ -- that's a healthy scope, not an incomplete one. Tell the user the rest arrives on demand: "When you first capture a task or a thought here, the right folder appears then."

Never scaffold `todo/`, `reminders/` or `inbox/`. They are the deprecated shape (`ontology.md#deprecated`): readable where they already exist, never created new. If the user asks for one of them by name -- "add an inbox", "set up a reminders folder" -- explain the docket in one plain sentence ("those all live together now in one place for what's open here: tasks, reminders, and things you leave for your agents") and offer that instead.

### Step 4 -- Pointer or store, per file

The docket stores or points **per file** (`ontology.md#docket`): tasks can live in the user's task tool while reminders and the agent backlog stay local. So the question is about tasks, and only tasks:

> "Are you tracking tasks in something already -- ClickUp, Linear, Todoist -- or keep them here?"

- **Keep them here:** nothing to declare; `todo.jsonl` appears on the first task.
- **Pointer:** capture the tool name. If the user volunteers connection details (a workspace, a board, a list id), capture those too; never a secret. Don't press for details they don't have handy. This becomes a `todo:` line under `Local deviations:` in `docket/agent.md`, from `defaults/docket-pointer.md`.

Reminders and the agent backlog default to local and need no question. If the user says their reminders live elsewhere (a calendar app, say), the same pointer line shape works for `reminders:`; that is rare, so don't ask.

**Optional: where reminders should reach them.** Only if the user mentions Slack, WhatsApp, email or similar during the conversation, ask one brief question:

> "Want reminders here to reach you somewhere -- Slack, WhatsApp, email? Which one, and may your agents send there automatically, or only prepare the message for you to send?"

If they name one, record a channel row in `docket/channels.jsonl` in the shape `ontology.md#channels` gives: a library-wide id, a `name` (e.g. `slack-dm`), `kind: dm` (it reaches them; `broadcast` only if they name a group or a shared channel), `via` the connector, `target` the address, `send: draft` unless they said automatic, and the envelope (`created`, `updated`, `revision: 1`). If they said automatic, `send: auto` **and** append a grant to `durable/ledger/grants.md` in the shape of `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/grants.md` (channel id, name and scope; granted date; who, on which surface, at which plugin version; their words) -- the grant is what authorises it, the flag alone grants nothing. Say plainly what "automatically" means before they answer: their agents may send to that address on their behalf without asking each time, and they can take it back later. If they don't mention a channel, don't ask; reminders surface in the session and on the dashboard, which is always there.

### Step 5 -- Scaffold

Create the directory, scope.md, and the folder-types selected in Step 3 -- with their content, not as empty shells. Read the exfu version from `exfu/latest.txt` at the substrate root. Use that version in all `Follows:` references and in the scope.md `exfu:` frontmatter field.

For `docket/`, scaffold `agent.md` from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/docket/agent.md` (or `defaults/docket-pointer.md` when tasks point elsewhere) plus `readme.md` from `defaults/docket-readme.md`. Do not create `todo.jsonl`, `reminders.jsonl` or `agent-backlog.jsonl` now: each appears on its first entry, and a docket holding only `agent.md` is healthy. If Step 4 produced a channel, `channels.jsonl` is the one file that may exist from the start, because it is content.

---

## Flow B -- adding a folder-type to an existing scope

This is how scopes grow, and any agent can do it mid-conversation the moment content appears ("leave this for my agents" in a scope with no docket -> create the docket, then append the entry to `agent-backlog.jsonl`).

1. Confirm the scope (the directory with the governing scope.md).
2. Read the scope's `exfu:` pin from scope.md (fall back to `exfu/latest.txt`).
3. Create the folder-type directory with its `agent.md`: protective header + `Follows: exfu/<version>/ontology.md#<type>` + `Local deviations:` only if something differs (e.g. a pointer to an external tool).
4. Put the content in. The content is why the folder now exists. For a docket entry, that means one JSON line in the right file under the record envelope (`ontology.md#records`): an id, `title`, `status: open`, `created`, `updated`, `revision: 1`, and `keywords` you choose at save time; a dated reminder also gets a trigger row in `triggers.jsonl` (`ontology.md#triggers`).
5. Mention it to the user in one line: "This area now has a place for what's open, and I've left that with your agents."

If the folder-type is `scheduled/` or `librarians/`, writing the definition is this skill's job; registering it so it actually runs is the install-scheduled-agent skill's job. Hand over and say so.

---

## What gets created

### scope.md

```yaml
---
name: <scope-name>
purpose: <one-line purpose>
parent: <parent-scope-name or "root">
exfu: <version from latest.txt>
---
```

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

<optional 2-3 sentence elaboration of purpose -- what it's for, never what it currently contains>
```

New scopes never carry a `status:` line. Later, when a scope winds down but isn't ready to delete or archive, add `status: stale` to the frontmatter -- a deliberate assertion that its content is no longer kept current. The next index run picks it up and the dashboard badges the scope. Remove the line to reactivate. `stale` is the only recognised value; never write `status: active`.

### agent.md (any folder-type, no deviations)

Use the template from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/<folder-type>/agent.md`:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/<version>/ontology.md#<type>
```

The anchor (`#context`, `#docket`, `#scheduled-agents`...) targets that folder-type's section in the core ontology file. A one-line human-friendly `readme.md` alongside is optional; if you write one, the same no-state rule applies.

### docket (everything local)

Use the sane defaults from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/`. Copy the content as-is -- these are ready to use without further setup.

- `scope/docket/agent.md` (identical to `defaults/docket-agent.md`) as `docket/agent.md`.
- `defaults/docket-readme.md` as `docket/readme.md`.
- No entry files. `todo.jsonl`, `reminders.jsonl` and `agent-backlog.jsonl` each appear on their first entry; `triggers.jsonl`, `signals.jsonl`, `fires.jsonl` and `archive.jsonl` are written by the skills and librarians that need them.

### docket (tasks point elsewhere)

Start from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/docket-pointer.md`:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/<version>/ontology.md#docket

Local deviations:
- todo: tracked in <tool-name>, not stored locally
- <connection details if provided, e.g. workspace, board, list id; never a secret>
```

The other files stay local; a pointer is per file, so `reminders:` can take the same line shape if the user's reminders genuinely live elsewhere. There is never a `todo.jsonl` in a docket whose `todo:` points away -- the external tool holds the tasks and their history.

### docket/channels.jsonl (only when the user asked for one)

One JSON object per line, per `ontology.md#channels`:

```json
{"id":"<UTC timestamp to the second>-<ten or more random base32 chars>","name":"slack-dm","kind":"dm","via":"slack","target":"@<handle>","send":"draft","created":"<ISO>","updated":"<ISO>","revision":1}
```

`send: auto` is only ever written together with a grant appended to `durable/ledger/grants.md`. Until the outward mechanism is complete, only a `dm` to the user themself is honoured automatically; anything outward is drafted even when granted, and you should say so if they ask for automatic sending to someone else.

### databases

Each database is a subfolder (or single file) with a `schema.md` describing the record shape: the fields, what each means, the filename convention (record filenames are natural keys so wikilinks resolve). Recurring personal records -- daily logs, journals -- are databases too: same shape every time means schema, even when each record is prose.

### scheduled agents and librarians

Definitions follow the format in the core ontology (`exfu/<version>/ontology.md#scheduled-agents`): YAML frontmatter with `name`, `cadence`, `description` (plus optional `scripts`, `reads`, `writes`, `depends_on`), body = the instructions a cold agent carries out. Remit decides the folder: substrate maintenance is a librarian in librarians/; the user's domain work is a business agent in scheduled/. Definitions do nothing until registered -- hand to install-scheduled-agent for that.

---

## Special case: the user/ scope

When creating the user/ scope during the install conversation:

1. **Name** comes from the about-me conversation that preceded this. Use whatever the user said their name is.
2. **Parent** is `none` (it's the personal scope, not nested under anything).
3. **No `exfu:` field** in scope.md. The user/ scope doesn't pin a version -- it's always current.
4. **context/about-me.md** is populated with what was captured during the about-me conversation. This is the user's identity document, and it's why context/ materialises here.
5. **ontology/ways-of-working.md** is populated with the user's captured working preferences -- their personal conventions, communication style, decision defaults. (The way-of-working *concept* is defined in the ExFu core ontology; this file is the user's own content for it.) Only create it if preferences were actually captured.
6. **Optional folder-types:** offer a docket as in the normal flow -- `user/docket` is where most people keep their personal tasks, reminders and captures, and where they declare the channel their reminders reach them on (Step 4). The `setup-docket` skill generates their personal `<username>-docket` skill against it; that is a separate conversation, not part of scope creation. skills/ is common for the user/ scope later -- it holds the sources of their generated personal skills (wow, docket, writing styles) -- but it materialises when the first skill is generated, not now.

The user/ scope lives at the substrate root -- not inside `scopes/`. Its scope.md format:

```yaml
---
name: <username>
purpose: Personal workspace and global defaults
parent: none
---
```

followed by the protective header.

---

## After scaffolding

1. **Confirm.** Tell the user what you built and why each part exists: the scope name, which folder-types materialised and what content went into them, whether anything points to an external tool. Two or three sentences.
2. **Hand back.** If the install conversation called you, hand control back. If the user called you directly, ask if they want to do anything with the new scope right away or if they're done.
3. **Don't create a scope skill automatically.** Scope skills are a separate concern; the scope is usable immediately through the exfu-library skill.
4. **Suggest an index refresh** if several scopes changed: the nightly-index librarian will catch up overnight anyway, so only mention it when the user needs current navigation immediately.

---

## Dependencies

- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/` -- per-folder-type agent.md stubs.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/` -- sane-default content for the docket (`docket-agent.md`, `docket-pointer.md`, `docket-readme.md`). The todo, reminders and inbox defaults beside them serve deprecated scopes only; never scaffold from them.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/grants.md` -- the shape of a grant entry, appended when a channel is elevated to automatic sending.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/actors.md` -- the actor record; when a `dm` channel to the user is declared, add its target id to their record so the dispatcher can see the channel reaches the owner.
- `exfu/latest.txt` in the substrate root -- current version string.
- `exfu/<version>/ontology.md` in the substrate -- the core ontology this skill implements; read its folder-type sections when judgment calls arise.
- The substrate must be accessible (filesystem or connector) before this skill can scaffold anything. If it isn't, say so and stop.
