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

## 20260724-1910-split-convention-base
- considered: 2026-07-24
- by: al (Claude Code), plugin 0.10.0
- outcome: not-applicable
- notes: fresh install -- library created at the target shape

## 20260903-1743-docket
- inventory: Alastair (reminders 3, inbox 1, todo pointer); Acme (todo pointer only)
- Alastair: converted -- 3 reminders with once triggers, 1 backlog entry, todo pointer carried; originals in docket/legacy/
- Acme: skipped -- Al: "leave Acme on the old shape until the renewal closes"; pointer-only, nothing to convert
- considered: 2026-09-03
- by: al (Claude Code), plugin 0.11.0
- outcome: applied
- notes: al-reminders and al-inbox replaced by al-docket in the same sitting; slack-dm channel declared and granted auto.
