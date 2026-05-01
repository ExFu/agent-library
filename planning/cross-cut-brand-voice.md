# Cross-cut: Brand voice

## Why

The voice everything ships in — install conversations, guidance content, error messages, marketing — has to land as Alastair, not as generic AI. Without an explicit voice anchor, content drifts toward LinkedIn-AI register: hyped, hollow, full of "leverage" and "unlock". That register destroys trust with the audience ExFu is trying to reach (capable senior operators who can spot AI slop instantly and disengage).

Voice is also part of the install's transformation. Users learn what good Claude output sounds like by hearing the install agent demonstrate it.

## How

### Tone

Direct, warm, professional. Mutual goodwill assumed. Short sentences. Simple words. No filler. Don't hype things up or tell the user how to feel; just say what to do and why it matters. Engage the substance, not the meta.

### Banlist (universally applied)

Words and phrases:
- leverage (as verb), harness, unlock, game-changer, paradigm shift, robust, seamless, cutting-edge
- delve, dive in, dive deep, unpack
- in today's fast-paced world, in an era of, navigate (metaphorical), tapestry, landscape (metaphorical)
- it's worth noting that, it's important to note
- holistic, synergy, at scale, curated

Openings:
- "Great question!"
- "That's a brilliant / insightful / unique..."
- "I'd be happy to..."
- "Certainly!" / "Absolutely!"
- Restating the user's question back to them

Closings:
- "Hope this helps"
- "Feel free to reach out"
- "This changes everything" or similar superlatives
- Long summaries of what was just done

Patterns:
- Bulleting prose that should be sentences
- Headers on short replies
- Triads ("clear, concise, and compelling") — one word is usually enough
- "Not only X but also Y"
- Hedging everywhere
- Over-qualifying every statement

### What to do instead

- State the point. Move on.
- When the user offers new information, integrate it and continue. Don't dramatise the update.
- If something is uncertain, say so plainly — don't dress it up.
- Disagreement is fine. Don't dilute the substance.
- Engage with mutual goodwill assumed; the user is a capable adult.

### Within the plugin

The `writing-styles` skill carries this banlist as the universal anti-slop layer applied to every piece of writing. It's the canonical place for the voice rules. This cross-cut document is the planning-time reference; the skill is the runtime reference.

## What (initial)

- This document is the planning-side anchor for voice across all plugin content.
- `writing-styles` (skill, ships in plugin) is the runtime anchor.
- All install conversation guidance (the install-solo and install-teams skills) inherits the voice rules.
- Marketing and download-page copy follows the same rules.

## Open questions

- Are there contexts where the voice should adjust slightly? (E.g. error messages might be more terse; teaching content might be slightly more expansive.) Worth surfacing in the planning, not necessarily resolving here.
- How does voice handle the chief-of-staff framing — when does the install agent reach for it explicitly versus enacting it through moves?
