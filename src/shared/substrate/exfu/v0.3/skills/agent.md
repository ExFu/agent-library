# Skills

## Why

Scopes often need specialised agent capabilities -- a skill that knows how to query the scope's CRM, generate reports in the scope's format, or follow the scope's review process. Skills/ gives these a conventional home.

## How

Skill definitions here follow the ExFu skill-packaging convention. Each skill is scoped to this context and references the scope's ontology and conventions rather than duplicating them.

### Store-or-point

- **Stored:** Skill definition files (.md) or packaged skills.
- **Pointer:** "Shared team skills live in the team repo at [path]."

### Boundaries

- Skills are *capability definitions*. Background info goes in context/. Vocabulary goes in ontology/. Maintenance automation goes in librarians/.

## What an agent should do

1. Discover available skills when entering the scope.
2. Surface relevant skills to the user when they match the current task.
3. When creating new skills, reference the scope's ontology rather than hardcoding terms.
