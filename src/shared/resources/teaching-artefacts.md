# Teaching Artefacts Catalogue

This catalogue is the single source of truth for all teaching artefacts available in the ExFu plugin suite. Install agents — `exfu:install-solo`, `exfu:install-team`, and `exfu:install-team-admin` — reference this file when looking for a visual to use at a calibration or orientation moment. Each entry gives you the format, path, what it teaches, and when to reach for it.

To show an artefact, load the file at the given path (relative to `${CLAUDE_PLUGIN_ROOT}`) and render or share it inline. When a diagram is relevant but the moment hasn't arrived yet, hold it — don't dump all of them at once. One diagram per moment of genuine need.

New artefacts can be added to this catalogue without changing the install skills. Add an entry below, place the file at the listed path, and the install agents will find it.

---

## Artefacts

### substrate-overview

| Field | Value |
|---|---|
| Format | PNG |
| Path | `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/substrate-diagram.png` |
| Variant(s) | all (solo, team, team-admin) |
| Source | ExFu original |

**What it teaches:** The four ingredients of a Claude substrate (knowledge base, skills, connectors, things on a timer) and the discoverability asymmetry between them — skills surface themselves, files need to be pointed at. Gives the user a concrete map of what they're about to build.

**When to show it:** At the very start of an install, before doing anything else. This is the calibration moment. Walk through it briefly: what each ingredient does, what they do together, and the felt experience you're building toward. The diagram does heavy lifting — it tells the user there's real structure here and gives them a reference point for the rest of the conversation.

---

### agent-typology

| Field | Value |
|---|---|
| Format | PNG |
| Path | `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/agent-typology.png` |
| Variant(s) | all (solo, team, team-admin) |
| Source | ExFu original (typology builds on Anthropic's public agent/tool framing) |

**What it teaches:** The four broad types of AI agent interaction — chat, cowork (knowledge worker), coding, and custom-hosted — and where ExFu fits (Cowork). Helps users orient to what they're getting and what's not in scope.

**When to show it:** When a user is confused about where ExFu fits relative to other Claude surfaces or AI tools they've heard about. Useful when someone asks "is this like using the API?" or "how does this relate to Claude Code?" Frames the answer visually without a long explanation.

---

### personal-vs-team-skills

| Field | Value |
|---|---|
| Format | PNG |
| Path | `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/personal-vs-team.png` |
| Variant(s) | team, team-admin |
| Source | ExFu original |

**What it teaches:** The two-layer structure of a team substrate: each user's personal substrate on one side, the team's shared substrate on the other, and the user's `wow` skill as the bridge that makes both accessible in a single session.

**When to show it:** Early in the team or team-admin install, when introducing the concept that the user has both a personal substrate and a shared team layer. Especially useful before explaining what the user owns versus what the substrate champion manages.

---

### admin-vs-user-domain

| Field | Value |
|---|---|
| Format | PNG |
| Path | `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/admin-vs-user.png` |
| Variant(s) | team-admin only |
| Source | ExFu original |

**What it teaches:** The separation between the admin plane (what the substrate champion controls: shared skills, conventions, repo policies, onboarding materials) and the user domain (what individual team members own: personal substrate, personal scopes, their own `wow` customisations). Establishes why the team-admin plugin has different capabilities than the team plugin.

**When to show it:** At the start of the team-admin install, when introducing the substrate champion role. Also useful when a team-admin user asks what they should and shouldn't be putting in shared skills versus leaving for members to decide.

---

### seniority-trust-roles

| Field | Value |
|---|---|
| Format | PNG |
| Path | `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/seniority-trust.png` |
| Variant(s) | team-admin only |
| Source | ExFu original |

**What it teaches:** Recommended substrate configurations across organisational seniority and trust levels. Shows how the substrate setup that makes sense for an exec (broader access, fuller context sharing, more automation) differs from what makes sense for an IC or a new joiner (more constrained, narrower shared context). Helps the substrate champion think about permissions and configuration rather than applying one setup to everyone.

**When to show it:** During the team-admin install when designing the team's substrate structure, or when the substrate champion is deciding what shared context to expose to different roles. Also useful when an IT or security reviewer wants to understand how access is differentiated by role.
