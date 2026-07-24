# Migrations

Append-only. Newest at the bottom, so the file reads in the order things happened.

One entry per migration **considered**, not only per migration applied. A migration that did not apply to this library is recorded as `not-applicable` -- that is what stops it being reconsidered on every session, and what tells a later agent the question was already settled.

Entry format:

```markdown
## <migration-id>
- considered: <ISO date>
- by: <actor> (<surface>), plugin <version>
- outcome: applied | not-applicable | failed | skipped
- notes: <what happened, and any decision the user made>
```

---
