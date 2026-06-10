---
name: scope-setup
description: Guided setup for creating new scopes in an ExFu substrate. Use when someone says "create a scope", "new project", "set up a workspace", "add a scope for X", "I've got a new client", or when the install conversation delegates scope creation. Handles both the user/ scope during first install and working scopes for projects, clients, or areas of focus. Asks a few questions, scaffolds the directory with sane defaults, and wires up the folder-types the user wants.
---

# Scope setup

You create scopes -- the structural unit of active work in an ExFu substrate. A scope is a directory with a `scope.md` boundary marker and one or more folder-types inside it. This skill guides the user through creating one conversationally.

You are called in two situations:
1. The install conversation delegates here (for user/ and the first working scope).
2. The user invokes you directly ("I've got a new client, create a scope").

Both paths use the same flow below, with a special case for the user/ scope noted at the end.

---

## Hard constraints

1. **Never use em-dashes.** Use " -- " (space-dash-dash-space) instead.
2. **Conversational, not a form.** Ask questions naturally. Don't present a checkbox list of folder-types. Weave the questions into the flow based on what the user has told you.
3. **Context and ontology are always created.** Don't ask about these -- they're needed for any scope to be useful.
4. **Always read `exfu/latest.txt` from the substrate root** to get the current version string for the `Follows:` references and scope.md frontmatter. Never hard-code a version.
5. **Use the templates from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/`** as the source for scope scaffolding. Use the defaults from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/` for sane-default content.
6. **Don't over-scaffold.** Only create folder-types the user actually wants. Docs, skills, librarians, databases, and visualisations are offered only if the user's description suggests them.

---

## The flow

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

### Step 3 -- Folder-types

Context and ontology are always created. Don't mention them as options.

For the three "daily workspace" types, ask naturally based on what the user told you about the scope's purpose. Don't rattle off a list -- pick up on cues:

- **Todo.** "Do you want a place to track tasks for this? It can store them locally or point to whatever tool you already use." Offer this for any scope that sounds like active work.
- **Reminders.** "Do you want time-based reminders here -- nudges separate from your tasks?" Offer when the scope has ongoing obligations, deadlines, or check-in patterns.
- **Inbox.** "Do you want a quick-capture inbox for unsorted thoughts and links?" Offer when the scope sounds like it generates a lot of unstructured input.

For the remaining types, only suggest them if the user's description makes them relevant:
- **Docs** -- if the scope involves written deliverables, reference material, or documentation.
- **Skills** -- if the scope has specialised workflows that would benefit from skill files.
- **Librarians** -- if the scope has enough content to need automated maintenance.
- **Databases** -- if the scope tracks structured data (contacts, inventory, metrics).
- **Visualisations** -- if the scope involves dashboards, charts, or visual reporting.

If none of the advanced types seem relevant, don't mention them. Keep it tight.

### Step 4 -- Pointer or store

For todo, reminders, and inbox: ask whether to store content locally or point to an external tool.

Keep it brief: "Are you tracking tasks in something already -- ClickUp, Linear, Todoist -- or do you want to keep them here?"

- **Local store:** use the sane defaults (see below). These work out of the box.
- **Pointer:** capture the tool name. If the user volunteers connection details (a project ID, a board name), capture those too. Don't press for details they don't have handy.

### Step 5 -- Scaffold

Create the directory structure. Read the exfu version from `exfu/latest.txt` at the substrate root. Use that version in all `Follows:` references and in the scope.md `exfu:` frontmatter field.

---

## What gets created

### Directory structure

```
<scope-name>/
  scope.md
  context/
    agent.md
  ontology/
    agent.md
  todo/              # if selected
    agent.md
    done.md          # if local store
  reminders/         # if selected
    agent.md
    archive.md       # if local store
  inbox/             # if selected
    agent.md
  docs/              # if selected
    agent.md
  skills/            # if selected
    agent.md
  librarians/        # if selected
    agent.md
  databases/         # if selected
    agent.md
  visualisations/    # if selected
    agent.md
```

### scope.md

```yaml
---
name: <scope-name>
parent: <parent-scope-name or "root">
exfu: <version from latest.txt>
---

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

<purpose statement -- one to three sentences about what this scope is for>
```

### agent.md (for context and ontology -- always created)

Use the template from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/<folder-type>/agent.md`. The standard content:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/<version>/ontology/folder-types/<type>.md
```

### agent.md (for optional folder-types with local store)

Use the sane defaults from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/`. Copy the content as-is -- these are ready to use without further setup.

**Todo (local):** Copy `defaults/todo-default.md` as `todo/agent.md`. Also create `todo/done.md` from `defaults/todo-done.md`.

**Reminders (local):** Copy `defaults/reminders-default.md` as `reminders/agent.md`. Also create `reminders/archive.md` from `defaults/reminders-archive.md`.

**Inbox:** Copy `defaults/inbox-default.md` as `inbox/agent.md`. Inbox is always local (no pointer variant).

### agent.md (for optional folder-types with pointer)

Use the pointer template from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/todo-pointer.md` as a starting point. Replace `<tool-name>` with the actual tool name and `<connection details if provided>` with whatever the user gave you. If no connection details were provided, remove that line.

**Todo (pointer):**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/<version>/ontology/folder-types/todo.md

Local deviations:
- Tasks are tracked in <tool-name>, not stored locally
- <connection details if provided>
```

**Reminders (pointer):**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/<version>/ontology/folder-types/reminders.md

Local deviations:
- Reminders are managed in <tool-name>, not stored locally
- <connection details if provided>
```

No `archive.md` or `done.md` when using a pointer -- the external tool handles history.

### agent.md (for docs, skills, librarians, databases, visualisations)

Use the corresponding template from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/<folder-type>/agent.md`. These are the standard two-line agent.md files (protective header + Follows reference).

---

## Special case: user/ scope

When creating the user/ scope during the install conversation:

1. **Name** comes from the about-me conversation that preceded this. Use whatever the user said their name is.
2. **Parent** is `none` (it's the personal scope, not nested under anything).
3. **No `exfu:` field** in scope.md. The user/ scope doesn't pin a version -- it's always current.
4. **Always include:** context and ontology.
5. **context/about-me.md** is populated with what was captured during the about-me conversation. This is the user's identity document.
6. **ontology/ways-of-working.md** is populated with the ways-of-working captured during the conversation.
7. **Optional folder-types:** offer todo, reminders, inbox as in the normal flow. Skills is also common for the user/ scope (it holds the user's personal skill files).

The user/ scope lives at the substrate root -- not inside `scopes/`. Its scope.md format:

```yaml
---
name: <username>
purpose: Personal workspace and global defaults
parent: none
---

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.
```

---

## Integration

- The install conversation delegates here for both the user/ scope and the first working scope.
- Users can invoke directly at any time for organic scope creation.
- The exfu version for all `Follows:` references comes from `exfu/latest.txt` in the substrate. Never assume a version -- always read it.
- After scaffolding, confirm to the user what was created with a brief summary. Don't list every file -- summarise by folder-type.

---

## After scaffolding

Once the scope is created:

1. **Confirm.** Tell the user what you built: the scope name, which folder-types are included, whether anything points to an external tool. Keep it to two or three sentences.
2. **Hand back.** If the install conversation called you, hand control back. If the user called you directly, ask if they want to do anything with the new scope right away (add context, create tasks, etc.) or if they're done.
3. **Don't create a scope skill automatically.** Scope skills (`scope-<name>`) are a separate concern. If the user asks for one, that's a different conversation. The scope is usable immediately through the substrate skill without a dedicated scope skill.

---

## Dependencies

- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/scope/` -- scope directory template with stub agent.md files.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/defaults/` -- sane-default content for todo, reminders, inbox.
- `exfu/latest.txt` in the substrate root -- current version string.
- The substrate must be accessible (filesystem or connector) before this skill can scaffold anything. If it isn't, say so and stop.
