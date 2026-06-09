# Folder type: visualisations/

Agent-created visual outputs for this scope. HTML builds, web views, interactive content, charts, diagrams -- anything an agent produces that's meant to be viewed in a browser or visual tool.

**Analogy:** a gallery.

## Default behaviour

When an agent creates visual output (an HTML page, an interactive dashboard, a chart), it goes here. Each visualisation lives in its own subfolder with all its assets. The folder name describes what the visualisation shows.

The first ExFu-shipped visualisation is the substrate map: an HTML view of the global index that gives non-technical users a visual overview of their substrate.

## Store-or-point

- **Stored:** HTML files, associated CSS/JS, images, data files. Each visualisation in its own subfolder.
- **Pointer:** "Dashboards live in Looker at [URL]. This folder tracks what's been built and where to find it."

## Boundaries

- Visualisations are *visual outputs*. Source data goes in databases/. Documents go in docs/. Skill definitions go in skills/.
- No particular constraint on what visualisations look like. The folder is a conventional place to put them, not a format requirement.
