# T3 -- Example prototype

Rebuild `plugin/example/` from scratch to demonstrate the resolved v0.3.0 substrate design. The example is the reference implementation -- the thing future agents and design sessions look at to understand what a real substrate looks like.

**Parents:** `T2-substrate-architecture.md` (domain), `M2-substrate-redesign.md` (milestone)
**Prerequisites:** T3-convention-base, T3-scope-model, T3-versioning (the conventions, scope format, and versioning infrastructure must all be defined before the example can demonstrate them)
**Status:** not started.

---

## Why

The existing `plugin/example/` (~50 files) follows the pre-direction model: exfu/ without scope.md, convention snapshots, scopes as leaves, rich YAML-heavy scope.md, ontologies/ plural. Every one of these diverges from the resolved design.

A correct example is essential because:
1. **Future agents use it as a reference.** When an install conversation creates a scope, it should match the example's patterns.
2. **It validates the design.** If the resolved decisions produce an awkward or confusing substrate when made concrete, the example surfaces that before skills are rewritten.
3. **It's a teaching artefact.** Al (and future collaborators) can browse the example to understand the substrate without reading design docs.

---

## What to build

### Directory structure

The example should demonstrate a realistic substrate for a solo user with two top-level scopes and one level of nesting. Enough to show the patterns; not so large that it's hard to browse.

```
plugin/example/
  exfu/
    v0.3/
      ontology/
        agent.md
        readme.md
        scope/
          what-is-a-scope.md
          scope-md-format.md
          nesting.md
        folder-types/
          ontology.md
          context.md
          docs.md
          skills.md
          librarians.md
          todo.md
          reminders.md
          inbox.md
          databases.md
          visualisations.md
        librarian/
          what-is-a-librarian.md
          nightly-index.md
      context/
        agent.md
        readme.md
        principles.md           # Golden Circle, concrete-first, etc.
        recommendations.md      # curated third-party suggestions
      skills/
        agent.md
        readme.md
      librarians/
        agent.md
        readme.md
        nightly-index.md        # the canonical librarian definition
      todo/
        agent.md
        readme.md
      reminders/
        agent.md
        readme.md
      inbox/
        agent.md
        readme.md
      databases/
        agent.md
        readme.md
      docs/
        agent.md
        readme.md
      visualisations/
        agent.md
        readme.md
    latest -> v0.3/
    latest.txt                   # fallback: "v0.3"
    derived/
      index.json                 # example nightly index output
  user/
    scope.md                     # name: Alastair, no exfu pin
    ontology/
      agent.md
      readme.md
      ways-of-working.md         # personal definitions
    context/
      agent.md
      readme.md
      about-me.md                # personal background
    skills/
      agent.md
      readme.md
    todo/
      agent.md                   # "tasks are in ClickUp"
      readme.md
    reminders/
      agent.md
      readme.md
    inbox/
      agent.md
      readme.md
  scopes/
    acme/
      scope.md                   # name: Acme, parent: root, exfu: v0.3
      ontology/
        agent.md
        readme.md
        terminology.md           # "we call them clients, not customers"
      context/
        agent.md
        readme.md
        account-overview.md
      todo/
        agent.md                 # "tasks are in ClickUp, tag: acme"
        readme.md
      docs/
        agent.md
        readme.md
      scopes/
        q3-renewal/
          scope.md               # name: Q3 Renewal, parent: Acme, exfu: v0.3
          context/
            agent.md
            readme.md
            deal-brief.md
          todo/
            agent.md
            readme.md
    side-project/
      scope.md                   # name: Side Project, parent: root, exfu: v0.3
      context/
        agent.md
        readme.md
      inbox/
        agent.md
        readme.md
```

### Key demonstrations

The example must visibly demonstrate each resolved design decision:

1. **exfu/ as special location, internally like a scope.** No scope.md in exfu/, but it has the standard folder-types inside v0.3/.

2. **Versioned exfu/.** v0.3/ directory, latest symlink, latest.txt fallback, derived/ with example index.

3. **Minimal scope.md.** Every scope.md is 5-10 lines: YAML frontmatter (name, purpose, parent, exfu) + protective header + optional one-sentence elaboration. No entities, no status fields, no dependency arrays.

4. **Scope nesting via scopes/.** Acme has `scopes/q3-renewal/`. The q3-renewal scope.md declares `parent: Acme`.

5. **Reference+delta agent.md.** Every agent.md has: protective header, `Follows:` line with versioned path, optional `Local deviations:` section. Folders with no deviations have just the header and follows line.

6. **Store-or-point.** user/todo/ and acme/todo/ demonstrate the pointer pattern ("tasks are in ClickUp"). side-project/inbox/ demonstrates the store pattern (data lives locally).

7. **Unversioned user/.** user/scope.md has no `exfu:` field.

8. **Protective headers.** Every scope.md and agent.md has the standard blockquote header.

9. **Principles and recommendations in context/.** exfu/v0.3/context/ contains principles.md and recommendations.md (the pre-direction's dedicated folders collapsed into context/).

10. **Example index output.** derived/index.json shows what the nightly index produces -- scope tree, folder-type population, version pins.

### Content tone

The example uses realistic content, not lorem ipsum. The "Alastair" user scope, the "Acme" client scope, the "Q3 Renewal" project scope are plausible scenarios. Content should be brief but recognisable -- someone browsing should think "I see how this would work for my projects."

Follow the brand voice: direct, warm, simple words. No insider vocabulary in user-facing readme.md files.

---

## What to delete

The entire existing `plugin/example/` directory. It follows the pre-direction model and every structural pattern diverges from the resolved design. No files can be reused as-is, though content (like the Alastair persona and the Acme scenario) can be adapted.

---

## Acceptance criteria

1. `plugin/example/` contains a complete, browsable substrate following all resolved v0.3.0 decisions
2. Every scope has minimal scope.md with correct YAML frontmatter
3. Every agent.md uses the reference+delta pattern with versioned paths
4. At least one scope demonstrates nesting via scopes/
5. At least one folder-type demonstrates the pointer pattern (store-or-point)
6. exfu/ has versioned directory, symlink, latest.txt, and derived/ with example index
7. user/ scope is unversioned
8. All protective headers are present and consistent
9. The example is self-consistent -- every reference resolves to something that exists within the example
10. An agent or human browsing the example can understand the v0.3.0 substrate design without reading design docs

---

## Where this plan lives

- This file: `plugin/planning/T3-example-prototype.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
- Existing example (to replace): `plugin/example/`
