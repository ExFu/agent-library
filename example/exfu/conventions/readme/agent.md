---
convention: readme
applies-to: all-folders
copy-on-create: true
---

# Convention: README.md per folder

## Why

Discoverability without a central index. When the agent (or a human) lands in a folder cold, the README orients them in seconds: what is this for, what is here, what does it connect to. No README, no orientation; the folder becomes opaque and stale within weeks.

## How

Every folder in the substrate has a `README.md` with three sections, in this order:

1. **Purpose** — one or two sentences on what this folder is for. The Why.
2. **Contents** — overview of what is inside. Brief; not an exhaustive listing.
3. **Dependencies** — other folders or files in the substrate that this folder relates to or depends on. Optional if there are none, but include the section header anyway with "None" underneath if so.

Plain language. Short. No clever formatting. The README is read often and should not punish the reader.

The agent maintains the README as the folder's contents evolve. When a new dependency is created (a file here references a file there), update both READMEs.

## What

For any new folder the agent creates, write the README immediately. Do not defer; an unREADMEd folder is a discoverability hole.

For folders that should also be agent-facing in a structured way (scope folders, typed folders), the README is human-facing; the agent-facing reference lives in `scope.md` (for scope folders) or `agent.md` (for typed folders). README and the structured file cross-reference each other.

## Snapshot semantics

This convention atom is the canonical version. When applied to a folder, the relevant text is referenced (not copied as-is, since READMEs are folder-specific content). The convention itself does not get copied into each README; the *behaviour* is followed.

(Compare with `agent.md` in ontology-typed folders, where the template *is* copied as the snapshot. READMEs are different because their content is folder-specific.)
