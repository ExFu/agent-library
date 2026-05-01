# Cross-cut: Teaching artefacts

## Why

Abstract concepts in AI-assistant land are hard to grok. People understand them when they see them. A library of teaching artefacts — diagrams, live HTML widgets, worked examples — gives the install agent (and the client themselves) ways to make the abstract concrete at the moment it matters.

This is structural, not a one-off. We already know we want a substrate diagram, an agent-typology diagram, a personal-vs-team-skills-and-instructions diagram, an admin-plane-vs-user-domain diagram, and a seniority/trust-roles diagram. There will be more. The planning needs to treat the catalogue as extensible from day one rather than tacking each new one on.

## How

### Two formats

- **Static diagrams (PNG, SVG).** Single image, standalone, easy to share and easy to drop into a chat. Best for orientation moments where the user just needs a glance.
- **Live HTML artefacts.** Interactive widgets the install agent can render inline during a conversation. Useful where the value is in playing with the concept (e.g. seeing what a setup looks like as different roles are toggled) rather than just seeing it.

Pick the format per artefact based on whether interactivity adds clarity. Default to static unless interactivity is genuinely useful.

### Catalogue structure

A single canonical index of teaching artefacts lives in the plugin. Each entry has:
- Artefact name
- Format (PNG / SVG / HTML)
- File path within the plugin
- One-line summary of what it teaches
- When the install agent should consider showing it
- Source/credits if borrowed or built on prior work

The install-solo and install-teams skills reference the index when looking for a teaching artefact for the moment. The catalogue can grow without changing the skills' code.

### Source attribution

Many teaching concepts in the AI space have prior art. When an artefact builds on someone else's idea, credit them in the artefact and in the catalogue entry. ExFu is a guide through the ecosystem, not an originator of every concept.

### Production workflow

**Static diagrams (PNG, SVG)** are produced via ChatGPT — currently the strongest diagram generator. The planning task is to write rich descriptive instructions that capture *what the diagram needs to convey* (concepts, structure, relationships, key visual asymmetries to surface) rather than dictating visual particulars (which ChatGPT handles well on its own). When the surrounding planning file already contains the rich description, the instruction can be as simple as "give ChatGPT this entire file plus this request: <request>". Alastair copy-pastes between Claude and ChatGPT and brings the resulting image back into the plugin.

The principle: be hyper-clear on the conceptual content, hands-off on the visual styling. If we find ourselves writing "use this colour" or "put this on the left", we're doing ChatGPT's job badly.

**Live HTML artefacts** are produced directly by Claude (via Cowork's artefact mechanism or as static `.html` files bundled in the plugin). These need full implementation, not just instructions, because they're code.

### Where artefacts live in the plugin source

Static diagrams: `plugin/src/shared/resources/diagrams/<artefact-name>.png` (or .svg).
Live HTML: `plugin/src/shared/resources/widgets/<artefact-name>.html`.
Catalogue index: `plugin/src/shared/resources/teaching-artefacts.md` — single source of truth for what's available, what each teaches, when to surface it.

## What (initial)

Known teaching artefacts (some exist, some are TBD):

- **Substrate overview diagram** — the four ingredients and the discoverability asymmetry. Already drafted. Lives at `public/clients/substrate-diagram.png` (will move into the plugin source).
- **Agent typology diagram** — chat / cowork / coding / custom-hosted agents. Helps users place ExFu's scope. Not yet built.
- **Personal vs team skills and instructions** — where things live for solo vs team installs. Not yet built. Critical for the team plugin.
- **Admin plane vs user domain** — what the team admin controls vs what individual team members own. Not yet built.
- **Seniority / trust roles** — recommended permissions and setups across organisational seniority. Not yet built.
- **Install flow diagram** — visual of how an install conversation unfolds (the about-me → buffet → small-wins shape). Possibly redundant with the substrate diagram; revisit.

## Open questions

- Where do live HTML artefacts get hosted/served? (Inside the plugin? Fetched from exfu.ai? Rendered as Cowork artefacts?)
- How does the catalogue handle versioning — an artefact updates, but old plugin installations still reference the old version. Probably this is fine because the artefact ships with the plugin version.
- Is there a "teaching-artefact creation" skill in scope? (E.g. an `exfu:create-teaching-artefact` that helps clients generate diagrams for their own evolving setups.) Out of scope for v1, but worth noting.
- Borrowing patterns: are there existing well-known diagrams in the AI-tooling space we should reference rather than redraw? Worth a research pass.
