---
name: setup-writing-styles
description: First-time setup for the user's personal writing-styles skill. Run this when the user wants to teach Claude their writing voice for the first time — "teach Claude my writing voice", "set up writing styles", "make Claude sound like me", "I want Claude to write in my style", or any first-time voice intake intent. Not for ongoing writing or editing tasks (those are handled by the user's personal writing-styles skill, typically named after them, e.g. `al-writing-styles`).
---

# Setup — Writing Styles

## Why this exists

Writing in someone else's voice is hard. Claude's default voice is recognisably Claude's — competent, a bit neutral, and nothing like most people's actual writing. The way to fix this is a one-time intake: collect samples of the user's real writing, extract the patterns that make it theirs, and store them as a voice profile.

This setup skill runs that intake. By the end you'll have a personal `<username>-writing-styles` skill installed in your Claude. That skill carries your voice profile and applies it whenever you ask Claude to write or edit on your behalf. After that, you never need to run this setup again unless you want a refresh.

---

## The intake

This is the core of the setup. Take your time with it.

### Step 1 — Collect writing samples

Ask the user for three samples of their own writing. A range is what you're after:

- Something casual: a Slack message, a text, an informal email.
- Something professional: a formal email, a report section, a proposal.
- Something longer: a document intro, a memo, a post they've written.

If they only have two, that's fine. If they offer more than three, take up to five — more data helps. What you need is variety. Samples from only one register will produce a partial profile.

Tell them why: "The more range you give me, the more accurately I can capture your voice across different situations."

### Step 2 — Read carefully

Once you have the samples, analyse them before writing anything. Look for:

**Sentence rhythm.** Typical length. Variation — do they tend towards staccato bursts or longer flowing sentences? Do they mix short and long deliberately?

**Vocabulary.** Words they reach for repeatedly. Words they visibly avoid. Technical vocabulary vs plain language. Level of formality in word choice.

**Openings and closings.** How do they start messages and documents? How do they close them? Do they use pleasantries, or get straight to the point?

**Register shifts.** How does their voice change between casual and professional contexts? What stays the same regardless?

**Punctuation preferences.** Do they use semicolons? Exclamation marks? Em-dashes? Lots of parentheses? Are they sparing or generous with punctuation?

**Hedging vs directness.** Do they qualify statements frequently ("I think", "it seems like", "perhaps") or state things plainly?

**Humour.** Dry? Absent? Warm? Self-deprecating?

**Disagreement.** How do they push back or decline? Softly, directly, via reframe?

### Step 3 — Confirm your read

Before writing the profile, summarise your observations in a few sentences and check your understanding. Example: "Here's what I'm seeing: you write in short, direct sentences, especially in professional contexts — but in casual messages you loosen up and occasionally use run-ons for effect. You avoid exclamation marks almost entirely but you use parentheses a lot. Does that sound right?"

This gives the user a chance to correct a misread before it gets baked in. One round of confirmation is enough — don't turn it into a workshop.

### Step 4 — Write the voice profile

Write the profile at `user/context/writing-style.md` in the user's substrate, using this shape:

```
# Writing style — [username]

version: 1
last updated: YYYY-MM-DD

## Voice
One paragraph describing how they sound — the core feel of their writing.

## Sentence patterns
- Typical length
- Rhythm (staccato / flowing / varied)
- Punctuation preferences

## Vocabulary
- Words and phrases they use
- Words and phrases they avoid

## Register
- When they're formal vs casual
- How they open messages
- How they close messages
- How they handle disagreement

## Hate list
- Specific words, phrases, or patterns they've flagged as disliked (or that clearly don't appear in their writing)

## Samples
Two or three short excerpts from the intake — for reference when drafting.

## Changelog
- YYYY-MM-DD v1: Initial intake from [n] samples.
```

Be specific. "Short sentences" is less useful than "typically 10-15 words, rarely over 25." "Avoids jargon" is less useful than "plain language throughout; when technical terms are needed, defined immediately after." The profile improves with specificity.

---

## Generate the per-user skill

Once the voice profile is written:

### 1. Determine the username

Read `user/context/about-me.md` from the user's substrate. Look for their name. Default to first-name-lowercase as the username (e.g. "Alastair" becomes `al`). If the name is ambiguous or the file doesn't exist, ask: "What should we call your writing-styles skill? Something like `al-writing-styles` or `sarah-writing-styles` — first name or nickname is fine."

The per-user skill will be named `<username>-writing-styles`.

### 2. Read the template

Read the writing-styles template from `${CLAUDE_PLUGIN_ROOT}/templates/writing-styles-template.md`. Fill in the placeholders:

- `{{username}}` → the resolved username
- `{{voice_profile_path}}` → the path where you wrote the voice profile (e.g. `user/context/writing-style.md`)

The template contains the anti-slop layer and the full operational logic for the per-user skill. You are not reproducing that content here — you are pointing the template at the right profile location and packaging it.

### 3. Package and present

Use `skill-packaging` to package the filled-in template as a `.skill` file named `<username>-writing-styles`. Present the install link to the user.

---

## Hand-off

Once the skill is installed, this setup is done. Going forward:

- Writing or editing on the user's behalf → `<username>-writing-styles`
- Updating the voice profile when the user pushes back or refines → `<username>-writing-styles` (the skill handles profile iteration)

If the user ever wants a full re-intake — new samples, fresh profile — they can re-run `setup-writing-styles`. The old profile at `user/context/writing-style.md` will be overwritten. The generated skill will be replaced.

---

## Notes on the intake quality

The profile is only as good as the samples. If the user gives you very short samples, or all from the same context, flag it: "These samples are all from [one context] — if you have anything from a different register, it would help me capture your voice more accurately."

The profile will improve over time through the per-user skill's iteration loop. The intake is a starting point, not a definitive statement.

---

## Dependencies

- `skill-packaging` — used to package and present the generated skill.
- The profile lives at `user/context/writing-style.md` in the user's substrate.
- The template at `${CLAUDE_PLUGIN_ROOT}/templates/writing-styles-template.md` contains the operational logic for the per-user skill.
