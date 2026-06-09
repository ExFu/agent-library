# Nightly index librarian

The canonical ExFu-shipped librarian. Runs nightly, walks the entire substrate, and regenerates the global index.

## What it does

Scans every scope in the substrate and produces a JSON map at `exfu/derived/index.json` containing:

- The scope tree (names, paths, parent relationships, nesting)
- Folder-type status per scope (data-bearing, pointer-only, or empty)
- ExFu version pins per scope
- Summary of which exfu versions are in use and which is latest

## What it touches

- Reads: every scope.md and agent.md in the substrate (read-only)
- Writes: `exfu/derived/index.json` (overwrites on each run)

## When it runs

Nightly, via the substrate-index scheduled task.

## What it produces

A single JSON file that gives any agent a whole-substrate picture in one read. Also feeds the HTML substrate visualisation (when built).

## Why it matters

Without the index, an agent entering the substrate has to walk the entire directory tree to understand what exists. With it, one file read gives the complete map -- every scope, where it sits, what it contains, which conventions it follows.
