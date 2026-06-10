# T3 -- Dashboard librarian view

The "is it healthy?" view: registered librarians with health status, run history, and warnings for definitions that exist but were never installed.

**Parents:** `T2-exfu-dashboard.md` (domain), `M2.1-exfu-dashboard.md` (milestone)
**Prerequisites:** T3-dashboard-generation (pipeline); the scheduled-agent registry and log (landed in the M2 conventions revision: `exfu/derived/agent-registry.json` + `agent-log.json`, entries carry `kind: librarian | agent`)
**Status:** v2 built 10 June 2026 from Al's review. Your agents lead the view, grouped by scope in collapsible sections (open by default); ExFu's own agents sit collapsed at the bottom -- housekeeping, not headline. The unregistered warning, "this run" self-awareness, disabled dimming, a cadence status strip, and a radial map view (agents hanging off the scopes they work for, with kind filters) all render. Guidance copy explains how to create an agent; ? hints explain what agents and librarians are.

---

## Why

Librarians run overnight, unwatched. Without a visual signal the user has to trust that everything worked, and trust doesn't scale past the first silent failure. This view turns the registry and log into a glanceable answer to "did last night work, and is anything quietly broken?"

It also closes a subtler gap: work that was *defined but never installed*. A librarian definition sitting unregistered in a scope is invisible everywhere today -- the registry doesn't know it, so nothing surfaces it. (Live example: the mx5-scanner definition written during the substrate migration, deliberately left unregistered.) The dashboard is the natural place to make that state visible.

---

## What to build

### 1. Health semantics (v1, document as the contract)

Derived from registry fields, rendered as a coloured dot plus badge:

- **Healthy** -- last run succeeded, no consecutive failures
- **Warning** -- 1-2 consecutive failures, or last run failed
- **Failing** -- 3+ consecutive failures
- **Unknown** -- never run
- **Disabled** -- `enabled: false` in the registry

Cards group by cadence, with the cadence's own last-run shown in the group header. Warm palette throughout: green/amber/red as defined in the generator's CSS variables.

### 2. Unregistered definitions warning (gap -- the T2 requires it, v1 lacks it)

The generator scans for scheduled-agent definition files (markdown with `name:` frontmatter) in the convention base's `librarians/` folder and in each scope's `librarians/` and `scheduled/` folders, using scope paths from the index. Any definition whose name is absent from the registry renders as a dimmed card with a "found, not installed" badge and a plain hint ("ask Claude to install it"). This is a warning, not an error -- unregistered is a legitimate resting state, as mx5-scanner shows.

### 3. Disabled rendering (partial gap)

v1 labels disabled librarians but renders them at full strength. Dim the whole card so the eye reads "deliberately off" before the label is read.

### 4. "This run" self-awareness (gap, shared with the pipeline plan)

The dashboard generator renders itself honestly: its own entry shows "this run -- generating now" instead of stale last-run data. Sibling freshness is solved by the cadence contract (record each outcome before the next librarian starts; dashboard runs last) -- see `T3-dashboard-generation.md`, decision 4. This view must never fabricate state for other librarians.

### 5. Run history (v1, refine)

The recent-runs list shows the last 15 outcomes, newest first: status dot, cadence, timestamp, name, one-line detail. Keep it flat and terse -- it is a reassurance trail, not a log viewer. If the log grows structured run-grouping later, group visually by night; do not build that structure here.

### 6. Both kinds of scheduled agent (vocabulary landed)

The M2 conventions revision settled the vocabulary: scheduled agents come in two kinds -- librarians (substrate remit) and business agents (domain remit, in `scheduled/` folders) -- sharing one registry. The view covers both, grouped by kind within each cadence, librarians first (mirroring run order). Plain-language labels at build time; the dashboard never invents terms the substrate doesn't teach.

---

## Acceptance criteria

1. At a glance, a user can answer: did last night's run work, is anything failing repeatedly, and is anything switched off?
2. A definition file present in the substrate but absent from the registry appears as "found, not installed" -- verified against a substrate carrying an unregistered definition.
3. Disabled librarians are visibly dimmed.
4. The morning after a clean cadence run, every librarian in that run shows that run's outcome; the generator shows itself as "this run".
5. The view renders a friendly empty state when no registry exists, and a "registered but nothing has run" state when the log is empty.

---

## Files to create/modify

- Modify: `plugin/src/shared/scheduled-tasks/scheduled-agents/dashboard-generator.py` (`render_librarian_dashboard`, `render_librarian_card`, definition scan, CSS)

Paths as of commit 2d592bb (the M2 conventions revision).

---

## Where this plan lives

- This file: `plugin/planning/T3-dashboard-librarian-view.md`
- Domain: `plugin/planning/T2-exfu-dashboard.md`
- Milestone: `plugin/planning/M2.1-exfu-dashboard.md`
- Pipeline: `T3-dashboard-generation.md`
