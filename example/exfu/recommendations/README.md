# exfu/recommendations/

## Purpose

A curated catalogue of third-party connectors, plugins, and skills that most users would benefit from considering. The install agent consults this catalogue in conversation, surfacing relevant entries at the moments they would be useful, rather than as a buffet at the start or a passive resource the user has to know to ask about.

## Contents

One file per recommendation:

- `calendar-connector.md` — the user mentions calendar-related work, the agent surfaces this.
- `ai-writing-tools.md` — the user mentions drafting in their voice, the agent surfaces this.

(A real install would carry many more. The current `ecosystem-references.md` resource in the v0.2.x plugin is the seed material for this catalogue.)

## Dependencies

- Consulted by the install agent in real time during the install conversation (T2-D in the v0.3.0 plan).
- Open to user and scope extension: users may add their own `recommendations/` at `user/recommendations/`; scopes may add scope-specific recommendations.

## Shape of a recommendation entry

Each recommendation file follows the same shape (illustrated in the two example entries):

- **What** — the connector/plugin/skill, one line.
- **Why a user would want this** — the outcome it delivers.
- **Trigger phrases or contexts** — what the user might say or be doing that should cause the agent to surface this.
- **Caveats** — anything the user should know before installing (paid vs free, requires X, conflicts with Y).
- **Where to get it** — link or install instructions.

## Why this is a separate ontology type, not a single file

A single `recommendations.md` would grow unwieldy and the agent would have to parse the whole thing every time. As individual atoms, the agent can match on filename or content for the relevant entry at the moment of need, and users can add or remove specific recommendations without touching the rest.

## Why this is consulted but not offered

Per the outcome-framed elicitation principle: the install agent does not ask "do you want to install third-party connectors?". It listens for the user's actual needs and surfaces the relevant recommendation in context. The user sees a recommendation when it would help, not before.
