---
name: setup-inbox
description: First-time setup for the user's personal inbox skill. Run this when the user wants to set up quick-capture for the first time — "set me up with an inbox", "give me a place to capture stuff", "I keep losing thoughts, fix that", "set up quick-capture", or any first-time inbox setup intent. Not for ongoing capture or inbox review (those are handled by the user's personal inbox skill, typically named after them, e.g. `al-inbox`).
---

# Setup — Inbox

## Why this exists

The inbox is a quick-capture log: a place to dump thoughts, links, and loose items without deciding where they belong yet. The problem it solves is simple — the moment you have to think "where does this go?", you lose the thought.

This setup skill is a one-shot conversation. By the end you'll have a personal `<username>-inbox` skill installed in your Claude. That skill knows where your inbox file lives and how you prefer to use it. After that, you never need to run this setup again. All ongoing inbox operations — capturing, reviewing, processing — happen through your personal skill.

---

## The intake

Walk through these questions in conversation. Don't ask them all at once as a form. Pick up the thread naturally.

### Where the inbox file lives

Ask the user where they want their inbox file. The standard location is `databases/inbox/inbox.md` inside their substrate. If they've set up a substrate already, confirm that's where to put it. If they want it somewhere else — a different folder name, a different path — capture that instead.

Note any deviation from the standard location. The generated skill will hard-code the actual path so the user doesn't have to remember it.

### Format preferences

The default format is a flat markdown log, newest entries at the top, each line timestamped:

```
2026-04-20 11:02 — remember to check if Sam's responded about the partnership
2026-04-19 22:47 — https://example.com/article — read later, thinking about onboarding
```

Ask if the default works or if they want something different. Most users are fine with it; the point is to note any strong preferences (e.g. bullet list instead of plain lines, no timestamps, or a specific date format).

### Review cadence

Ask how often they expect to process their inbox. Weekly is the minimum recommended. Some people like to clear it daily; others batch it monthly. This preference goes into the conventions section of their skill — it's a nudge, not enforcement.

### Anything else

Any other preferences or quirks? For example:
- Do they want the file created immediately, or only on first capture?
- Is there a specific reminder to process the inbox they want set up alongside?

Keep this brief. If nothing else comes up, move on.

---

## Generate the per-user skill

Once you have the intake answers:

### 1. Determine the username

Read `user/context/about-me.md` from the user's substrate. Look for their name. If the file exists and a name is clear, default to first-name-lowercase as the username (e.g. "Alastair" becomes `al`, or if the about-me spells out a preferred handle, use that). If the name is ambiguous or the file doesn't exist, ask: "What should we call your inbox skill? Something like `al-inbox` or `sarah-inbox` — first name or nickname is fine."

The per-user skill will be named `<username>-inbox` and its frontmatter `name:` will reflect this.

### 2. Read the template

Read the inbox template from `${CLAUDE_PLUGIN_ROOT}/templates/inbox-template.md`. This contains all the operational logic for the inbox skill. Your job is to fill in the placeholders with what the intake captured:

- `{{username}}` → the resolved username
- `{{inbox_file_path}}` → the confirmed file path (e.g. `databases/inbox/inbox.md`)
- `{{date_example}}`, `{{date_example_2}}`, `{{date_example_3}}` → sample dates (use recent plausible dates, not today's exact date)
- `{{conventions}}` → any custom preferences noted during intake, phrased as brief bullet points. If nothing unusual, leave this as an empty placeholder so the template's default conventions apply.

### 3. Package and present

Use `skill-packaging` to package the filled-in template as a `.skill` file named `<username>-inbox`. Present the install link to the user. Walk them through installing it if this is their first time with skill packaging.

---

## Hand-off

Once the skill is installed, this setup is done. Going forward:

- Capturing thoughts ("save this", "add to inbox", "don't lose that") → `<username>-inbox`
- Reviewing what's piled up ("what's in my inbox", "process inbox") → `<username>-inbox`
- Session-start inbox count (called by substrate) → `<username>-inbox`

If the user ever wants a fresh setup — different file location, different preferences — they can re-run `setup-inbox`. It will overwrite the generated skill. Their existing inbox file and its contents are never touched.

---

## Dependencies

- `skill-packaging` — used to package and present the generated skill.
- `exfu-library` skill calls the user's inbox skill (by name) at session start if it is installed.
- The template at `${CLAUDE_PLUGIN_ROOT}/templates/inbox-template.md` contains the operational logic.
