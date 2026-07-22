---
name: exfu-dropbox-storage
description: Governs how Claude manages files in a Dropbox-backed Agent Library -- the cloud folder that serves as persistent substrate storage. Applies to personal libraries (solo users) and to team-shared libraries where the champion has chosen Dropbox as the shared storage backend. Dropbox's MCP connector supports create, read, move, copy, and delete natively by path, so no workaround machinery is needed; this skill covers access modes, conflict handling, hydration quirks, and hygiene rules. Use whenever Claude needs to read, write, organise, or clean up files in a Dropbox-backed knowledge base. Triggers on "save this", "organise my files", "move this to the Acme folder", "where did that file go?", "get rid of that note", "share this with the team's folder", or any instruction involving reading, writing, moving, or deleting content in a Dropbox-backed library.
---

# ExFu Dropbox Storage

Dropbox is the storage layer for this substrate. Claude manages the library files on the user's behalf -- the user rarely needs to touch Dropbox directly. This skill applies whether the library is personal (solo user) or team-shared (the champion chose Dropbox as the shared backend). The same conventions and hygiene rules apply in both cases.

Unlike the Box backend this replaced, Dropbox needs no workaround machinery: the connector supports delete, move, and copy natively, addresses files by path (not numeric IDs), and keeps per-file revision history. There is no `_trash/` folder, no `_DELETED_` prefix convention, and no cleanup task. If you encounter those artefacts, they are leftovers from a pre-0.4 Box-backed install -- suggest the `exfu-migrate-to-dropbox` skill.

## How Claude manages this library

Claude is the primary manager of this knowledge base. All organisation, filing, moving, and deletion is handled by Claude on the user's behalf.

The user may browse their Dropbox folder on their own machine -- that's fine. They should avoid manually renaming or moving library structure (scope folders, agent.md files); if Claude detects manual changes, reconcile the state at the start of the next session.

**Team-shared libraries:** multiple team members read and write the same shared folder. Dropbox has no file-level locking; when two people edit the same file in close succession, Dropbox keeps both by writing a *conflicted copy* (see below) rather than merging or overwriting. Keep shared files focused and single-author where possible, and write promptly after making changes.

## Access modes

**Local filesystem (preferred).** When the user's Dropbox folder is mounted in a Claude Desktop Cowork session, use filesystem tools directly: read, write, move, delete as normal filesystem operations. The Dropbox client syncs changes automatically. This is faster than the connector.

**Dropbox MCP connector (universal fallback).** Mobile sessions and sessions without the folder mounted use the Dropbox connector. It supports the full set natively:

- Create / overwrite: `create_file` (and folder creation)
- Read: `get_file_content`, `list_folder`, `search`
- Move and rename: `move` (a rename is a move within the same folder)
- Copy: `copy`
- Delete: `delete`
- Recovery: `list_file_revisions` / `restore_file_revision` for per-file history; deleted files remain recoverable in Dropbox's own trash for a period set by the user's plan (30 days on basic plans, longer on some paid plans)

Always check whether filesystem access is available before defaulting to the connector. If in doubt, ask: "Do you have your Dropbox folder open in this session?"

## Conflicted copies

When two edits collide, Dropbox writes a sibling file named like `notes (Alastair's conflicted copy 2026-07-20).md` instead of merging. Rules:

- Treat any file with "conflicted copy" in its name as a flag, not noise. Surface it to the user when encountered.
- Compare the conflicted copy against the main file, reconcile the content (with the user if the difference is substantive), then delete the conflicted copy.
- Never silently pick one version.

## Hydration (online-only files)

Dropbox can keep files "online-only" to save disk space. Reading such a file through the filesystem normally triggers a download, but a slow or offline link can make reads fail or come back empty. Recommended fix: right-click the library folder and choose **Make Available Offline** so the whole library stays hydrated. If you encounter empty files or read errors, the most likely cause is hydration, not a missing file.

## Symlinks

Sync layers handle symlinks unreliably; do not create them inside the library. The convention base's `exfu/latest.txt` pointer file exists for exactly this reason.

## Naming conventions

- Lowercase, hyphen-separated slugs: `meeting-notes-2026-07-20.md`
- Date-prefix time-sensitive files: `YYYY-MM-DD-filename`
- No spaces in filenames

## Behaviour rules

- **Confirm before destructive operations.** Deletes are real deletes now. Before deleting or overwriting content, confirm with the user unless the instruction was unambiguous. Mention that Dropbox's trash and revision history exist if the user hesitates.
- **No secrets.** Never write API keys, passwords, tokens, or credential files into the library. In a shared context, a credential written to Dropbox is visible to every member with folder access.
- **Large binaries.** For files over ~10 MB via the connector, flag before moving or copying rather than failing silently.
- **Sharing changes are the user's call.** Creating shared links or changing folder membership affects who can see the library -- do it only on explicit instruction.
