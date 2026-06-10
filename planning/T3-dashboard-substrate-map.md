# T3 -- Dashboard substrate map view

The "what do I have?" view: every scope as a card, arranged by relationship, with folder-type population at a glance. A conceptual map, not a file tree.

**Parents:** `T2-exfu-dashboard.md` (domain), `M2.1-exfu-dashboard.md` (milestone)
**Prerequisites:** T3-nightly-index (complete), T3-dashboard-generation (pipeline)
**Status:** v2 built 10 June 2026 from Al's review. The list view gained container boxes for grouping folders, a dot legend, and plain-language labels; and a second presentation landed: a radial map (you at the centre, scopes radiating out, grouping folders and agents as toggleable node types) with a click-to-open node sidebar and a List/Map toggle. Sections 2-4 below are delivered; 5-6 stand.

---

## Why

A returning user's first question is "what have I built?". Reading scope.md files one at a time answers it slowly and without shape. The map answers it in one glance, and doubles as the proof-of-concept artefact Al shows prospects: this is what an installed substrate looks like.

The map must stay conceptual. The moment it looks like a filesystem tree, it stops teaching "scopes are bounded working contexts" and starts teaching "it's just folders".

---

## What to build

### 1. Scope cards (v1, keep)

Each scope renders as a card: name, purpose (from the index, enriched from `scope.md` frontmatter when the index lacks it), version pin badge, and one dot per populated folder-type. The user scope is visually distinct (warm highlight, "personal" badge) -- it is the personal layer, not just another scope. Child scopes nest inside their parent's card area with an indent line, read as "contained", not "indented path".

### 2. Legend for the dots (gap)

Green means data lives here; blue means this folder points at an external system; both are currently unexplained. Add a one-line legend at the top of the view ("filled here / managed elsewhere" in plain words). A non-technical user must never have to infer a colour code.

### 3. Grouping folders made visible (gap)

Plain grouping folders (directories under `scopes/` with no `scope.md`, e.g. `clients/`) are flattened by the index: Swoop and ZapMap show parent "root" though they live at `scopes/clients/`. The map should show the grouping lightly -- an eyebrow label on the card (e.g. "clients /") or a soft group heading, derived from the path segments between `scopes/` and the scope directory. Light touch only: grouping folders organise, they are not scopes, and must not render as cards.

### 4. Plain-language labels (gap)

Per the T2's visual language: no jargon in labels. The tab currently reads "Substrate Map"; prefer "Your scopes". The versions line ("ExFu versions: v0.3 (latest) -- 10 scope(s)") becomes a sentence a person would say ("Conventions: ExFu v0.3, the latest -- used by 10 scopes"). The exfu/ convention base never renders as a peer card; it appears only in this conventions line.

### 5. Empty folder-types stay hidden (decision)

The index records only populated folder-types per scope; the map renders only those. A row of grey "empty" dots on every card is noise, not information. A scope with nothing yet shows name and purpose alone -- that emptiness is honest and visible enough.

### 6. Graph view (built 10 June 2026)

A second way of seeing the same answer: a radial SVG map, dependency-free, drawn client-side from data embedded in the page. You sit at the centre; top-level scopes ring you; grouping folders are dashed waypoint nodes with their scopes fanned beyond; nested scopes chain outward; agents (off by default) hang off their scopes as small health-coloured nodes. Filter checkboxes show or hide node types. Clicking any node opens a sidebar: purpose, an About section (the scope.md body plus a root readme.md when present), path, conventions pin, folder-type dots, agents, children, capped excerpts of the scope's context/ files (the folder's readme.md first, each in its own collapsible), and one guidance line ("ask Claude about this scope by name"). The path renders as a `file://` link (Safari opens the folder in Finder; Chromium browsers show a navigable listing) with a copy button beside it; one-click reveal-in-Finder arrives with the action server (`T3-dashboard-actions.md`). List cards open the same sidebar on click, so both views reach the same depth. List and map are peers behind a List/Map toggle.

### 7. Responsive behaviour

Cards stack to a single column on narrow screens (a 700px breakpoint exists in v1); verify dot rows wrap rather than overflow, and nested cards keep their containment reading on mobile. Users will open this on a phone.

---

## Acceptance criteria

1. A non-technical user can answer "what scopes do I have, what is each for, and what's in it?" within thirty seconds of opening the view.
2. The dot colour code is explained on the page, in plain words.
3. Nested scopes and grouped scopes are visually distinct from top-level scopes, without the view reading as a file tree.
4. No jargon in any label a user sees.
5. The view renders correctly with only `index.json` present (no registry, no log).
6. The map is legible on a phone-width screen.

---

## Files to create/modify

- Modify: `plugin/src/shared/scheduled-tasks/scheduled-agents/dashboard-generator.py` (`render_substrate_map`, `render_scope_card`, CSS)
- Possibly modify: `plugin/src/shared/scheduled-tasks/substrate-index/index.py` (surface grouping-folder path segments if card rendering needs them explicitly)

Paths as of commit 2d592bb (the M2 conventions revision).

---

## Where this plan lives

- This file: `plugin/planning/T3-dashboard-substrate-map.md`
- Domain: `plugin/planning/T2-exfu-dashboard.md`
- Milestone: `plugin/planning/M2.1-exfu-dashboard.md`
- Pipeline: `T3-dashboard-generation.md`
