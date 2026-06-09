# Folder type: context/

Background an agent should know about this scope. The briefing material that makes an agent useful rather than generic.

**Analogy:** a wiki.

## Default behaviour

An agent reads context/ when it needs to understand the scope beyond its vocabulary. This is where personal background, project history, team culture, stakeholder info, and situational awareness live.

## Store-or-point

- **Stored:** Markdown files with background info (about-me.md, project-history.md, stakeholders.md).
- **Pointer:** "Team context lives in Confluence at [URL]. Read that for full background."

## Boundaries

- Context is background *information*. Definitions of terms go in ontology/. Documents to keep go in docs/. Tasks go in todo/.
- Context doesn't need to be comprehensive. A few paragraphs that help an agent make better decisions are more valuable than an exhaustive wiki nobody maintains.
