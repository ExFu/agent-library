# Context

## Why

Agents work better with background. Without context, they give generic answers. This folder holds the briefing material that makes an agent useful for this specific scope -- history, culture, stakeholder info, situational awareness.

## How

Files here are background reading. An agent entering the scope reads context/ to understand the situation before acting. Content can range from a few paragraphs to a collection of briefing documents.

In the ExFu convention base, context/ holds ExFu's own operating principles (Golden Circle, concrete-first, build-by-doing) and curated recommendations.

### Store-or-point

- **Stored:** Markdown files with background info.
- **Pointer:** "Team context lives in Confluence. Read [URL] for full background."

### Boundaries

- Context is *background information*. Term definitions go in ontology/. Documents to keep go in docs/. Tasks go in todo/.
- Keep it useful, not exhaustive. A few focused paragraphs beat a comprehensive wiki nobody reads.

## What an agent should do

1. Read context/ when entering the scope for the first time or when the user's request needs situational awareness.
2. Don't read context/ on every interaction -- use judgement about when background is relevant.
3. When adding context, keep it concise and current. Flag stale content for the user.
