# Cross-cut: Planning approach

## Why

The way we plan this work is itself a teachable artefact. It applies a golden-circle frame (Why → How → What) and a tiered structure (T1 → T2 → T3) that scales from "everyone needs to grok this" through "parallelisable workstreams" to "implementation-ready specs". The same approach is useful for ExFu clients when they're shaping their own AI behaviours, building skills, or planning agentic work — so it should also ship as guidance inside the plugin's `guides` content.

We're using it here for our own planning *and* refining it as a thing we'll teach. If it's awkward in our own use, it's not ready to ship.

## How

### Golden circle

Every plan section, of any tier, should anchor on the Why before describing the How and the What. *Why* this exists, what it's for, what changes if we do it well. Then *How* — the approach, principles, architectures, trade-offs being made, dependencies. Only then *What* — the concrete moves, file structures, content, deliverables.

This is harder than it sounds. The instinct is to skip Why because it feels obvious, then jump to What because it feels productive. Pushing through that instinct is the discipline. The Why is what gives a downstream agent (or a future Claude session) the context to make good judgement calls when something we hadn't anticipated comes up.

### Three tiers

- **T1 (overview).** Single document, read by everyone. The shared context -- what we're building, why it matters, the high-level How, the candidate workstreams, the open questions. Anything anyone working anywhere on the plan should know.
- **T2 (workstream).** One file per parallelisable workstream. Each T2 should be reachable from T1 raw or via a rich summary. T2 lays out the workstream's own Why-How-What and identifies T3 topics within it. T2s are *domain-oriented* -- they describe areas of work (shared skills, solo plugin, teaching artefacts), not when things ship.
- **T3 (implementation).** One file per implementation-ready topic. Detailed enough that a Claude Code agent can execute against it with minimal back-and-forth. Anchored in its T2 context, the T1 Whys, and the milestone it belongs to.

### Milestones

- **Mn (milestone).** One file per sequenced delivery goal. Milestones answer "in what order do we ship, and what must exist before the next thing can start?" -- a different axis from T2 workstreams, which answer "what areas of work exist?"

Milestones follow the golden circle:
- **Why** -- who this milestone is for, what it unlocks, why it matters now.
- **How** -- process-focused: sequencing, dependencies between deliverables, how work will be validated, what "done" looks like. (Contrast with T2's How, which is architecture-focused.)
- **What** -- the concrete deliverables for this milestone.

T3 implementation plans are parented by *both* a T2 (domain) and an Mn (milestone). The T2 gives the agent architectural context; the milestone gives it sequencing context and tells it what's in scope for this delivery.

Milestones can be retrospective (capturing what was done, for future agents who need to understand the project's history) or prospective (capturing what's next).

Version numbers and milestones are not the same thing. Versions track breaking changes in deliverables (what users see). Milestones are internal planning (what the team ships and when). Multiple milestones may land within a single version; a single milestone may span preparatory work that doesn't ship to users at all.

### Cross-cuts

Cross-cutting concerns (this document, brand voice, storage architecture, etc.) are planning dependencies that get developed first — and iterated as the plan evolves. T2 and T3 work assumes these are settled (or has explicit decision points where it doesn't).

### Side-quests and reviews

The structure is flat — `Tx-…` prefixes — because real planning gets messy. Side-quests, review notes, ad-hoc explorations are first-class and live alongside the canonical plan files, not buried in folders. Use clear filename prefixes (e.g. `review-…`, `side-quest-…`) so files self-organise visually.

### Council of experts and deep research

Best practice in this space changes fast. Rather than enshrining a particular review process, the planning approach should encourage running Claude itself to do deep research at decision points — at install time for clients, at architectural moments for us. For the current planning round, we don't need to deep-research anything; we're not writing code. We pick well-established and reputable approaches and run with them. As implementation begins, deep research becomes a routine move.

## What (initial)

- This file is the canonical reference for the planning method.
- The same content (lightly adapted) becomes part of the plugin's `guides` material — so clients can apply it to their own AI work.
- Future iteration: as we use it and find friction, refine here and propagate to the guides content.

## Open questions

- How do we want to handle plan reviews specifically — do we have a defined "council of experts" pass at each tier, or do we trust the discipline of the golden-circle anchoring + cross-cut dependencies?
- When a side-quest emerges, what's the lightweight template for capturing it without disrupting the main plan?
