# T3 -- Dashboard workspace views

The "what's on my plate?" view: todo, reminders, and inbox content across scopes, rendered scannable. The largest gap between v1 and the milestone's bar.

**Parents:** `T2-exfu-dashboard.md` (domain), `M2.1-exfu-dashboard.md` (milestone)
**Prerequisites:** T3-dashboard-generation (pipeline), and **written sane-default formats** for todo/reminders/inbox -- see "The adaptor strategy" below. T3-scope-setup-skill creates folders following those formats, so setup, ontology, and rendering must agree on file shapes.
**Status:** v1 exists but falls short -- it dumps raw file text into the page, YAML frontmatter included. A user currently sees `type: personal-context` and `last-updated:` as literal text. This plan specifies the rendering layer that turns collected content into something a person scans in seconds.

---

## Why

The milestone's bar is "a summary of their todos, reminders, and inbox items across scopes... scannable in seconds". Raw file dumps fail that bar twice: frontmatter is plumbing a user should never see, and unrendered markdown makes the user do the parsing the dashboard exists to do.

This view is also the dashboard's daily-return reason. The map and librarian views change slowly; the workspace is why someone opens the file tomorrow. Rendering quality here decides whether the dashboard becomes a habit or a curiosity.

The boundary stays firm: read-only summaries. "Here's what's on your plate", never "manage your tasks here" -- management lives in the conversation and in the external tools the pointers name.

---

## How -- the adaptor strategy

The dashboard cannot render arbitrary markdown well, and shouldn't try. The architecture is a narrow waist:

1. **A normalised workspace shape** is the contract: a task is `{text, done, group}`, a reminder is `{text, date?, group}`, an inbox item is `{title, summary, age, status?}`. The renderer only ever sees this shape.
2. **Sane-default parsers ship with the dashboard.** Folders that follow the sane-default formats (the common case -- scope-setup creates them) parse to the normalised shape with no configuration.
3. **Pointer folders** render as chips (see below); nothing to parse.
4. **Deviating scopes provide a feed, not a parser.** A scope whose todo or reminders live in some other shape materialises a normalised feed file (e.g. `<scope>/visualisations/workspace-feed.json`), typically written by one of its own scheduled jobs. The dashboard consumes the feed verbatim and skips its own parsing for that folder. Pluggable data, no pluggable code -- the generator never executes scope-provided logic.

**The prerequisite, mostly landed (M2 conventions revision, commit 2d592bb):** the sane defaults now exist as templates at `templates/defaults/` -- todo is markdown checkboxes under "## Active tasks" with completed tasks moved to a sibling `done.md`; reminders are date-plus-note entries under "## Upcoming reminders" with past ones moved to `archive.md`; inbox is one item per entry (or per sibling file). The parsers target exactly these shapes. What remains is pinning the grammar the parsers rely on -- the task-line form and especially the reminder date format -- as one or two lines in those templates (and, if warranted, the matching `ontology.md` anchors), coordinated with whoever holds the convention base. Loose-format files still degrade gracefully to the markdown-rendering layer below; they never error.

---

## What to build

### 1. Shared rendering rules (all three sections)

- **Frontmatter never renders.** Strip YAML frontmatter from every file before rendering. Selected fields may *inform* rendering (an inbox item's triage status, a reminder's date); the block itself is invisible.
- **Minimal markdown, stdlib only.** A small renderer for the shapes the sane defaults produce: headings become section labels, `- [ ]` / `- [x]` become styled checkboxes, bullet lists become lists, bold renders bold. Everything else renders as plain text. No external markdown library.
- **Scope grouping stays** (v1): items group under their scope's name, in map order.
- **Caps with honesty.** Long content truncates at a sane per-folder limit with "... and N more" -- never a silent cut, never a wall of text.
- **Classification comes from the index.** Data-vs-pointer status is read from `index.json`, not re-detected here (see T3-dashboard-generation, decision 3).

### 2. Todo

- **Pointer folders** (the common case -- e.g. todo tracked in ClickUp): render a labelled chip ("Managed in ClickUp") plus the one descriptive line from the folder's agent.md. If that line contains a URL, render it as a link; never fabricate one. This settles the T2's open question on pointer rendering: chip + source line, link only when the substrate provides it.
- **Data folders:** render task lines as a checklist; open tasks prominent, done tasks dimmed. Headings in the file become group labels within the scope.

### 3. Reminders

- Strip frontmatter, render the body per the shared rules.
- Where entries carry parseable dates (ISO dates, or a `due:`-style key the sane defaults define), group into **overdue** (red accent) and **coming up** (amber accent, next 7 days), with the rest under their own headings as written.
- Date parsing is best-effort: an unparseable reminder renders as ordinary content, never an error. The renderer must not impose a stricter format than the sane defaults promise.

### 4. Inbox

- One file = one item: filename (de-slugged) as the title, first non-heading line as the summary, file age as a quiet timestamp.
- If the inbox-triage librarian has recorded a status in the item's frontmatter, render it as a small chip (e.g. "waiting on you").
- Old items read as gently stale, not alarming -- the inbox invites triage, it doesn't nag.

### 5. Empty and missing states (v1, keep)

Sections with no content collapse to a single friendly line; a substrate with no workspace content at all keeps the existing "Nothing in your workspace yet" state. Missing folders are simply absent, per the pipeline's graceful-degradation contract.

---

## Acceptance criteria

1. No YAML frontmatter is visible anywhere in the rendered dashboard.
2. Checkbox tasks render as styled checklists; done items are visibly dimmed.
3. A pointer todo folder shows a "Managed in ..." chip and the substrate's own descriptive line; a URL in that line is clickable.
4. Reminders with parseable dates group into overdue and coming-up; unparseable reminders still render cleanly.
5. Inbox items show title, summary, and age without exposing raw markdown.
6. Long content truncates with an explicit "and N more", never silently.
7. The sane-default formats for todo, reminders, and inbox are written down in the core ontology, and the shipped parsers parse exactly those formats.
8. A scope providing a normalised `workspace-feed.json` sees its content rendered with no dashboard code changes, and the generator executes no scope-provided logic.
9. Rendered against Al's live substrate, each section is scannable in seconds by someone who has never seen the files behind it.

---

## Files to create/modify

- Modify: `plugin/src/shared/scheduled-tasks/scheduled-agents/dashboard-generator.py` (`collect_workspace_items`, `render_workspace_folder`, `render_workspace_views`, new minimal markdown renderer, CSS)
- Possibly modify: `plugin/src/shared/substrate/templates/defaults/todo-default.md`, `reminders-default.md`, `inbox-default.md` (pin the task-line and reminder-date grammar the parsers rely on)

Paths as of commit 2d592bb (the M2 conventions revision).

---

## Where this plan lives

- This file: `plugin/planning/T3-dashboard-workspace-views.md`
- Domain: `plugin/planning/T2-exfu-dashboard.md`
- Milestone: `plugin/planning/M2.1-exfu-dashboard.md`
- Pipeline: `T3-dashboard-generation.md`
