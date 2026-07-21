# ExFu convention base -- v0.3

The definitions everything else in this substrate builds on. To its user this whole installation is their Agent Library; "substrate" is the internal register for how the library is implemented. This directory is owned by the ExFu plugin: agents and users read it, they don't edit it. It is deliberately flat and small so it can be ingested in a handful of reads.

- `ontology.md` -- the complete core ontology in one file: the two vocabulary registers (Agent Library user-facing, substrate internal), the scope model, the folder-type catalogue, scheduled agents and librarians, the way-of-working concept, and the authoring rules. **Read this first.** `Follows:` references across the substrate point into it by anchor.
- `principles.md` -- the design principles behind the conventions, plus curated tool recommendations.
- `librarians/` -- the ExFu-shipped librarian definitions (nightly-index, inbox-triage, dashboard-generator, version-cleanup). Instances, ready to register.
- `skills/` -- the ExFu-shipped skill sources, including the way-of-working template that personal wow skills are generated from.

This directory is not a scope (no scope.md). Versioned convention bases sit side by side under `exfu/`; `exfu/latest.txt` names the current one, and generated content lives in `exfu/derived/`.
