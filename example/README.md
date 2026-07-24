# Example Agent Library

A browsable reference implementation of the current substrate design. Shows what a real library looks like for a solo user with two top-level scopes and one level of nesting.

## What this demonstrates

1. **exfu/ as special location.** No scope.md. Deliberately flat: the versioned contract, plus the unversioned readme, principles, shipped librarians, and shipped skill sources.
2. **The single-file core ontology.** exfu/20260724-1749/ontology.md carries the complete structural vocabulary in one read; every agent.md Follows: line anchors into it (e.g. `ontology.md#todo`).
3. **The lock boundary.** The version directory holds ontology.md and nothing else -- a file is frozen if and only if a Follows: line can anchor into it. readme.md, principles.md, librarians/ and skills/ sit unversioned beside it and move with plugin releases. latest.txt names the current version; derived/ is the generated cache.
4. **Minimal scope.md.** Every scope.md is YAML frontmatter + protective header. No entities, no status fields.
5. **Scope nesting via scopes/.** acme/ has scopes/q3-renewal/. The nested scope declares parent: Acme.
6. **Reference+delta agent.md.** Every agent.md has a protective header, Follows: anchor, and optional Local deviations. Descriptors carry no state -- nothing says "currently empty" or counts items.
7. **Materialise on demand.** Folder-types exist only where content does. side-project/ has just scope.md, context/, and scheduled/ -- a healthy minimal scope, not an incomplete one.
8. **Store-or-point.** user/todo/ and acme/todo/ demonstrate pointers (ClickUp). q3-renewal/todo/ stores tasks locally with done.md.
9. **Reference documents live in context/.** A kept document (PDF, transcript, export) sits beside the prose that gives it meaning.
10. **Unversioned user/.** user/scope.md has no exfu: field and parent: none.
11. **Scheduled-agent definitions as agent instructions.** Two kinds, one format (YAML frontmatter over an instruction body; scripts are tools the instructions call, never the work itself):
    - **Librarians** (substrate remit) ship in exfu/librarians/: nightly-index, inbox-triage, dashboard-generator, version-cleanup.
    - **Business agents** (domain remit) live in a scope's scheduled/ folder: scopes/side-project/scheduled/weekly-trends-scan.md, with its output at side-project/context/trends-notes.md.
12. **Agent registry.** derived/agent-registry.json shows the runtime state: registered scheduled agents with kind (librarian or agent), cadence groups (nightly-agents, weekly-agents), and health tracking.
13. **Run log.** derived/agent-log.json shows the run history: one entry per outcome, with timestamp, status, and a one-line detail.
14. **Example index and dashboard.** derived/index.json and exfu/visualisations/dashboard/index.html show what the nightly run produces.
15. **The dashboard's front door.** dashboard.html at the root is a generated redirect to the real page in the visualisations gallery -- a redirect rather than a symlink, because sync layers handle symlinks unreliably and a symlinked page would resolve the dashboard's own relative gallery links from the wrong depth.

## Structure

```
dashboard.html    generated front door: redirects into exfu/visualisations/
exfu/             convention base, versioning infra, generated cache
  20260724-1749/  the versioned contract: ontology.md (the core, ONE file)
  readme.md       orientation map, including the on-disk layout
  principles.md   design principles and recommendations
  librarians/     shipped librarian definitions
  skills/         shipped skill sources (wow template)
  derived/        generated files (index.json, agent-registry.json, agent-log.json)
  visualisations/ generated dashboard
  latest.txt      points to 20260724-1749
user/             personal workspace (unversioned): context, ontology, todo pointer,
                  reminders, inbox
scopes/
  acme/           client scope (context, ontology, todo pointer) with nested q3-renewal
                  (context, local-store todo)
  side-project/   minimal scope: context plus a registered weekly business agent
```

## Design reference

See `planning/v0.3.0-reconciliation.md` for the design decisions the scope model came from, `planning/conventions-lock-boundary.md` for why the version directory holds only the ontology, and `exfu/20260724-1749/ontology.md` here for the conventions themselves.
