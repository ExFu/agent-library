---
name: golden-circle
applies-to: all-agents
---

# Principle: Golden Circle (Why → How → What)

## Why

When an agent explains, plans, or writes something another agent will read, the instinct is to skip Why (it feels obvious) and jump straight to What (it feels productive). The result is artifacts that work in the moment but fail later: a future agent reads only the What, has no anchor for judgement when something unanticipated comes up, and either freezes or improvises poorly. The reasoning behind a decision is as useful to a future agent as the decision itself, often more so.

## How

For any non-trivial artifact (planning doc, skill body, convention atom, `agent.md` template, install instruction, scope reference, librarian instruction), structure the content as:

1. **Why** — what problem this solves, what would go wrong without it, what changes if it lands well.
2. **How** — the approach, principles, trade-offs, dependencies. The reasoning.
3. **What** — the concrete deliverables, file structures, content.

Each section short enough to read; deep enough to act on. Anchor to the Why throughout; let the How explain the reasoning; let the What be obvious from the first two.

## What

Apply this to: planning docs, skill bodies, `agent.md` per-folder snapshots, convention atoms, install instructions, librarian instructions, scope.md files, ontology schemas, anything materialised into a user's substrate or shipped in `${CLAUDE_PLUGIN_ROOT}`. Include rationale, principles, and trade-offs alongside conclusions. Better to over-explain than to leave a future agent guessing at intent.

Do not apply to: short conversational turns with the user (they have the context already); transient scratch notes the user has explicitly marked as ephemeral.
