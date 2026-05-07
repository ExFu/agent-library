---
name: setup-reminders
description: First-time setup for the user's personal reminders skill. Run this when the user wants to set up reminders for the first time — "set up reminders for me", "give me a way to nudge myself later", "I keep forgetting things, fix that", or any first-time reminder setup intent. Not for creating individual reminders or checking what's due (those are handled by the user's personal reminders skill, typically named after them, e.g. `al-reminders`).
---

# Setup — Reminders

## Why this exists

Reminders are Claude's own nudges to the user — separate from whatever task manager they actually use. The problem they solve: "remind me to check on this next Monday" or "don't let that slip" — small time-triggered flags that live inside Claude's context, not in an external app.

This setup skill is a one-shot conversation. By the end you'll have a personal `<username>-reminders` skill installed in your Claude. That skill knows where your reminders file lives and how you prefer to use it. After that, you never need to run this setup again. All ongoing reminder operations — creating, surfacing, completing, snoozing — happen through your personal skill.

---

## The intake

Walk through these questions in conversation. Don't present them as a list. Pick up the thread naturally based on what the user says.

### Where the reminders file lives

Ask the user where they want their reminders file. The standard location is `databases/reminders/reminders.md` inside their substrate. If they've set up a substrate already, confirm that's where to put it. If they want it somewhere else, capture that instead.

Note any deviation from the standard location. The generated skill will hard-code the actual path.

### Default reminder format

The default format is a flat markdown checklist:

```
- [ ] 2026-04-21 — Ask me if I still want to pursue the Acme deal.
- [x] 2026-04-15 — (done 2026-04-14) Tax filing deadline.
```

Ask if this works or if they have strong preferences. Most users are fine with the default. If they want a different date format or additional context fields, note that.

### Recurring reminders

Ask if they expect to use recurring reminders — things like "every Monday, remind me to check X" or "first of each month, surface Y". The default behaviour is no built-in recurrence; the user re-sets a reminder when they complete the current one. If they want the skill to handle recurring patterns explicitly, note this so it can be added to the conventions section.

### Surface on load behaviour

Reminders surface at session start if anything is due or overdue. Ask the user if they want to adjust this:
- Default: surface due/overdue only, silently skip if nothing is due.
- Some users prefer: "always tell me how many reminders I have, even if nothing's due."
- Some prefer: "only surface if something is overdue by more than a day" (to reduce noise on tight deadlines they're already tracking).

Capture the preference. If they're fine with the default, move on.

### Anything else

Any other preferences? Keep this brief. If nothing comes up, move on.

---

## Generate the per-user skill

Once you have the intake answers:

### 1. Determine the username

Read `context/me/about.md` from the user's substrate. Look for their name. Default to first-name-lowercase as the username (e.g. "Alastair" becomes `al`, or use whatever handle is clear from the file). If the name is ambiguous or the file doesn't exist, ask: "What should we call your reminders skill? Something like `al-reminders` or `sarah-reminders` — first name or nickname is fine."

The per-user skill will be named `<username>-reminders`.

### 2. Read the template

Read the reminders template from `${CLAUDE_PLUGIN_ROOT}/templates/reminders-template.md`. Fill in the placeholders with what the intake captured:

- `{{username}}` → the resolved username
- `{{reminders_file_path}}` → the confirmed file path (e.g. `databases/reminders/reminders.md`)
- `{{conventions}}` → any custom preferences from the intake, phrased as brief bullet points. If nothing unusual, leave as an empty placeholder so the template's default conventions apply.

### 3. Package and present

Use `skill-packaging` to package the filled-in template as a `.skill` file named `<username>-reminders`. Present the install link to the user. Walk them through installing it if this is their first time with skill packaging.

---

## Hand-off

Once the skill is installed, this setup is done. Going forward:

- Creating reminders ("remind me to X on Y", "don't let me forget Z") → `<username>-reminders`
- Session-start check for due/overdue reminders (called by substrate) → `<username>-reminders`
- Completing or snoozing reminders → `<username>-reminders`

If the user ever wants a fresh setup — different file location, different surface-on-load behaviour — they can re-run `setup-reminders`. It will overwrite the generated skill. Their existing reminders file and its contents are never touched.

---

## Dependencies

- `skill-packaging` — used to package and present the generated skill.
- `substrate` skill calls the user's reminders skill (by name) at session start if it is installed.
- The template at `${CLAUDE_PLUGIN_ROOT}/templates/reminders-template.md` contains the operational logic.
