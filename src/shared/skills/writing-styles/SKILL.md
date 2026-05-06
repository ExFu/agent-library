---
name: writing-styles
description: Write and edit in the user's voice, not Claude's defaults. Use whenever producing written output for or on behalf of the user. Runs a first-time intake to extract the user's voice into a profile if one doesn't exist yet, then applies that profile plus a universal anti-slop layer to every subsequent piece of writing. Triggers on "write this for me", "draft an email to X", "can you sound more like me?", "this doesn't sound right, fix it", "edit this in my style", "write a message to X", "help me reply to this", or any time the user asks Claude to produce or improve text that will go out under their name.
---

# Writing Styles

Write in the user's voice, not Claude's. Two parts: a personal profile extracted once and reused, plus a universal anti-slop layer applied on top every time.

## First use: run the intake

If `context/me/writing-style.md` doesn't exist, run the intake before producing any writing for this user.

1. Ask them for three samples of their own writing. A range is useful — something casual, something professional, something longer.
2. Read carefully. Pay attention to: sentence length and rhythm; vocabulary (words they use, words they avoid); openings and closings; register shifts between contexts; punctuation preferences (semicolons, exclamation marks); hedging vs directness; humour; how they handle disagreement.
3. Write a profile at `context/me/writing-style.md` using the template below.
4. Confirm with one line: "Profile saved. I'll use this whenever I'm writing for you. Tell me when it's wrong — the profile improves over time."

Don't skip the intake. Writing in the wrong voice is worse than not writing — the user (and their readers) spot AI voice instantly and lose trust.

## Ongoing: apply the profile

Before producing any written output:

1. Read `context/me/writing-style.md`
2. Draft using the profile
3. Apply the anti-slop layer below
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

## Profile template

Use this shape when writing `context/me/writing-style.md`:

```
# Writing style — [user name]

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
- Specific words, phrases, or patterns they've told me they dislike

## Samples
Two or three short excerpts from the intake — for reference when drafting.

## Changelog
- YYYY-MM-DD v1: Initial intake.
```

## Drafting vs editing

- **Drafting from scratch**: apply profile + anti-slop fully.
- **Editing their text**: preserve voice, fix the specific thing asked about, don't rewrite for flow unless they asked.
- **Writing as them** (email replies, posts, messages): first person, their voice. Don't add caveats or hedges they wouldn't add.
- **Writing about them** (bios, introductions): use their voice if the context is their own platform; adjust if it's third-party.

## Iteration

When the user pushes back ("I wouldn't say it like that", "too formal", "you still sound like AI"), update the profile and add a changelog entry. If a pattern keeps coming up, add it to the profile's hate list. The profile grows — that's the point.
