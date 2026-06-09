# T3 -- Scope setup skill

A guided skill for creating new scopes with sane defaults for common folder-types. Used by install conversations and directly by users adding scopes to their substrate.

**Parents:** `T2-substrate-architecture.md` (domain), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-convention-base, T3-scope-model (phase 1, complete)
**Status:** not started.

---

## Why

Creating a scope today means knowing the conventions: scope.md format, which folder-types to include, the reference+delta agent.md pattern, protective headers. That's fine for agents that have read the convention base, but it's a lot to get right, and the install conversation needs a reliable, repeatable way to scaffold scopes.

The scope setup skill makes scope creation conversational. It asks a few questions, scaffolds the directory, and offers sane defaults for the folder-types most people want. This is the skill the install conversation delegates to when it's time to create a scope.

---

## What to build

### 1. Core flow

When the user says "create a scope for my Acme project" or the install conversation calls this skill:

1. **Name and purpose.** Ask for the scope name and a one-line purpose. ("What's this scope for?")
2. **Parent.** If inside an existing scope's `scopes/` directory, infer the parent. Otherwise ask: top-level (under scopes/) or nested under an existing scope?
3. **Folder-types.** Offer the standard set with brief explanations:
   - "Do you want a place for tasks? (todo)" -- explain briefly: tracks what needs doing, can point to ClickUp/Linear/Todoist or store tasks locally
   - "Do you want reminders?" -- time-based nudges, separate from tasks
   - "Do you want an inbox?" -- quick capture for unsorted thoughts and links
   - Context and ontology are always created (they're needed for the scope to be useful). Docs, skills, librarians, databases, visualisations are offered only if the user's description suggests them.
4. **Pointer or store.** For todo, reminders, inbox: ask whether to store locally or point to an external tool. If pointer, capture the tool name and any connection details.
5. **Scaffold.** Create the directory from the scope template, filling in scope.md frontmatter and agent.md deviations.

### 2. Sane defaults

For the three "daily workspace" folder-types, provide ready-to-use defaults:

**Todo (sane default):**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/todo.md

## Active tasks

<!-- Tasks are listed here as markdown checkboxes. Completed tasks are moved to done.md periodically. -->

- [ ] (no tasks yet)
```

Plus a `done.md` file for completed tasks.

**Reminders (sane default):**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/reminders.md

## Upcoming reminders

<!-- Reminders are listed with a date and a note. Past reminders are moved to archive.md periodically. -->

(no reminders set)
```

**Inbox (sane default):**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/inbox.md

## Unsorted items

<!-- Drop anything here. The inbox librarian sweeps periodically and helps triage. -->

(empty)
```

These defaults give the folder-type immediate utility without requiring a setup conversation. Users can customise later.

### 3. Pointer defaults

When the user picks "point to an external tool" for todo:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/todo.md

Local deviations:
- Tasks are tracked in <tool-name>, not stored locally
- <connection details if provided>
```

### 4. Template usage

The skill uses the scope templates from `plugin/src/shared/substrate/templates/scope/` (built in phase 1). It copies the template, fills in placeholders (scope name, purpose, parent, exfu version from latest), and adds sane-default content for selected folder-types.

### 5. Integration with install conversation

The install skill calls scope-setup when:
- Creating the user/ scope (first install)
- Creating the user's first working scope ("what are you working on right now?")
- The user asks to add a scope later

The scope-setup skill is also available standalone for organic use: "I've got a new client, create a scope for them."

---

## Acceptance criteria

1. Skill can create a complete, correctly-formed scope through guided conversation
2. Sane defaults for todo, reminders, inbox are ready to use out of the box
3. Pointer pattern works for external tool integration
4. Context and ontology folders are always created
5. The skill uses scope templates and fills in frontmatter correctly
6. Install conversations can delegate to this skill
7. The skill works both for first-time install and organic scope creation

---

## Files to create

- `plugin/src/shared/skills/scope-setup/SKILL.md`
- `plugin/src/shared/skills/scope-setup/` (skill content)
- Sane default templates in `plugin/src/shared/substrate/templates/` (todo-default.md, reminders-default.md, inbox-default.md)

---

## Where this plan lives

- This file: `plugin/planning/T3-scope-setup-skill.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
