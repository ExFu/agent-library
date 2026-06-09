# Visualisations

## Why

Agents create visual output -- HTML dashboards, interactive charts, reports meant for browsers. Without a conventional home, these scatter across the substrate or get lost in temporary directories.

## How

Each visualisation lives in its own subfolder with all its assets (HTML, CSS, JS, images, data files). The folder name describes what the visualisation shows.

The ExFu convention base ships the substrate map visualisation: an HTML view of the global index for non-technical users.

### Store-or-point

- **Stored:** HTML files and assets, each visualisation in its own subfolder.
- **Pointer:** "Dashboards live in Looker at [URL]. This folder tracks what's been built."

### Boundaries

- Visualisations are *visual outputs*. Source data goes in databases/. Documents go in docs/. Skill definitions go in skills/.
- No format constraints. HTML is typical, but anything visual belongs here.

## What an agent should do

1. Create visualisations in subfolders with descriptive names.
2. Include all assets so the visualisation works standalone (no external dependencies).
3. When updating a visualisation, overwrite in place rather than creating duplicates.
