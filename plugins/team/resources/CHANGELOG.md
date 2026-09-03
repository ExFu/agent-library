# ExFu plugins changelog

This file tracks substantive changes to the ExFu plugin suite. Future Claude sessions can read it at `${CLAUDE_PLUGIN_ROOT}/resources/CHANGELOG.md` to understand what behaviour has shipped, when, and why. Useful for orientation when a skill's behaviour seems different from how it's described in older notes, or when reconstructing why a convention exists.

Versions match the plugin manifests. Patch bumps cover bug fixes and small behaviour changes; minor bumps add features; major bumps make breaking changes.

---

## v0.11.0 -- 2026-09-03

**What is open in a scope now lives in one docket, as records.** Tasks, reminders and captured thoughts were three folder-types of freeform markdown that scripts guessed at: the dashboard took the first date it found in a line as a reminder's date, decided a folder was a pointer by substring-matching phrases, and split reminder files by whether they happened to use headings or bullets. The two generations of personal skills disagreed about where the files even lived. And one file per captured item is the most expensive shape there is for an agent to read. Decision record: `planning/structured-worklist.md`, adopted after a Codex audit and a two-voice council.

**One folder, three files, one shape.** `docket/` replaces `todo/`, `reminders/` and `inbox/` with `todo.jsonl`, `reminders.jsonl` and `agent-backlog.jsonl`: one JSON object per line, a whole collection in one read from any surface including a phone through the storage connector. The record is deliberately thin (title, notes for humans, agent notes as freeform instructions for agents, status, timestamps, keywords) and carries no ontological fields: priority, dependencies and recurrence are prose an agent can act on. Anything a program must read arrives as a **mixin** file joined on library-wide ids, never as a column. The inbox is renamed for what it always was: the **agent backlog**, a queue of things the user leaves for their agents, not the user's own in-tray.

**Reminders generalise into triggers, signals and a dispatcher.** A trigger is a scope's statement that at some moment, or on some occurrence, something should be assessed by an agent, and how: deliver through a channel, spin up a sub-agent at a declared weight, or run a registered definition. A fired trigger's handler reports **signals**, and any trigger may arm on a signal name, so "check email for the Acme reply" and "on the reply, draft the follow-up" form a workflow neither side knows about. Every fire writes an append-only **receipt**, intent before acting and result after, so a crash cannot double-send and a shared scope carries its own record of what fired. Three schedule modes ship (`once`, `cron`, `on-signal`); natural-language rules are resolved once at authoring time. The **dispatcher** librarian runs hourly as a Claude Code Desktop local task with the cheapest model, never boots the library, and reads one due view; the boot skill drains the same view at session start.

**Channels and consent.** Any scope may declare how it reaches people (`dm`, `broadcast`; `pull` is always there). Whether the dispatcher may send unattended is a property of the channel, `draft` by default, and elevation to `auto` is a grant recorded in `durable/ledger/grants.md`, which the dispatcher checks before every automatic send; in this release `auto` is honoured only on a dm to the trigger's owner.

**The search index moves outside the synced library.** The ontology always said fast lookups are built per machine outside the synced root; `exfu/derived/` was inside it. A stdlib SQLite index with full-text search now lives at `~/.exfu/derived/<library-id>/`, rebuilt incrementally by content hash so nothing is recomputed unless it changed, and never a source of truth. Text caches stay in `exfu/derived/`. No embeddings yet: every path available today needs an install the plugin cannot assume or a per-call cost it will not add; the schema reserves the columns.

**Deprecated, never wiped.** The three old folder-types stay in the ontology as deprecated, every reader keeps a labelled legacy path for them, and the docket migration is offered scope by scope, journalled, reversible, and skippable forever. Half a dozen libraries exist at different stages; the change is meant to be kind to all of them.

**Changed**
- Convention base minted as `20260903-1743/`: `#docket` replaces three folder-types (kept as `#deprecated` with their anchors); new `#docket-mechanics` (`#records`, `#mixins`, `#triggers`, `#signals`, `#fires`, `#actors`, `#channels`, `#grants`, `#schedule-modes`, `#dispatcher`); the derived-location rule reworded; migrations gain the scope-by-scope journal rule.
- New `scheduled-tasks/library-index/index.py` (stdlib only): incremental index, `query`, `due`, `explain`, `fire`, `receipt`, `compact`, and `exfu/derived/due.json`.
- New librarians `docket-compact` (nightly) and `dispatcher` (hourly); `inbox-triage` becomes `backlog-sweep`; registry template gains all three and the hourly cadence. `library-updater` now permits declared scope writes after consent, with a journal.
- Second migration ships: `20260903-1743-docket`, offered per scope, `requires_user_decision: true`.
- `setup-docket` replaces `setup-reminders` and `setup-inbox`; one `docket-template.md` replaces two; the six todo/reminders/inbox defaults and three scope folders are retired.
- `substrate-index/index.py` indexes dockets per file and lists deprecated folder-types per scope; the dashboard gains a Docket section with trigger, receipt and signal views and keeps a labelled legacy renderer.
- `exfu-library` writes `channels.json` at boot and drains the due view at session start; `scope-setup` offers only `docket/`; install skills describe the hourly Desktop task and seed `grants.md`; substrate guide v14.

**Not changed:** the durable membership test, the conventions lock, and the rule that nothing binary is ever written inside the library.

---

## v0.10.1 -- 2026-08-10

**The licence now travels with the plugin.** Every manifest has declared `"license": "Proprietary"` for a while, but the text itself sat only at the top of the source repo, which is not something an installed plugin carries. Anyone installing from the marketplace got a licence claim with nothing behind it, and no obvious way to read the terms they were accepting. The build now copies `LICENSE` into each plugin, so the claim and the text arrive together.

The build fails outright when the file is missing from the repo root, rather than quietly producing a plugin that asserts a licence it cannot show. A declared licence with no text behind it is exactly the thing worth catching at build time instead of leaving for a user to discover.

Nothing about how the plugins behave has changed. Distribution coordinates settled in the same round: the marketplace repo is `ExFu/exfu-marketplace` and the install line is `/plugin install exfu-agent-library-solo@exfu`. Decision record: `planning/T2-build-and-distribution.md`.

---

## v0.10.0 -- 2026-07-24

**Libraries can now be updated over time.** Every release that changes shape needs something to carry installed libraries across, and nothing owned that job -- 0.9.0 shipped its split base with no standalone upgrade path, and the two existing migration skills each encode one transition and know nothing about each other. Decision record: `planning/library-migrations.md`.

**Migrations are boot-detected, not scheduled.** A plugin update does not touch the library; it changes what is installed alongside it. There is no update hook, so nothing *can* run at update time. The first opportunity to notice is the next session that loads `exfu-library`, which compares the migrations the plugin ships against the library's ledger and hands anything pending to the new `library-updater` librarian. Applying happens with the user present, never on a cadence.

**New top-level `durable/`, the permanent record.** The record of what has been done to a library cannot live in `exfu/` (plugin-owned, refreshed wholesale on update -- one refresh would destroy it) and cannot live in `exfu/derived/` (defined as a disposable cache). It is the one thing in the substrate that categorically cannot be regenerated, so it gets its own location that no update touches. The logbook lives inside it at `durable/ledger/`, holding `migrations.md` and `install.md`.

The container is deliberately more general than its first tenant: more stateful things will need to survive outside `exfu/` over time, and naming the root entry after one of them would have been too specific. `durable` was chosen over the alternatives on evidence rather than taste. The corpus already used the word for exactly this category in ten places written before anyone tried to name a folder, and it sits in exact opposition to the one term it must be told apart from, so `exfu/derived/` versus `durable/` teaches the whole rule in five words: **derived is rebuilt, durable is kept.** `state/` was rejected as actively unsafe: the ontology already points that word at the cache ("Current state belongs in the derived index"), so a root `state/` would have made the one file every agent reads cold contradict itself, and the predictable misfile would route regenerable output into the one directory every skill is forbidden to touch.

**The membership test**, in the same iff form as the conventions-lock rule: *a path belongs in `durable/` if and only if it is an append-only text record about the library itself that no shipped generator can produce.* Three conditions, all required. Unregenerable -- delete it, run every librarian twice, and see whether it comes back; regeneration *cost* is explicitly not part of the test, so "expensive to recompute" stays in `derived/`. About the library rather than the world -- records whose subject is a person, company, or deal are domain data and belong in a scope's `databases/`. Append-only human-readable text -- which excludes databases, embeddings, and mutable config by construction rather than by judgement. No SQLite or binary content: libraries sync through Dropbox or git, where database sidecars sync out of order and two surfaces produce a conflicted copy with no merge, so putting one in the directory that exists because its contents cannot be regenerated is self-defeating.

**The carve-out is stated positively, never as an exception list:** *a refresh replaces `exfu/`; it never touches `durable/`, `user/`, or `scopes/`.* This is not cosmetic. An exception list grows silently wrong as durable things are added, and a forgotten entry destroys the only category of file that cannot be recovered -- a bug of exactly that kind was found and fixed in `exfu-migrate-to-dropbox` while building this release.

**Three rules that make this safe**
- **Fresh installs seed, they do not replay.** A new library is already in the target shape, so install records every shipped migration as `not-applicable`. Without this, computing pending as *shipped minus applied* would make every brand-new library attempt the entire migration history against a shape it never had. This is the failure mode that would bite hardest as new users onboard.
- **Preconditions are tested against actual structure, not the ledger.** Users half-migrate, restore backups, hand-edit. The ledger says what is believed; the filesystem says what is true. When they disagree the agent reports and stops, matching the discipline `exfu-migrate-to-dropbox` already applies to divergence.
- **Version skew between surfaces is detected.** Claude Code and Cowork have separate plugin installs and either may auto-update, so the same library can be opened by a surface older than the library itself. A ledger recording migrations the installed plugin does not ship means the library is ahead: that surface declines structural work and says so.

**Changed**
- Convention base minted as `20260724-1910/`: the ontology gains the permanent record (#durable, with #durable-test and #durable-carveout), the ledger as a subsection of it (#ledger, so shipped `Follows:` lines keep resolving), and the migration concept and definition format (#migrations).
- New `exfu/librarians/library-updater.md` and `exfu/migrations/`, both unversioned -- they describe plugin-owned behaviour, so by the 0.9.0 lock rule they are not part of the contract.
- First migration ships: `20260724-1910-split-convention-base`, closing the upgrade gap 0.9.0 left open. It adds the unversioned copies and re-points registry `source` paths; it deliberately does not strip the old version directories, since scopes pinned there still read them.
- Migration ids are `YYYYMMDD-HHMM-slug`, so lexicographic order is application order -- reusing the property the conventions scheme already relies on. Frontmatter carries `plugin:` and, when a mint is involved, `conventions:`, so the version movement is legible without reading the body.
- Templates for `durable/` and `durable/ledger/`, install-time seeding in all three install skills, boot-time detection in `exfu-library`, substrate guide v13.
- Retirement policy stated from the start: the plugin ships migrations back to a documented floor; older libraries are told to reinstall rather than migrated through the full history.

**Fixed:** `build/mint-conventions.sh` rewrote historical identifiers in the changelog. `grep -r src/` emits paths with a doubled slash (`src//shared/...`), which silently defeated the literal path match guarding history-recording files. Paths are normalised before the check now. Caught when the first real mint corrupted the v0.9.0 entry; restored in the same session.

---

## v0.9.0 -- 2026-07-24

**The conventions lock moves to the contract, not the folder.** A convention version directory now contains `ontology.md` and nothing else. Everything else the plugin ships -- `readme.md`, `principles.md`, `librarians/`, `skills/` -- moves out to unversioned `exfu/` and travels with plugin releases. Decision record: `planning/conventions-lock-boundary.md`.

The timestamp scheme (0.6.0) froze version directories so a pinned scope always sees the same conventions. Right, and kept. But the freeze was drawn around a folder of related material rather than the contract surface, and it caught four things nothing resolves against. Measured: all 16 `Follows:` anchors point into `ontology.md`; nothing anchors into the readme, the principles, the librarian definitions, or the skill templates. They were locked purely by colocation.

The rule that now decides membership, and is mechanically decidable rather than a per-edit judgement call:

> A file belongs in a version directory if and only if a `Follows:` line can anchor into it.

This came out of 0.8.0, where a two-line documentation edit was blocked by a rule that had no business covering it. Relaxing the rule to "additive-only" was considered and rejected: the base is read *live* (the registry pins agents to definitions by versioned path), so an additive line in a librarian's `writes:` frontmatter is textually additive but expansive in authority; "byte-identical" is checkable in CI while "additive enough" is judged by whoever wants the edit; and the identifier would stop being a sufficient description of a content set.

**Changed**
- Convention base minted as `20260724-1749/`, holding `ontology.md` alone. The root-layout depiction moved out of the ontology to `exfu/readme.md` -- it describes what the plugin ships, which is free to change. The ontology's versioning section documents the new boundary.
- `readme.md`, `principles.md`, `librarians/`, `skills/` now live at `exfu/`. Registry `source` paths stop breaking on every mint: previously each one pinned `exfu/<version>/librarians/...`, so minting silently invalidated them in every installed library.
- The 0.8.0 `dashboard.html` edits that were deferred as blocked are folded in -- the dashboard-generator librarian's `writes:` list and the layout depiction.
- New `build/check-conventions-lock.sh`, run by `build.sh` before composing: any version directory present in both HEAD and the working tree must be byte-identical. Adding a version is fine; removing a superseded one is fine. The rule was broken three times under the old scheme, so it is now a gate rather than a convention.
- New `build/mint-conventions.sh`: copies the current version to a fresh UTC timestamp, re-points every pin, removes the superseded directory. Minting is one command, so cost is never the reason to edit in place.
- Install skills, the migration skill, the substrate guide (v11), `exfu-library`, `exfu-guides`, and the wow template all describe the split shape. Bases shipped before `20260724-1749` keep the four items inside the version directory; that is the older shape and both coexist.
- `principles.md` records the Open Knowledge Format direction (see below).

**Not changed:** parsers needed no work. `index.py discover_versions()` and `dashboard-generator.py find_convention_dir()` already keyed on "a version directory containing `ontology.md`", which is exactly the new shape.

### Open Knowledge Format

Google Cloud's OKF (published 2026-06-12, v0.1) is now recorded in `principles.md` as a direction: **align now, adopt natively later, interoperate by projection.** The surface fit is close -- markdown with YAML frontmatter is already the substrate's idiom and `description` already carries OKF's meaning. Deliberately not done: no field renames (`name`/`title`, `purpose`/`description` would break the index parser, the dashboard, every template and every installed library at once), no isolated `type` field, and no one-concept-per-file. That last one genuinely contradicts the v7 decision to flatten the ontology into a single file because agents ingest one complete read far more reliably, which `Follows:` anchoring depends on. Interop does not require conformance: an importer reads public OKF bundles, a generated projection makes the library readable by OKF visualisers, and both are additive.

---

## v0.8.0 -- 2026-07-24

The dashboard gets a front door. `dashboard.html` now sits at the library root and redirects to the real page at `exfu/visualisations/dashboard/index.html`. Users open the dashboard from the top of their library instead of remembering a four-deep path, and the bundle stays in the visualisations gallery where visual outputs belong.

**Why a redirect page rather than a symlink.** Two independent reasons. Sync layers handle symlinks unreliably -- Dropbox follows them and syncs a copy, so a root symlink would freeze at whatever the generator wrote that day and silently go stale; this is the same constraint that makes `exfu/latest.txt` a text file rather than a `latest` symlink. And browsers resolve relative URLs against the document URL, not a link's target: the dashboard emits `../../../scopes/...` paths for its gallery cards and mounted scope-view iframes, so a symlinked page would resolve every one of them from the wrong depth and break them. Redirecting moves the document URL to the real location first, so those references resolve exactly as generated. The pointer also survives the dashboard growing into a multi-file bundle, which a file symlink would not.

**Changed**
- `dashboard-generator.py` maintains the pointer alongside its normal output. Idempotent: an unchanged pointer is not rewritten, so nightly runs don't churn its mtime through the sync layer. A `dashboard.html` the generator did not author (no marker comment) is left alone rather than overwritten. Pointer status is reported in the run line.
- The pointer carries three redirect mechanisms -- a script `location.replace()`, a `meta` refresh, and a visible link -- so it works with scripts disabled and degrades to one click if a browser declines both on `file://`.
- Root-layout depictions in `substrate-guide.md` (now v10) and the `exfu-library` skill gained the root entry; `exfu-guides` now tells users to open `dashboard.html` rather than the deep path.

**Note:** the pointer is created by the dashboard generator, not at install time -- a fresh install has no dashboard yet, and a root file pointing at a missing page would be a dead front door. It appears on the first dashboard run.

---

## v0.7.0 -- 2026-07-23

Project identity rename to **ExFu Agent Library**. The user-facing product label is now "ExFu Agent Library" (dropping the possessive "ExFu's"), and the three plugins are renamed to carry it:

- `exfu-solo` -> `exfu-agent-library-solo`
- `exfu-team` -> `exfu-agent-library-team`
- `exfu-team-admin` -> `exfu-agent-library-team-admin`

Renaming published plugin names is a breaking change: existing installs reference the old names, and the entries in the separate `ExFu/claude-marketplace` repo must be updated in lockstep (marketplace name `exfu-library` -> `exfu-agent-library`; install becomes `/plugin install exfu-agent-library-solo@exfu-agent-library`). The source repo is renamed `ExFu/library` -> `ExFu/agent-library`. This repo no longer carries any marketplace-sync machinery -- distribution is entirely the marketplace repo's concern. Historical changelog and planning entries keep the old names as an accurate record; only forward-facing identity was changed. No behaviour changes to the skills themselves.

---

## v0.6.2 -- 2026-07-23

Dashboard path correction, found by the agent applying a live library migration. Two skill texts still placed the dashboard at `exfu/derived/dashboard/` (the pre-0.4 location): the exfu-library substrate-layout depiction and the exfu-guides dashboard section. Both now say `exfu/visualisations/dashboard/`, matching the shipped convention base, the dashboard-generator librarian, and dashboard-generator.py. No behaviour changes.

---

## v0.6.1 -- 2026-07-23

Record correction, no behaviour changes. The 0.6.0 notes and the decision record carried an over-stated enactment claim about how installed legacy `v0.3/` bases are handled during migration; withdrawn -- that is decided in the migration session itself, on the user's instruction. The no-backwards-compatibility-machinery ruling stands.

---

## v0.6.0 -- 2026-07-23

Conventions versioning moves to timestamp identifiers. Convention-base versions are now named by their release moment -- a shortened UTC timestamp to the minute, `YYYYMMDD-HHMM` -- instead of `v0.x` labels. The two version surfaces (plugin releases, conventions releases) no longer share a naming scheme, and because every conventions release mints a fresh identifier, a version directory's contents can never again change under a stable name (the shipped `v0.3/` had been patched in place across 0.4.0, 0.5.0, and 0.5.1). Decision record: `planning/conventions-versioning-timestamps.md`.

**Changed**
- The shipped convention base is minted as `20260723-1446/` -- the first timestamped release, carrying the former shipped v0.3 contents. The ontology's versioning section now documents the scheme: lexicographic order is chronological order; `v0.x` is the legacy scheme and any timestamp identifier is newer than any `v0.x` one (never compare the two schemes by raw string sort).
- Template pins (`scope.md` frontmatter, all `Follows:` stubs, the agent-registry template) bumped to the new identifier.
- exfu-migrate-to-dropbox's convention-base refresh states how "newer" is decided across both identifier schemes.
- `index.py` version discovery and `dashboard-generator.py` convention-dir fallback recognise both identifier shapes, and their newest-version fallbacks prefer the timestamp era over legacy `v0.x`.
- Depictions and examples across exfu-library, exfu-guides, exfu-start, the install skills, install-scheduled-agent, and the substrate guide (v9) show the timestamped identifier; legacy-detection references and history stay concrete.

---

## v0.5.1 -- 2026-07-23

Version-churn-proofing. The overarching skills stop naming the convention version, so they survive a base bump without a rewrite. Prompted by a real failure: a generated wow skill hardcoded `exfu/v0.3/` paths and broke during a substrate migration.

**Changed**
- Skills, guides, and templates that *prescribe* behaviour now say `exfu/<version>/` and resolve the concrete version at read time: `exfu/latest.txt` inside a substrate, or the single version directory under `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/` inside the plugin. Genuinely version-dependent content is untouched -- scope pins, `Follows:` lines, the convention base's self-description, v0.2 migration detection, and examples that depict real file contents.
- The wow template's navigation map no longer bakes the convention version into generated wow skills.
- Install skills (solo, team, team-admin) deploy whatever convention version the plugin ships instead of hardcoding v0.3; completion checklists match.
- exfu-migrate-to-dropbox's convention-base refresh is version-aware: same version overwrites in place; a newer shipped version installs alongside and updates `latest.txt`, leaving pinned older versions in place (side-by-side model).
- Dropped drifting version labels from skill headings and script docstrings (the exfu-library heading still said v0.4.0 under the 0.5.0 plugin; the three Python helpers disagreed with each other).

**Fixed**
- The example library's wow-template copy had missed the 0.4 vocabulary rename (it still auto-loaded `substrate` instead of `exfu-library`). Synced from the shipped template.

---

## v0.5.0 -- 2026-07-22

The dashboard learns to take instructions. Interactions queue prompts instead of touching files: the Action Basket. Plus an ontology reference view, linked pointer chips, date-aware reminders, a staleness banner, and a visualisations gallery.

**Added**
- **The Action Basket.** The dashboard stays read-only about the library's files, but its controls now queue editable instructions: tick a task checkbox, mark an item for deletion, use the + New task / scope / reminder / capture forms, type into the sidebar's ask-about inputs, or press a suggest button on a guidance line. Instructions collect in a drawer (inline edit, reorder, remove; persisted in the browser per library root) and export two ways: **Copy prompt** (a complete, path-annotated prompt for any session) or **Open in Claude** (a `claude://cowork/new` deep link that prefills a Cowork session; the user still presses send; over ~13k characters the link disables and points at Copy). Queued changes render optimistically with a dashed amber "queued" style; instructions written against an older page snapshot are flagged. Nothing on disk changes until the user's AI does the work -- the basket is a prompt under construction, which is also how it teaches the conversational model.
- **How it works view.** The core ontology rendered as a visual reference: the folder-type catalogue as a card grid, every section of `ontology.md` readable in collapsibles. The sidebar now also surfaces each scope's own `ontology/` files alongside `context/`.
- **Gallery.** Your scopes now ends with every visualisation bundle across scopes (with or without a `viz.md` manifest), linked to open; `view: true` bundles still mount as top-level tabs.
- **Staleness banner.** When the index behind the page is older than 36 hours, a banner says so and offers to queue a refresh instruction.

**Changed**
- Pointer chips ("Managed in ClickUp") become real links when the folder's own agent.md names a URL -- never fabricated. The sidebar detail gains an "Open in your tool" button.
- Reminders group by urgency: Overdue (red), Coming up within 7 days (amber), then the rest as written. ISO dates are parsed best-effort; entries without one render exactly as before. Bullet-entry titles shed their checkbox markers and leading dates.
- The example library now demonstrates the new surfaces out of the box: dated reminders, an inbox capture with triage status, and a ClickUp board URL on the pointer todo.

**Fixed**
- Removed two stray duplicate definitions of `grouping_label`/`hint` in dashboard-generator.py left behind by an earlier editing pass, and synced the example's dashboard-generator librarian definition to the v0.3.1 gallery placement it had missed.
- `skill-packaging` delivery is now surface-aware. The `computer:///` link + Save Skill flow only works in Cowork chat; in Claude Code (the CLI, or the Claude Code view inside Claude Desktop) file links render but do nothing, so the skill now says: open the containing folder for the user and point them at Settings -> Capabilities -> Skills -> Upload skill (or a Cowork session). Packages are written to a space-free path (spaces broke link handling). Its bedrock-skill list also caught up with the 0.4 vocabulary: exfu-library etc., with the setup-generated per-user skills delivered like custom skills.

---

## v0.4.0 -- 2026-07-20

The Agent Library release: the pitch is renamed, the plumbing is not; and storage moves from Box to Dropbox.

**Changed**
- **Two-register vocabulary.** User-facing, the product is now **ExFu's Agent Library**, kept organised by **Agent Librarians** (always plural -- an ecosystem the user appeals to, never a single all-knowing character; a scope may be taught as a "shelf", an analogy, not a rename). "Substrate" is retained as the internal register: the implementation vocabulary agents use in files and with each other. Defined once in `ontology.md#vocabulary`; carried through the primers, the guide, the install conversations, plugin manifests, and the dashboard ("<name>'s library"). No structural renames: folders, anchors, resource filenames, and scope.md machinery are unchanged.
- **Boot skill renamed `substrate` -> `exfu-library`.** The front-door skill name was the worst cross-plugin collision risk; the `exfu-` prefix is the naming convention for new and replaced skills from 0.4 onward. The CLAUDE.md guard's canonical text now names `exfu-library` and describes the folder as an Agent Library root. All references updated (wow template, install skills, templates, guides).
- **Dropbox replaces Box as the solo storage default and the team cloud-folder path.** The Dropbox connector supports delete, move, and copy natively by path, with per-file revision history -- so the entire Box workaround layer is deleted rather than ported. New shared skill `exfu-dropbox-storage` (access modes, conflicted-copy handling, hydration and symlink caveats); `team-box-folder-provisioning` becomes `team-dropbox-folder-provisioning`; the compliance briefing's storage sections now describe Dropbox; the exfu-library skill detects Dropbox-backed roots and treats Box-backed roots as legacy pending migration.
- Substrate guide bumped to v8: two-register note, Dropbox access modes, corrected dashboard path (`exfu/visualisations/dashboard/`), fixed a stale version header. The human primer (`the-substrate-primer.md`, now titled "The Agent Library Primer") sheds its outdated v0.2 PII-layer and orgs/teams passages.

**Added**
- **`exfu-migrate-to-dropbox`** -- the 0.4 upgrade path: verifies the user's Dropbox copy against the Box original (which becomes a read-only fallback, never modified), refreshes the deployed convention base, rewrites the guard, retires `_trash/`/`_DELETED_`/box-cleanup artefacts, updates the wow's paths and glosses, records the storage change, and emits the account-side checklist (Global Instructions path, connectors, scheduled-task prompts, personal skills).

**Removed**
- `box-filesystem-management`, `team-box-folders`, and the solo `box-cleanup` scheduled task (with its `_trash/` + `_DELETED_` + 60-day purge machinery). Deletes are real deletes now, with Dropbox's own trash and revision history as the safety net.

---

## v0.3.4 -- 2026-06-12

The dashboard's big interface release: the Grounded Editorial design system, a split-pane reading layout, item-level workspace views, and second-brain style graphs.

**Added**
- **View registry with pluggable scope views.** Tabs generate from a registry: Your scopes, Agents, and Todos / Reminders / Inbox as their own top-level views. Any scope's `visualisations/<name>/` bundle with a `viz.md` manifest declaring `view: true` mounts automatically as a tab (relative iframe). The example substrate demonstrates it ("Trend snapshot" from the side-project scope).
- **Everything is a card with a story.** Tasks, reminders (split per entry from their files: headings first, then bullets, then whole-file), and inbox captures render as individual cards; clicking any card, agent, or graph node opens its detail in the reading panel.
- **Split-pane layout.** The detail panel is always open on the right (default half the window), resizable by dragging its edge (width remembered). It greets with the personal scope.
- **Second-brain graphs.** The scope and agent maps follow the conventions of tools like Obsidian: small dots sized by connections, thin straight edges, hover highlights the node's neighbourhood and dims the rest, wheel zoom, background pan, a gently continuous force layout, and draggable nodes that spring back when released. Honours `prefers-reduced-motion`.
- Filesystem links open in a new tab; nothing truncates for good (overflow folds into expanders).

**Changed**
- Full design pass applying the website's Grounded Editorial language: Source Serif 4 display (embedded; the woff2 ships with the plugin -- no network fetches) over a humanist text stack, the site's paper/ink/rust palette, an editorial left-aligned header ("<name>'s substrate"), scope cards in a responsive grid with the personal scope as hero, grouping folders as labelled container boxes, paper grain, staggered entrances.
- Dashboard copy says "your AI" (Claude only in explicitly-Claude examples) -- carried through all new views.

---

## v0.3.3 -- 2026-06-10

**Changed**
- Install conversations get a pacing and consent model ("How to begin", replacing "start moving"). The previous instruction read "their go is implicit... begin immediately, then continue through the steps in order" -- which licensed silent multi-step execution and writing into the user's folders before any dialogue. Now: the first message answers what the user actually asked, sketches the shape of the install, and proposes the first move; reading is free, the first write needs an explicit yes, the user's own content is propose-then-do, and a direct question is always answered before tools fire. One step at a time, narrated. Matching must-never constraint ("Don't execute silently") in all three variants.

---

## v0.3.2 -- 2026-06-10

**Changed**
- Install conversations now carry a "How to talk to the user" contract, applied from the first message: golden circle with the outcome first, internal vocabulary earned one term at a time (the brand terms "substrate" and "wow" are used freely but glossed in layman language on first use), a say-this-not-that translation table, and no plan-dump openings. Compact versions in exfu-start, scope-setup, and the substrate skill.
- Routing for kept content stated positively everywhere: reference documents (PDFs, spreadsheets, transcripts, exports) are context with a file extension and live in `context/`; repeating records live in `databases/`. A shipped librarian definition and several resources that still suggested pre-v0.3 destinations were corrected.
- `team-repo-provisioning` and `team-box-folder-provisioning` no longer seed structure: they end where content begins (repo or folder created, access configured, clone verified), and the install conversation seeds the substrate against the current conventions.

**Fixed**
- Marketplace upload validation: SKILL.md frontmatter that failed YAML parsing (unquoted ": " in descriptions) and a description over the 1024-character server limit. build.sh now enforces YAML parseability, the length cap, and the no-XML rule locally.

**Removed**
- `pii-layer-guidance.md` (a v0.2 resource superseded by the v0.3 secrets-only data rule).

---

## v0.3.1 -- 2026-06-10

**Added**
- Substrate dashboard v2–v4, generated by the dashboard-generator librarian into `exfu/visualisations/dashboard/index.html`: List/Map view toggles on the scopes and agents tabs; dependency-free radial map (the user at the centre, scopes radiating out; agents hub-and-spoke off their scopes) with node-type filters; click-to-open sidebar on every node and list card showing purpose, About (scope.md body), capped `context/` excerpts (the folder's readme.md first), folder-type dots, agents, children, and a `file://` path link with a copy button; grouping folders as container boxes in the list view; agents tab split into the user's agents (grouped by scope, collapsible) and ExFu's own (collapsed, at the bottom); "Found, not installed" section surfacing staged definitions; guidance lines and "?" hints explaining scopes, agents, and grouping folders in place.

**Changed**
- Dashboard output moved from `exfu/derived/dashboard/` to the visualisations gallery (`exfu/visualisations/dashboard/`); `ontology.md` and the librarian definition updated to match. The generator reads `agent-registry.json`/`agent-log.json` and falls back to the pre-rename `librarian-*` filenames for substrates that predate the scheduled-agent vocabulary.
- Dashboard copy refers to "your AI" rather than Claude, except where something is genuinely Claude-specific (e.g. Claude Cowork Scheduled tasks as an example).

---

## v0.3.0 -- 2026-06-09

Recorded retrospectively; the v0.3.0 zips shipped without a changelog entry.

**Changed**
- M2 substrate redesign: scope-based model (scope.md boundary markers, nesting via `scopes/`, grouping folders), versioned convention base at `exfu/v0.3/` with a single-file anchor-addressed core ontology (`ontology.md`), materialise-on-demand folder-types (kept documents live in `context/`), and the scheduled-agent framework -- librarians (substrate remit, `librarians/`) plus business agents (domain remit, `scheduled/`), one registry (`exfu/derived/agent-registry.json`), one run log, helper scripts under `scheduled-tasks/scheduled-agents/`.
- All three install skills rewritten for the v0.3 model; sane-default templates added for todo, reminders, and inbox.

---

## v0.2.8 -- 2026-05-07

**Changed**
- Substrate skill Step 1: when the substrate isn't accessible in the current session, the skill now invokes the working-folder picker (`request_cowork_directory`) directly rather than asking the user in text to add it. Hard constraint #6 added: never proceed without substrate access; no fallback to inference, guessed structure, or working from memory of prior sessions.
- The `inbox`, `reminders`, and `writing-styles` skills have been split. The plugin now ships `setup-inbox`, `setup-reminders`, and `setup-writing-styles` -- setup skills that capture user preferences and generate a per-user skill (`<username>-inbox`, `<username>-reminders`, `<username>-writing-styles`) that handles ongoing operations. The operational content lives in templates at `${CLAUDE_PLUGIN_ROOT}/templates/<name>-template.md`. Pattern parallel to how `exfu-create-wow` produces the `wow` skill. The substrate skill (Step 10) now delegates to whatever `*-reminders` or `*-inbox` skill is loaded in the session, rather than looking for the old generic names.

**Added**
- This CHANGELOG.md, for future-agent reference.

---

## v0.2.6 -- 2026-05-07

**Added**
- New `substrate-index` scheduled task (`shared/scheduled-tasks/substrate-index/`). Stdlib-only Python script walks every folder (skipping system folders, `_trash/`, `_meta/`), extracts Purpose + Contents from each README, writes `_meta/substrate-index.md`. Folder-only output, no allowlist; novel folders surfaced honestly. Caps fields at 120 chars, total at 50 KB.
- `exfu-create-wow` skill: substrate-index registration is now a baseline part of every wow generation. Skill runs the indexer once on the spot for an immediate first index, creates the recurring scheduled task, hands it to the user for install. Not a buffet item.

**Changed**
- Substrate skill Step 4 now requires reading `_meta/substrate-index.md` on every load. Flags absence to the user with a clear remedy (register the scheduled task, or run the script manually).
- `wow-template` gets a brief note: editorial layer (curated pointers) versus comprehensive layer (machine-walked nightly index).

---

## v0.2.5 -- 2026-05-07

**Added**
- `_meta/storage-backend.md` handshake: install skills write a canonical record of the chosen storage backend (`git`, `box`, or `local`) at the substrate root. Substrate skill reads it on every session start to decide which verb vocabulary and storage-skill delegation to use.

**Changed**
- Substrate skill Step 1.5 detects storage backend from the handshake file (with inference fallback from `.git/` presence or Box-mount path heuristics).
- Substrate skill Step 7 generalised with explicit subsections for git-backed, Box-backed, and local-only substrates. Each backend gets backend-appropriate verb vocabulary; the git-specific verb table is preserved but scoped clearly.
- Substrate skill ongoing-behaviour: storage-skill delegation rule per backend (`git-substrate-sync` for git, `box-filesystem-management` plus `team-box-folders` for Box, direct filesystem for local-only).
- All 3 install skills now write `_meta/storage-backend.md` after capturing the storage choice. Records also land in the wow navigation map for human-readable context.

---

## v0.2.4 -- 2026-05-07

**Added**
- New `team-box-folders` skill (in `shared/skills/`, excluded from solo via build script). For team members and admins to organically create scope folders, share with colleagues, manage access. Covers the multi-folder reality of Box team substrates (per-org, per-team, per-scope sharing groups).

**Changed**
- `team-box-folder-provisioning`: removed the "if these dealbreakers, consider git" trade-off section. Decontamination principle: Box-using teams shouldn't see git referenced in their storage skills, and vice versa. Install entrypoints still mention all options because that's where the choice is made.
- `box-filesystem-management` moved from `solo/skills/` to `shared/skills/`. Now ships in all 3 plugins so Box is a real option for team contexts.
- Install-team Step 5 and install-team-admin Step 6 now offer three storage paths: git, Box shared folder, local-only.
- `cross-cut-storage-architecture.md` (planning) rewritten for the 3-option model with trade-off table and multi-folder Box explanation.
- `compliance-briefing.md` augmented with backend-specific commentary throughout: data flow, controls, ISO 27001 table notes, audit trail, backup, and access control all now cover git, Box, and local-only.

---

## v0.2.1 -- 2026-05-05

**Changed**
- Plugin distribution format switched from `.tar.gz` to `.zip`. Build script writes versioned archives directly to `public/downloads/`.
- `install.astro` page: archive section populated with v0.2.0 entries.

---

## v0.2.0 -- 2026-05-05

**Added** (initial v0.2.0 release; substantive substrate model revision)
- Three-plugin split: `exfu-solo`, `exfu-team`, `exfu-team-admin`. Hard separation at plugin boundary; team-admin is a strict capability superset of team but installed separately so capability doesn't leak.
- `substrate-guide.md` v5: top-level `orgs/` and `teams/` siblings, top-level `scopes/`, hard `context/` convention, two-layer model (substrate proper plus PII layer), CLAUDE.md guard at substrate root, permission-aware verb surfacing, non-techie verb vocabulary.
- New `the-substrate-primer.md`: human-facing pre-install reading. Covers the four ingredients, discoverability asymmetry, build-by-doing, chief-of-staff framing.
- New `exfu-primer.md`: human-facing intro to what ExFu is.
- New `pii-layer-guidance.md`: framework-agnostic guidance for the two-layer model. Contract shape only; implementations are wrapping-plugin territory.
- New `ecosystem-references.md`: catalogue of Anthropic and community resources, plus deep-research-as-a-move pattern.
- New `teaching-artefacts.md`: catalogue of diagrams that ship with the plugins.
- New `cross-cut-extension-and-wrapping.md` (planning): meta-principle that ExFu provides patterns; wrapping plugins (one per org, typically) or the installing Claude resolve org-specific decisions.
- New `compliance-briefing.md` (team-admin only): material the substrate champion can hand to IT or security teams.
- `exfu-start` orchestrator: first-run detection. New users get the install entrypoint loaded immediately, no triage menu.
- 3 install entrypoints (one per variant) with multi-org/team question and CLAUDE.md guard creation.
- New admin-only skills in team-admin: `team-repo-provisioning`, `team-shared-skills-authoring`, `team-onboard-member`, `exfu-upgrade-from-team-to-admin`.
- New `git-substrate-sync` skill (shared, excluded from solo): wraps git operations safely for substrate use.
- New `exfu-migrate-from-fetch-model` skill: handles the upgrade path from the previous fetch-from-URL install model.

**Changed**
- All 18 SKILL.md files: descriptions rewritten with thicker context (a Claude reading them cold has enough grounding) and real-user-language triggers (verbs and substance, not insider vocabulary). Bodies that lacked Why got a Why sentence added.
- Substrate skill rewritten (98 → 265 lines): boot reads new v5 layout, creates CLAUDE.md guard at substrate root, multi-org/team aware, expects optional permission lookup and PII connector from wrapping plugin or install.
- Author field corrected to `Alastair Brayne` across all manifests and references (was `Whaley`, derived incorrectly from the company name `WhaleyBear Ltd`).

---

## v0.1.0 -- 2026-05-02

Initial 3-plugin release. Replaces the previous fetch-from-URL install model with a self-contained Claude Code plugin install model.

**Added**
- exfu-solo: 11 skills including `box-filesystem-management` for solo storage.
- exfu-team: 11 skills, `git-substrate-sync` as the team storage skill.
- exfu-team-admin: 15 skills, including `team-repo-provisioning` and other admin-only skills.
- Skills, resources, and templates ported from the previous fetch-from-URL install model.
- Build pipeline (`plugin/build/build.sh`) with shared-plus-variant composition and `--dist` zip generation.
- `install.astro` page with 3-plugin decision helper.
