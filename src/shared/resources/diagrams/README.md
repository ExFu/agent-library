# Shared diagrams

PNGs that ship in all three plugins (or in a subset, per the catalogue). When you generate a new diagram via ChatGPT (using the brief in `plugin/planning/diagram-instructions/<slug>.md`), drop the PNG here and verify the catalogue entry at `plugin/src/shared/resources/teaching-artefacts.md` matches.

Current contents:

- `substrate-diagram.png` — substrate overview. Ships in all 3 plugins.
- `agent-typology.png` (TODO) — chat / cowork / coding / custom-hosted typology. Ships in all 3.
- `personal-vs-team.png` (TODO) — personal substrate vs team substrate split. Ships in all 3 (catalogue marks it relevant for team and team-admin only; solo install agents won't reach for it).

Path at runtime: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/<slug>.png`.
