# Cross-cut: Future explorations

## Why

Some ideas are worth capturing now even though they're out of scope for v1, because they shape architectural decisions ("don't build something that locks this out") and because they're worth coming back to when the ecosystem catches up. Without a place to capture them, they get lost between conversations.

This file is the parking lot. Everything here is *deliberately not* being planned in detail right now. It's a notes-to-future-self about directions worth exploring.

## How

Anything that comes up in conversation, planning, or implementation that:
- Isn't urgent enough to plan in detail now
- Shouldn't be lost
- Might shape an architectural decision currently being made
- Will likely come up again with a future client or as the ecosystem evolves

…goes here, with a short note on why it might matter and what would prompt a serious look. As any item reaches the threshold for serious work, it gets promoted to a proper T2 or cross-cut and removed from this file.

## What (initial)

### Graph and Obsidian-style concepts

The current substrate doesn't have a graph layer or Obsidian-style backlinks. These are powerful for navigating an evolving knowledge base — particularly for users who already use Obsidian or similar tools.

Why it matters now: the substrate's file conventions (markdown with front-matter, directory structure, README dependency declarations) don't preclude adding a graph view later. An Obsidian vault can sit on top of the substrate and treat it as raw material. Worth not making structural choices that fight this.

Trigger to revisit: a client comes in already using Obsidian and wants their substrate to play nicely with their vault. Or Anthropic surfaces graph-style navigation as a first-class feature.

### Agentic workflows beyond personal

The plugins target Cowork agents — knowledge-worker, desktop, conversational. Custom hosted agents (workflow agents, functional agents, devops agents) are a bigger conversation, more naturally a Lope engagement. But ExFu users will increasingly bump into needing them as their work grows.

Worth thinking about: what's the right way for a Cowork-substrate user to discover that they need a custom hosted agent, and what's the handoff to "you should talk to Lope about this"?

### Multi-substrate users

A user might have multiple substrates over time — personal, work-team, side-venture-team, client-project. Each is its own installation. How does that work cleanly?

Probably: each substrate is a separate folder root, the user's `wow` skill picks up which root is active for the current conversation (via Global Instructions or a session marker). Out of scope for v1 — both plugins assume one substrate per user — but worth not architecturally precluding.

### Claude memory and Anthropic's own memory features

Anthropic is actively shipping memory features (Claude Projects memory, Dispatch memory, etc.). Some of what the substrate does will become native over time. The substrate is positioned to absorb or hand off to those features as they mature.

Watch list. When a native feature reaches parity with a substrate function, decide whether to swap it in.

### Self-evolving substrate

Long-term: a substrate that recommends its own structural improvements based on patterns Claude observes (e.g. "you keep capturing X in scratch — should I promote it to a database or scope?"). Currently the user does this manually. The hooks are there for it eventually.

### Plugin ecosystem reciprocity

If well-respected community plugins (superpowers, oh-my-claude) overlap with ExFu in interesting ways, there may be reciprocity opportunities — they reference us, we reference them, possibly shared conventions. Out of scope for v1 but worth not adopting conventions that fight this.

## Open questions

- What's the right cadence for revisiting this file? Probably per-major-version of the plugins.
- When does an item graduate from this file to actual planning? When a client conversation makes it concrete, or when the ecosystem catches up — whichever comes first.
