---
name: weekly-trends-scan
cadence: weekly
reads:
  - "scopes/side-project/context/"
writes:
  - "scopes/side-project/context/trends-notes.md"
depends_on: []
description: Scans recipe and food-tech communities for ideas relevant to the recipe engine and appends notable ones to the trends notes
---

# Weekly trends scan

A business agent (not a librarian: its remit is the project, not the substrate). Once a week, look for anything new and relevant to the recipe engine.

## Instructions

1. Read `scopes/side-project/context/project-brief.md` for what the project is and what counts as relevant.
2. Search the web for the past week's notable items: new recipe datasets, embedding tricks for ingredient matching, food-tech side projects that got traction.
3. Append a short dated section to `scopes/side-project/context/trends-notes.md` (create it on first run): three to five bullets, one line each, with links. No essays.
4. If nothing genuinely relevant surfaced, append a one-line dated entry saying the week was quiet -- a quiet week is a valid result.
5. In your detail line when recording, give the bullet count (e.g. "4 items noted").

## What it touches

- Reads: the project brief and existing trends notes
- Writes: `scopes/side-project/context/trends-notes.md` (append-only)
