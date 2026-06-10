# T3 -- Dashboard generation pipeline

The pipeline that turns derived substrate data into the dashboard: what the generator reads, what it writes, where the output lives, and the freshness contract with the librarian framework.

**Parents:** `T2-exfu-dashboard.md` (domain), `M2.1-exfu-dashboard.md` (milestone)
**Prerequisites:** T3-nightly-index (complete), T3-librarian-definitions (registry and log formats; live in prototype)
**Status:** v1 exists. `dashboard-generator.py` (~1,150 lines, in the plugin's scheduled-tasks bundle alongside the nightly librarian runner) was built during M2 phase 2 prototyping and ran clean against a real 11-scope substrate on 10 June 2026. This plan records the architectural decisions v1 embodies and specifies the gap to done.

---

## Why

The dashboard is only trustworthy if its generation is boring: deterministic, dependency-free, safe to run at any moment, and honest about how fresh its data is. Assembling HTML from JSON is exactly the kind of work that should be a script, not agent judgement -- the librarian inversion (commit 6e918eb) holds here: the librarian definition instructs the agent, and this script is the tool the agent runs.

The pipeline decisions also settle a placement question the T2 left open, and fix a freshness bug the v1 prototype surfaced on its first real run.

---

## Decisions this plan records

### 1. Output lives in the visualisations gallery: `exfu/visualisations/dashboard/`

The dashboard is the first ExFu-shipped visualisation, and it lives where visualisations live. The artefact splits in two:

- **App bundle** -- `exfu/visualisations/dashboard/index.html` (plus assets if it ever needs them). Stable: the generator writes it only when missing or when the plugin ships a newer dashboard version.
- **Data file** -- `exfu/visualisations/dashboard/dashboard-data.js`, rewritten on every run. The page loads it with a relative `<script src>` tag, which works from `file://` (it is `fetch()` that local CORS blocks, not script tags).

`exfu/derived/` remains the machine-state *source* (index, registry, log) that the data file is built from; no dashboard artefact lives there. The path is unversioned so a user's bookmark or desktop shortcut survives convention-base upgrades.

History, for future agents: the first pass of this plan placed the whole generated file at `exfu/derived/dashboard/index.html` on regenerable-state grounds (and the v1 prototype wrote there). Al's review the same day reversed it: the gallery is literally what `visualisations/` is for, derived/ shouldn't come into it, and the bundle split removes the "nightly-overwritten file in a curated gallery" objection -- only the data file churns. The earlier supersession note in the T2 was superseded in turn; the T2 now records this decision.

### 2. A self-contained bundle, stdlib only

- The app is a single HTML file with embedded CSS and JavaScript; data arrives via the adjacent data file. No external requests, no fonts fetched, no CDN. It must open from `file://`, offline, on any machine.
- The generator uses only the Python standard library. No pip installs on user machines, ever.
- The two-file bundle keeps Box/git sync and "open this file" instructions trivial, and makes refresh cheap: rewriting kilobytes of data, not reassembling the page. (v1 shipped as one fully-embedded file; the split is part of the gap to done.)

### 3. Data contract

The generator reads, all relative to the substrate root:

- `exfu/derived/index.json` -- scope tree, folder-type population, version pins
- `exfu/derived/agent-registry.json` -- registered scheduled agents (librarians and business agents, distinguished by `kind`) and their health state
- `exfu/derived/agent-log.json` -- recent run outcomes
- Scope folder content (todo/, reminders/, inbox/) read directly at generation time, for the workspace views

Every input is optional. A missing or unparseable file degrades that view to a friendly empty state; it never aborts the run. (v1 satisfies this.)

**The index is the single classifier.** v1 duplicates the data-vs-pointer detection heuristic from `index.py` inside the generator. Remove it: the generator trusts the index's `folder_types` classification and only reads folder content for *rendering*. One heuristic, one home; if classification improves, it improves in `index.py` and the dashboard follows.

### 4. Freshness contract and the self-staleness fix

v1's first real run exposed a sequencing bug: the dashboard rendered the registry as it stood *before* the same night's sibling librarians were recorded, so the fresh dashboard reported "Not yet run" for librarians that had just succeeded -- including itself.

The fix is a contract plus one special case:

- **Cadence contract:** the nightly session records each scheduled agent's outcome immediately after it completes, before starting the next (`agents.py record`). The dashboard-generator definition already says "run last in the cadence"; keep that.
- **Self-awareness:** the generator knows its own name. It renders its own registry entry as "this run -- generating now" rather than reporting itself stale. It must not fabricate state for any *other* librarian.
- **Honest timestamps:** header shows when the dashboard was generated; footer shows when the index it rendered was generated. (v1 satisfies this.)

### 5. On-demand refresh

The script is idempotent and runs in well under a second, so it is safe to invoke at any moment. The user-facing "refresh my dashboard" verb belongs to the substrate skill rewrite (`T3-substrate-skill-rewrite.md`), which should point at this script; nothing extra is built here.

### 6. Non-goals

Unchanged from the T2 and milestone: no interactivity beyond view switching, no live updates, no hosting or auth, no multi-substrate aggregation (each substrate gets its own dashboard).

---

## Acceptance criteria

1. App bundle at `exfu/visualisations/dashboard/index.html` with `dashboard-data.js` alongside; opens from `file://` with no network access and renders correctly.
2. A data-only refresh rewrites `dashboard-data.js` without touching `index.html`; the generator (re)writes the app file only when missing or version-bumped.
3. Generator runs on a bare Python 3 install (stdlib only) and completes in under a second on a ~dozen-scope substrate.
4. Any subset of the three JSON inputs may be missing; each absent input produces its view's empty state and the run still succeeds.
5. No data-vs-pointer classification logic remains in the generator; it consumes the index's classification.
6. Generated the night after a full cadence run, the dashboard shows every sibling librarian's outcome from that run, and shows itself as "this run", not stale.
7. The T2's placement section points here so no future agent builds against a superseded path.

---

## Files to create/modify

- Modify: `plugin/src/shared/scheduled-tasks/scheduled-agents/dashboard-generator.py` (bundle split, output path, single-classifier cleanup, self-awareness fix)
- Modify: `plugin/src/shared/substrate/exfu/v0.3/librarians/dashboard-generator.md` (writes: path, record-then-next contract wording)
- Modify: `plugin/src/shared/substrate/exfu/v0.3/ontology.md` -- **coordination needed**: its `#visualisations` section and the two `derived/` layout mentions currently state the dashboard lives at `exfu/derived/dashboard/` "because it's regenerated cache". That sentence predates this placement decision (the two work streams briefly held opposite instructions on 10 June); update it to the gallery placement when implementing, coordinating with whoever holds the convention base at the time.
- Modify: `plugin/planning/T2-exfu-dashboard.md` (placement note pointing at this decision -- done)

Paths as of commit 2d592bb (the M2 conventions revision).

---

## Where this plan lives

- This file: `plugin/planning/T3-dashboard-generation.md`
- Domain: `plugin/planning/T2-exfu-dashboard.md`
- Milestone: `plugin/planning/M2.1-exfu-dashboard.md`
- Sibling views: `T3-dashboard-substrate-map.md`, `T3-dashboard-librarian-view.md`, `T3-dashboard-workspace-views.md`
