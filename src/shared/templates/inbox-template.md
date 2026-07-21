---
name: {{username}}-inbox
description: Quick-capture log for {{username}}. Use when {{username}} wants to dump something out of their head without sorting it, when they ask what's piled up in their inbox, or when they want to process and sort captured items. Also called by the exfu-library skill at session start to flag pending items. Triggers on "save this", "capture that", "hold onto this", "jot this down for me", "I want to come back to this", "don't lose this thought", "this is important but I don't know where it goes yet", "what's in my inbox", "process my inbox", or any time the user wants frictionless capture of something that doesn't have a home yet.
---

**About this template:** This file is a template used by `setup-inbox` to generate each user's personal inbox skill. The frontmatter above is what the generated skill's frontmatter will look like. When `setup-inbox` runs, it fills in this template with the user's actual preferences and packages the result as their personal inbox skill.

---

# Inbox — {{username}}

Quick-capture log. Things to dump out of your head without deciding where they belong.

Distinct from reminders. Reminders are time-triggered ("ping me about this on [date]"). Inbox is place-agnostic quick capture ("don't let this thought fall out").

## Where the data lives

{{inbox_file_path}} — a plain markdown log, newest entries at the top, each timestamped.

If the file or the folder doesn't exist, create them on first use. Create a README alongside the data file describing what the folder is for. Then proceed.

## File format

```
{{date_example}} 11:02 — remember to check if Sam's responded about the partnership
{{date_example_2}} 09:14 — idea: offer ExFu as a monthly retainer, not just one-off
{{date_example_3}} 22:47 — https://example.com/article — read later, thinking about onboarding
```

Timestamp: `YYYY-MM-DD HH:MM` in the user's local time.

## Actions

### Capture

Triggers: "save this", "add to inbox", "don't lose that", "capture this"

1. Get a timestamp (user's local time).
2. Prepend a new line to the inbox file.
3. Confirm briefly: "Saved to inbox." Keep it short — capture should feel frictionless.

### Review / process

Triggers: "what's in my inbox", "process inbox", "sort my inbox", "clear the inbox"

1. Read the file.
2. For each entry, help the user decide where it belongs:
   - **Reminder?** → hand to the user's reminders skill ({{username}}-reminders if installed), remove from inbox.
   - **Task?** → add to their task manager (via MCP if connected; otherwise flag for them), remove from inbox.
   - **Scope-specific thought?** → move to the relevant `scopes/[name]/` folder, remove from inbox.
   - **Draft or working file?** → move to `scratch/`, remove from inbox.
   - **Noise?** → remove.
   - **Actionable right now?** → do it, then remove.
3. Save remaining items (if any).

### Count (called on session load by `exfu-library`)

1. Read the file.
2. Count non-empty lines.
3. If 0, say nothing.
4. If >0, mention briefly: "Inbox has [n] items. Want to process them?"
5. Don't force processing — just flag. Capture without friction matters more than a clean inbox.

## Conventions

{{conventions}}

- Newest first.
- No categorisation in the inbox itself — the point is frictionless dump.
- Process weekly at minimum; longer than that and it becomes a junk drawer.
- If a captured item is obviously actionable right now (quick reply, one-click check), do it rather than file it.
- Keep the file flat. Don't subdivide. Inbox is a single stream.

## Dependencies

- `exfu-library` skill delegates to this skill on session load.
- The processing step may hand items to `{{username}}-reminders` or the user's task manager MCP.
