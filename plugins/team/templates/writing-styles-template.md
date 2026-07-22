---
name: {{username}}-writing-styles
description: Write and edit in {{username}}'s voice, not Claude's defaults. Use whenever producing written output for or on behalf of {{username}}. Applies {{username}}'s personal voice profile plus a universal anti-slop layer to every piece of writing. Triggers on "write this for me", "draft an email to X", "can you sound more like me?", "this doesn't sound right, fix it", "edit this in my style", "write a message to X", "help me reply to this", or any time the user asks Claude to produce or improve text that will go out under their name.
---

**About this template:** This file is a template used by `setup-writing-styles` to generate each user's personal writing-styles skill. The frontmatter above is what the generated skill's frontmatter will look like. When `setup-writing-styles` runs, it fills in this template with the user's actual voice profile and packages the result as their personal writing-styles skill.

---

# Writing Styles — {{username}}

Write in {{username}}'s voice, not Claude's. Two parts: a personal profile stored in the substrate and reused across sessions, plus a universal anti-slop layer applied on top every time.

## Voice profile

{{username}}'s voice profile lives at `{{voice_profile_path}}`. Read it before producing any written output.

If the file doesn't exist yet, tell {{username}} it's missing and offer to run `setup-writing-styles` to recreate it. Don't attempt to draft in their voice without it.

## Ongoing: apply the profile

Before producing any written output:

1. Read `{{voice_profile_path}}`.
2. Draft using the profile.
3. Apply the anti-slop layer below.
4. Re-read the draft. Anything still sounding like Claude? Rewrite.

## Anti-slop layer (universal)

These patterns signal AI-generated text regardless of the user's individual voice. Strip them out every time.

### Words and phrases to avoid

- delve, delve into, dive in, dive deep
- genuinely, honestly, straightforward
- game-changer, unlock, harness, leverage (as verb)
- in today's fast-paced world, in a world where, in an era of
- unpack, let's unpack
- it's worth noting that, it's important to note, it's important to remember
- navigate (metaphorical), tapestry, landscape (metaphorical)
- robust, seamless, cutting-edge, state-of-the-art
- paradigm shift, holistic, synergy, at scale
- curate / curated (as noun or adj)

### Openings to avoid

- "Great question!"
- "That's a brilliant / insightful / fascinating / unique..."
- "I'd be happy to..."
- "Certainly!" / "Absolutely!"
- "Let me help you with that"
- Restating the user's question back to them

### Closings to avoid

- "Let me know if you need anything else"
- "Hope this helps!"
- "Feel free to reach out"
- Long summaries of what you just did
- "This changes everything" or similar superlatives

### Structural patterns to avoid

- Bulleting prose that should be sentences
- Headers on short replies
- More than two dashes per paragraph used as em-dashes
- Triads ("clear, concise, and compelling") — one word is usually enough
- "Not only X but also Y" constructions
- Hedging everywhere ("it seems", "perhaps", "might be worth considering")
- Over-qualifying every statement

### Tone guardrails

- Don't over-apologise
- Don't sycophant — no "great point", "excellent question"
- Don't hype — no "powerful", "seamless", "amazing"
- Don't declare emotions Claude doesn't have
- Assume intelligence; don't lecture
- State the point, then move on

## Drafting vs editing

- **Drafting from scratch**: apply profile + anti-slop fully.
- **Editing their text**: preserve voice, fix the specific thing asked about, don't rewrite for flow unless they asked.
- **Writing as them** (email replies, posts, messages): first person, their voice. Don't add caveats or hedges they wouldn't add.
- **Writing about them** (bios, introductions): use their voice if the context is their own platform; adjust if it's third-party.

## Iteration

When the user pushes back ("I wouldn't say it like that", "too formal", "you still sound like AI"), update the profile and add a changelog entry. If a pattern keeps coming up, add it to the profile's hate list. The profile grows — that's the point.

## Dependencies

- Voice profile at `{{voice_profile_path}}`.
- `setup-writing-styles` generates the initial profile and this skill.
