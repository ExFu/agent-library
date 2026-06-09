# Example substrate (v0.3.0)

A browsable reference implementation of the v0.3.0 substrate design. Shows what a real substrate looks like for a solo user with two top-level scopes and one level of nesting.

## What this demonstrates

1. **exfu/ as special location.** No scope.md, but internally structured with standard folder-types inside v0.3/.
2. **Versioned exfu/.** v0.3/ directory, latest.txt fallback, derived/ with example index.
3. **Minimal scope.md.** Every scope.md is YAML frontmatter + protective header. No entities, no status fields.
4. **Scope nesting via scopes/.** acme/ has scopes/q3-renewal/. The nested scope declares parent: Acme.
5. **Reference+delta agent.md.** Every agent.md has a protective header, Follows: line, and optional Local deviations.
6. **Store-or-point.** user/todo/ and acme/todo/ demonstrate pointers (ClickUp). side-project/inbox/ stores data locally.
7. **Unversioned user/.** user/scope.md has no exfu: field.
8. **Protective headers.** Every scope.md and agent.md starts with the standard blockquote.
9. **Principles and recommendations in context/.** exfu/v0.3/context/ contains principles.md and recommendations.md.
10. **Example index output.** derived/index.json shows what the nightly index produces.

## Structure

```
exfu/           convention base, versioning infra, global index
user/           personal workspace (unversioned)
scopes/
  acme/         client scope with nested q3-renewal project
  side-project/ minimal scope showing store pattern
```

## Design reference

See `plugin/planning/v0.3.0-reconciliation.md` for the resolved design decisions this example implements.
