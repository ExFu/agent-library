# _trash/

## Purpose

Soft-delete area. When a file is "deleted" in the substrate, it is moved here rather than removed from disk. This gives the user a recovery window before the file is permanently gone.

## Contents

(Empty in this example.)

In a live substrate, files would mirror their original path under `_trash/`, prefixed with the deletion date for traceability. Example: a file originally at `user/scratch/draft.md` deleted on 2026-05-21 would land at `_trash/user/scratch/2026-05-21-draft.md`.

## Dependencies

- The cleanup librarian (`exfu/librarians/cleanup/`) permanently deletes files in `_trash/` older than 60 days. Not shipped in this example.
- The substrate skill enforces that user-facing "delete" maps to "move to `_trash/`", never to a raw filesystem delete.

## Why this folder exists

A substrate is a knowledge base the user is meant to trust. Trust requires that mistakes are recoverable. `_trash/` is the 60-day undo window.
