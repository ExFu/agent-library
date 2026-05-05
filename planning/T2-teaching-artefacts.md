# T2 — Teaching artefacts

The diagrams and live HTML widgets that the install agents use to make abstract concepts concrete at the moment they matter. Production schedule, instruction patterns, catalogue assembly, attribution.

Anchors back to: `T1-overview.md`, `cross-cut-teaching-artefacts.md`.

---

## Why

Teaching artefacts are first-class deliverables, not decoration. The install conversation reaches for them to calibrate users on the lay of the land. The team and team-admin plugins in particular rely on diagrams to show structural distinctions (personal/team, admin/user, seniority/trust) that are hard to land in prose alone.

This T2 lays out which artefacts are needed, how they get made (per `cross-cut-teaching-artefacts.md`'s ChatGPT-instruction pattern), and where they live in the plugin source so the install agents can find them.

---

## How

### Production pattern (recap from cross-cut)

Static diagrams: we write rich descriptive instructions capturing what the diagram needs to *convey* (concepts, structure, relationships, key visual asymmetries to surface). Alastair takes those instructions to ChatGPT, copy-pastes the resulting image back. We don't dictate visual styling — ChatGPT handles that part well.

Each instruction file lives in `plugin/planning/diagram-instructions/<diagram-name>.md` and is structured:

1. **What this diagram teaches** — one paragraph, the conceptual content the image needs to carry.
2. **Key elements to include** — labelled list of concepts, entities, relationships.
3. **Visual asymmetries that matter** — specifically what the diagram should make *visually unequal* to land the conceptual asymmetry (e.g. skills surface themselves, files don't — the visual should reflect this).
4. **What this diagram is *not* trying to do** — keeps scope tight, prevents ChatGPT from helpfully adding things that confuse.
5. **Source attribution** — if the diagram builds on a public concept, credit it.
6. **Optional: example phrase to give ChatGPT** — e.g. "Here's the conceptual brief. Render as a clear infographic, warm tones, label everything plainly. No corporate stock-art clichés."

Live HTML widgets: we write the HTML directly (Cowork artefact format or static `.html`). These need full implementation, not just instructions.

### Catalogue mechanism

A single index file at `plugin/src/shared/resources/teaching-artefacts.md` lists every available artefact. Each entry:

- Artefact name (slug)
- Format (PNG / SVG / HTML)
- File path (relative to plugin root)
- One-line summary of what it teaches
- When the install agent should consider showing it
- Source attribution (if any)

The install-solo, install-team, and install-team-admin skills reference the catalogue when looking for an artefact for the moment. New artefacts can be added without changing the install skills.

### Where artefacts live

Per `cross-cut-teaching-artefacts.md`:

- Static diagrams (shared, all 3 plugins): `plugin/src/shared/resources/diagrams/<name>.png` (or `.svg`)
- Static diagrams (team + team-admin): `plugin/src/team/resources/diagrams/<name>.png`
- Static diagrams (team-admin only): `plugin/src/team-admin/resources/diagrams/<name>.png`
- Live HTML widgets (shared): `plugin/src/shared/resources/widgets/<name>.html`

Shared diagrams ship in all three plugins. Diagrams in `team/resources/diagrams/` ship in both team and team-admin. Diagrams in `team-admin/resources/diagrams/` ship only in team-admin.

---

## What — artefacts to produce

### Already exists

- **Substrate overview diagram** (`substrate-diagram.png`). Currently at `public/clients/substrate-diagram.png`. Move into `plugin/src/shared/resources/diagrams/`. Captures the four ingredients and the discoverability asymmetry. **Ships in: solo, team, team-admin.**

### To produce — shared (all 3 plugins)

- **Agent typology diagram.** Chat / cowork / coding / custom-hosted agents, with ExFu's scope highlighted as Cowork. Helps users place ExFu in the broader landscape and understand what's *not* in scope. **Ships in: solo, team, team-admin.**

### To produce — team + team-admin

- **Personal vs team skills and instructions.** Two-pane structure showing the user's personal substrate on one side, the team's shared substrate on the other, with the user's `wow` skill bridging both. **Ships in: team, team-admin.** Source: `plugin/src/team/resources/diagrams/personal-vs-team-skills.png`.

### To produce — team-admin only

- **Admin plane vs user domain.** Shows what the team's substrate champion controls (shared skills, conventions, repo policies) versus what individual members own (personal substrate, their own scopes, their own wow customisations). **Ships in: team-admin only.** Source: `plugin/src/team-admin/resources/diagrams/admin-plane-vs-user-domain.png`.
- **Seniority and trust roles.** Recommended permissions and setups across organisational seniority — what an exec setup looks like vs an IC, what shared vs private looks like by trust level. **Ships in: team-admin only.** Source: `plugin/src/team-admin/resources/diagrams/seniority-and-trust-roles.png`.

### Possible future

- **Install flow diagram.** Visual of how an install conversation unfolds (about-me → buffet → small-wins). Possibly redundant with the substrate overview for the calibration moment; revisit after solo plugin is shipping.
- **Live HTML widget for substrate exploration.** Interactive — click a skill, see what it does, click a folder, see what's in it. Higher-effort; defer until basic plugin is shipping.

---

## T3 candidates

- `T3-diagram-instruction-substrate-overview.md` — the existing diagram is already good; this T3 is just the move + a refresh pass on the instructions for future regeneration.
- `T3-diagram-instruction-agent-typology.md` — the conceptual content for ChatGPT. Includes the four agent types, what each is for, where ExFu fits.
- `T3-diagram-instruction-personal-vs-team.md` — team plugin's first diagram.
- `T3-diagram-instruction-admin-vs-user.md` — team plugin's second diagram.
- `T3-diagram-instruction-seniority-trust.md` — team plugin's third diagram.
- `T3-teaching-artefacts-catalogue.md` — author the index file at `plugin/src/shared/resources/teaching-artefacts.md` and the convention for entries.

Run in parallel — diagram instructions are independent. Catalogue work depends on diagram entries existing but is mostly mechanical.

---

## Open questions

- **Live HTML widget timing.** Worth shipping any in v1? Probably not; the static diagrams cover the calibration moments adequately. Defer to a future plugin version once we see whether interactive widgets actually move the needle.
- **Light/dark mode parity.** ChatGPT-produced diagrams come out in whatever style ChatGPT picks. Worth specifying tonal preference? Probably yes — warm earth-tones to match the ExFu brand. Mention in instruction template.
- **Diagram regeneration strategy.** When a concept evolves, the diagram needs updating. The instruction file is the durable artefact; the PNG is regenerated. Make sure each diagram's PNG can be traced back to its instruction file (e.g. via a comment in the catalogue entry, or matching slug names).
- **Source attribution conventions.** When a diagram builds on a public concept (e.g. golden circle), where does the credit live — on the diagram itself, in the catalogue, both? Probably both, briefly.
