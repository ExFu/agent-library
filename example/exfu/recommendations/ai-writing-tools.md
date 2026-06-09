---
recommendation: ai-writing-tools
category: ecosystem-pattern
status: stable
---

# Recommendation: Voice-matched writing tooling

## What

Several layered ways to get Claude (and other AI tools) drafting in the user's actual voice instead of a generic AI register: the ExFu `setup-writing-styles` skill (creates a per-user voice profile from samples), Anthropic's project-level instructions (sets baseline voice for a Claude Project), and third-party tools like ProWritingAid or Grammarly only when the user wants editorial polish rather than voice matching.

## Why a user would want this

Default AI writing reads like AI writing. The user's actual voice is what makes their writing theirs. Once Claude has a voice profile, drafts come back recognisable to the user, requiring edits rather than rewrites.

## Trigger phrases or contexts to surface this

The install agent surfaces this recommendation when the user mentions any of:

- Wanting Claude to draft on their behalf (emails, posts, messages, docs).
- Frustration that AI-generated text "doesn't sound like me".
- Editing AI drafts heavily because the voice is off.
- Specific drafting moments where voice matters (a tone-sensitive email, a personal LinkedIn post).
- Any creative or expressive writing context.

Do not surface unsolicited. The agent waits for the user to bring up drafting or voice frustrations, then offers the layered options in order: ExFu's voice setup first (free, owned by the user, lives in the substrate), Anthropic project instructions second (one place to maintain, applies inside a Project), third-party polish tools third (paid, separate workflow).

## Caveats

- Voice profile quality scales with sample quality. Three good samples covering different registers beat ten one-line messages.
- Voice profile is per-user, not per-scope. If the user wants different voices for different contexts (work vs personal vs a specific publication), that is a separate setup per voice.
- Third-party polish tools (Grammarly etc.) work *on top* of Claude output, not instead of voice setup. They polish; they do not voice-match.

## Where to get it

- ExFu's `setup-writing-styles` skill is shipped in the ExFu plugin (current location: `plugin/src/shared/skills/setup-writing-styles/`; v0.3.0 location: `exfu/skills/setup-writing-styles/`).
- Claude Project instructions: set in the Project's settings within Claude Desktop or the web app.
- Third-party tools: their own provider websites.

## Notes

The install agent's job is to surface the *right* layer for the user's actual need. A user who wants Claude to draft personal messages probably needs ExFu's voice setup. A user editing a Project's outputs probably needs Project instructions tweaked. A user who is happy with voice but wants grammar/style polish needs the third-party tool. Asking "which layer hurts most right now?" is usually clarifying.
