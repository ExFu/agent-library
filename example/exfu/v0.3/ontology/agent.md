# Ontology

## Why

Every scope needs a shared vocabulary. Without explicit definitions, agents guess what terms mean and users discover misunderstandings too late. An ontology folder makes the scope's vocabulary discoverable and explicit.

## How

This folder holds definitions -- "here is what this concept means in this scope." Each definition is a file (or a section in a file, depending on density). Agents read the ontology when entering a scope to understand the local vocabulary before acting.

In the ExFu convention base (this directory), the ontology defines the structural vocabulary of the substrate itself: what a scope is, how folder-types work, what a librarian is. In a user or project scope, the ontology holds domain-specific definitions ("we call them specialists, not reps"; "a lead in this context means...").

### Store-or-point

- **Stored:** Definition files live here directly (the common case).
- **Pointer:** "Our canonical glossary lives in Notion at [URL]. This folder defines only terms that differ from or extend the Notion glossary."

### Boundaries

- Ontology defines *what things mean*. It does not hold background information (that's context/), task lists (todo/), or reference documents (docs/).
- When writing new ontology entries that touch terms defined elsewhere (parent scope, user/, or exfu/), annotate the relationship: is this an extension, an override, or an orthogonal use of the same word?

## What an agent should do

1. Read this folder when entering the scope for the first time.
2. When a term is ambiguous, check whether the ontology resolves it before asking the user.
3. When creating new definitions, describe the intent for later consuming agents -- especially if a known conflict exists with another scope's ontology.
