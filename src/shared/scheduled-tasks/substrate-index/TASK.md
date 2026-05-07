---
name: substrate-index
description: Scheduled task that generates a folder-level index of the substrate nightly. Walks the folder tree, extracts Purpose and Contents from each folder's README.md, and writes a fresh map to _meta/substrate-index.md. Runs locally; no external dependencies.
---

# Substrate Index Scheduled Task

## What this task does

Runs a Python script nightly that walks your substrate folder tree and writes a fresh folder-level map to `_meta/substrate-index.md`. Each folder in the index is annotated with its Purpose (why it exists) and a brief note on what it holds, drawn from the folder's own README.md.

The map is folders only. Files are not listed. Hidden folders (`.git`, `node_modules`, `__pycache__`) and `_trash/` are excluded.

The script is idempotent: each run overwrites the previous index cleanly.

## Why it exists

The `wow` skill carries a hand-curated navigation map — an editorial layer that highlights what matters most. That map drifts as the substrate grows and reorganises. The substrate index is the complementary layer: comprehensive, machine-generated, always current because it's regenerated every night from the actual folder tree.

Agents reading `_meta/substrate-index.md` get a cheap orientation pass. When `wow`'s pointers aren't specific enough to answer "where might X live?", the index fills the gap without requiring a full directory scan.

## How to enable

1. Open **Claude Desktop**
2. Go to the **Cowork** tab
3. Click **Scheduled** in the left sidebar
4. Click **+ New task** in the upper right
5. Paste the task prompt below (with the path filled in)
6. Set the schedule to **Daily** at **03:00** (or any overnight time that suits you)
7. Click **Save**

The task runs while Claude Desktop is open. If the machine is asleep at the scheduled time, it runs automatically the next time the app opens.

## Task prompt

Replace `[SUBSTRATE_ROOT]` with the absolute path to your substrate root folder, then paste:

---

Run the substrate index script:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py [SUBSTRATE_ROOT]
```

Report the output. If the script is missing or fails, report the error — do not attempt to recreate or fix the script.

---

## Finding your substrate root

The substrate root is the folder you selected during your ExFu install — the one that contains `CLAUDE.md` and folders like `context/`, `scopes/`, `_meta/`. It's also recorded in `_meta/storage-backend.md` at that root.

If you set up multiple substrates (a personal layer and a team layer), run a separate task for each root path.

## After the task runs

Nothing to do. The script writes `_meta/substrate-index.md` and prints a brief summary to the Cowork session log. Agents read the index automatically when they need an orientation pass; you don't need to point them at it manually.

## Testing

After setup, run it manually once from the Scheduled tab to confirm it produces a sensible index. If you want to test from the command line first:

```
python3 [PATH_TO_PLUGIN]/scheduled-tasks/substrate-index/index.py [SUBSTRATE_ROOT]
```

The script prints how many folders it indexed and where the output was written.

## Privacy note

The index is generated locally and written to your substrate. It never leaves your machine. It contains folder names and the Purpose/Contents text from your READMEs — no file contents, no credentials, no personal data beyond what you've already written into your README files.
