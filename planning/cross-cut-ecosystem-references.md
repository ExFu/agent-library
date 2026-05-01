# Cross-cut: Ecosystem references

## Why

ExFu is positioned as a guide through the current best-practice ecosystem, not as a unique source of insight. Users benefit when the install agent points at the best resource for their specific question — Anthropic's official docs and courses, well-respected community skills, third-party tutorials — rather than re-teaching everything in-house. This also keeps the plugin lean: we don't have to recreate content that's already excellent and freely available.

Equally important: as the ecosystem evolves fast, encouraging the install agent (and clients themselves) to use Claude itself for deep research at decision points means the plugin stays useful even as specific external resources change underneath.

## How

### Two kinds of reference

**Static curated links.** Resources that are well-established and unlikely to disappear soon. The plugin ships a curated catalogue of these so the install agent can point at them at appropriate moments.

**Dynamic research patterns.** When the question is "what's the current best practice for X", the right move is for the agent (or the user) to do a fresh web search or deep research run. The plugin teaches *the move*, not the answer. Users who learn this pattern carry it with them well beyond the initial install.

### Curated catalogue (initial)

Anthropic-published:
- **Claude 101** (`https://anthropic.skilljar.com/claude-101`) — broader Claude orientation for users new to Claude.
- **Claude Code 101** — for users who'll do any code work with Claude.
- **Introduction to Claude Cowork** — directly relevant, explains the surface ExFu installs run on.
- **Anthropic docs** (`https://docs.claude.com`, `https://support.claude.com`) — feature-specific reference.
- **Anthropic skill documentation** — for users who want to understand or write skills.

Community / third-party:
- **claude101.com** — third-party guides; useful framing alternatives.
- **superpowers** (skill collection) — well-respected community skills worth referencing.
- **oh-my-claude** — community framework with useful patterns.
- (More to add as the catalogue grows. Worth a research pass to map current landscape.)

### When to point users at external resources

- User asks a question well-covered by an Anthropic resource → brief in-conversation answer + link.
- User wants to go deeper than the install scope → link.
- User is curious about Claude features outside ExFu's scope (e.g. Claude Code) → link.
- User encounters a feature-specific issue → link to support docs.

The install agent should reach for external links rather than expanding its own explanations whenever the external resource is a better answer. ExFu's value is the personal install experience, not exclusive content.

### Attribution and credit

When the plugin's own teaching content builds on a public concept, credit the original source. Specifically:
- Substrate diagram, primer, install patterns — note which concepts come from established practice (golden circle, JTBD, etc.) and which are ExFu's own framings.
- Skills bundled in the plugin that adapt or are inspired by community skills should credit the source.

### Deep-research as a teachable move

Both the install agent and the user can be coached toward Claude's deep-research as a routine move when current best-practice matters. This becomes part of the `guides` content and part of the install conversation when the user expresses uncertainty about how to do something current.

## What (initial)

- Curated catalogue lives in a plugin resource file (`resources/ecosystem-references.md` or similar). Single canonical list.
- The `exfu:guides` skill surfaces relevant entries to the user.
- The install-solo and install-teams skills reference the catalogue when pointing users at external resources.
- The deep-research-as-a-move pattern is captured in `guides` content as part of the planning approach (cross-cut-planning-approach.md is its planning-time anchor).

## Open questions

- What's the maintenance plan for the catalogue? Worth a six-monthly review pass minimum, given how fast the ecosystem moves.
- How do we handle community skills that have known issues or dependencies — we credit them but recommend with caveats? Worth a notes column in the catalogue.
- Should the plugin shipping deep-research-as-a-pattern guidance also include sample prompts for it (e.g. "how to ask Claude to research the current best practice for X")? Probably yes; small reusable templates.
