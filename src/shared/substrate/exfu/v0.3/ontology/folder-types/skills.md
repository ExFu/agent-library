# Folder type: skills/

Skill definitions or drafts related to this scope. Where scope-specific agent capabilities are defined and packaged.

**Analogy:** functions.

## Default behaviour

Skills here are scoped to this context -- they know about the scope's ontology, conventions, and tools. An agent discovering this folder may surface available skills to the user or use them when relevant to the task at hand.

## Store-or-point

- **Stored:** Skill definition files (.md) or packaged skills following the ExFu skill-packaging convention.
- **Pointer:** "Shared team skills live in the team repo at [path]. This scope adds no scope-specific skills."

## Boundaries

- Skills are *capability definitions*. Background info goes in context/. Vocabulary goes in ontology/. Maintenance automation goes in librarians/.
- Scope-level skills should reference the scope's ontology and conventions rather than duplicating them.
