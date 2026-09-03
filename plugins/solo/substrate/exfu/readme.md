# ExFu convention base

The definitions everything else in this substrate builds on. To its user this whole installation is their Agent Library; "substrate" is the internal register for how the library is implemented. This directory is owned by the ExFu plugin: agents and users read it, they don't edit it. It is deliberately flat and small so it can be ingested in a handful of reads.

## What is versioned, and what is not

`exfu/<timestamp>/ontology.md` is the **contract**. It is frozen the moment it ships: a version directory's contents never change under a stable name, and every conventions release mints a fresh identifier. Scopes pin to a version and read their conventions from it.

Everything else here is **plugin-versioned** -- it moves with plugin releases like any other shipped file. The rule that decides which is which:

> A file belongs in a version directory if and only if a `Follows:` line can anchor into it.

Nothing anchors into this readme, the principles, the librarian definitions, or the skill templates, so none of them are frozen. That is deliberate: it lets the conventions stay genuinely locked while documentation, shipped agents, and templates evolve at the pace features need.

- `<timestamp>/ontology.md` -- the complete core ontology in one file: the two vocabulary registers (Agent Library user-facing, substrate internal), the scope model, the folder-type catalogue, scheduled agents and librarians, the way-of-working concept, and the authoring rules. **Read this first.** `Follows:` references across the substrate point into it by anchor.
- `principles.md` -- the design principles behind the conventions, plus curated tool recommendations.
- `librarians/` -- the ExFu-shipped librarian definitions (nightly-index, backlog-sweep, docket-compact, dispatcher, dashboard-generator, version-cleanup, library-updater). Instances, ready to register. Unversioned because each describes a plugin-owned script and moves with it, which also keeps registry `source` paths stable across mints.
- `migrations/` -- the shipped migrations that carry an existing library from an older shape to this one. Ordered by id; applied by the library-updater librarian, which records every outcome in `durable/ledger/`.
- `skills/` -- the ExFu-shipped skill sources, including the way-of-working template that personal wow skills are generated from.
- `latest.txt` -- names the current convention version.
- `derived/` -- generated cache: the global index, the scheduled-agent registry and log. Never hand-edited.
- `visualisations/` -- ExFu-shipped visual outputs, e.g. the dashboard.

This directory is not a scope (no scope.md). Versioned convention bases sit side by side under `exfu/`.

## Substrate layout

How a library looks on disk. This depiction lives here rather than in the ontology because it describes what the plugin currently ships, which is free to change.

```
substrate-root/
  CLAUDE.md          # guard file: warns sessions that haven't loaded the conventions
  dashboard.html     # generated front door: redirects into exfu/visualisations/
  exfu/              # convention base (plugin-owned; agents and users don't edit it)
    20260903-1743/   # a convention version: ontology.md only, frozen at ship
    readme.md        # this file
    principles.md    # design principles and recommendations
    librarians/      # shipped librarian definitions, ready to register
    migrations/      # shipped migrations, applied by the library-updater
    skills/          # shipped skill sources (the wow template)
    latest.txt       # current version name, e.g. "20260903-1743"
    derived/         # generated cache: index, registries. Never hand-edited.
    visualisations/  # ExFu-shipped visual outputs, e.g. the dashboard
  durable/           # the permanent record: facts about this library that
                     #   nothing can regenerate. Append-only. A refresh
                     #   replaces exfu/ and never touches this.
    ledger/          #   the logbook: migrations.md, install.md
  user/              # the personal scope (special: unversioned, parent: none)
  scopes/            # every other scope
```

Note the asymmetry between `exfu/` and `durable/`: everything in `exfu/` is replaced wholesale on update, and nothing in `durable/` ever is. That is the whole reason the permanent record is not kept here. State the rule positively wherever it appears -- a refresh replaces `exfu/`, and never touches `durable/`, `user/`, or `scopes/` -- because an exception list grows silently wrong.
