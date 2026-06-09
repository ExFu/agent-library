# Folder type: ontology/

The scope's shared vocabulary. Definitions of what concepts and terms mean here.

**Analogy:** a glossary.

## Default behaviour

An agent reads the ontology when entering a scope. Definitions are files (one per concept, or grouped by theme). Agents use them to resolve ambiguous terms before asking the user.

## Store-or-point

- **Stored:** Definition files live directly in ontology/.
- **Pointer:** "Our canonical glossary lives in Notion. This folder defines only terms that differ from or extend it."

## Boundaries

- Ontology defines what things *mean*. Background info goes in context/. Documents go in docs/. Task conventions go in todo/.
- When writing definitions that touch terms from other scopes, annotate the relationship (extension, override, or orthogonal).
