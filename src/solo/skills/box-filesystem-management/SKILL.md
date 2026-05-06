---
name: box-filesystem-management
description: Governs how Claude manages files in the user's Box knowledge base — the cloud folder that serves as their persistent substrate storage. Because Box has limitations (no native move or delete in the MCP connector, offline-caching quirks), Claude needs specific workarounds to operate reliably on the user's behalf. Use whenever Claude needs to read, write, organise, or clean up files in this knowledge base. Triggers on "save this", "organise my files", "move this to the Acme folder", "where did that file go?", "get rid of that note", or any instruction involving reading, writing, moving, or deleting content in the knowledge base.
---

# Box Filesystem Management

Box is the storage layer for this user's substrate. Claude manages the knowledge base files on the user's behalf — the user rarely needs to touch Box directly. This skill exists because Box's MCP connector has real limitations (no native delete or move, offline-caching quirks) that require specific workarounds, and because naming and trash conventions need to be consistent across every session for the knowledge base to remain navigable.

## How Claude manages this knowledge base

Claude is the primary manager of this Box knowledge base. The user will typically not interact with Box files directly — all organisation, filing, moving, and deletion is handled by Claude on their behalf.

The user may occasionally browse Box Drive on their own machine — that's fine. They should not manually rename, move, or delete files. If Claude detects the user has made manual changes, reconcile the state at the start of the next session.

## Access mode: local filesystem vs Box connector

How Claude accesses the knowledge base depends on the context:

**Local filesystem access (preferred)**
When the user mounts their Box folder in a Claude Desktop Cowork session, Claude has direct filesystem access. Use the filesystem tools directly — read, write, move, and delete files as normal filesystem operations. Box Drive syncs changes to Box automatically. This is faster and more capable than the connector.

**Box MCP connector (universal fallback)**
Claude mobile and Claude Desktop sessions without a mounted Box folder must use the Box MCP connector. The connector has no native delete or move tools — use the workarounds below.

Always check whether filesystem access is available before defaulting to the connector. If in doubt, ask: "Do you have the Box folder open in this session?"

## CRUD via the Box connector (workarounds)

The following only applies when operating through the Box MCP connector, not when filesystem access is available.

### Delete (workaround)

The connector has no delete tool. To delete a file, move it to the trash folder:

1. Create the file at `_trash/[original-relative-path]/[filename]` using `upload_file`
2. Rename the original file with a `_DELETED_` prefix so the cleanup task knows to remove it from its original location

Example:
```
Original:  scopes/website/old-draft.md
Trash:     _trash/scopes/website/old-draft.md
Renamed:   scopes/website/_DELETED_2026-04-20_old-draft.md
```

The daily cleanup task handles both: it moves the renamed original into trash (if the connector couldn't fully remove it) and permanently deletes anything in `_trash/` older than 60 days.

### Move (workaround)

The connector has no move tool. Simulate a move as two steps:
1. Create a new copy at the destination using `upload_file`
2. Mark the original with `_DELETED_` prefix as above

For large binary files (over ~10 MB), this requires downloading and re-uploading the full content, which may be slow. Flag this to the user before attempting rather than failing silently.

### Copy

Upload the same content to the destination folder. No workaround needed — straightforward create operation.

### Folder IDs

The connector identifies folders by numeric ID, not path. Establish the correct folder ID before any operation. Store frequently used folder IDs in the knowledge base itself (e.g. in a `_meta/folder-ids.md` file) so they don't need to be re-discovered each session. If an operation fails with a not-found error, re-discover the ID before retrying — IDs can become stale if a folder was deleted and recreated.

## Trash folder

The `_trash/` folder lives at the root of the knowledge base. It mirrors the directory hierarchy of the main knowledge base so that recovery is straightforward — a file's path within `_trash/` tells you exactly where it came from.

Rules:
- Files in `_trash/` are recoverable for 60 days
- After 60 days, the cleanup task permanently deletes them
- To recover a file, move it back to its original location (the path within `_trash/` tells you where it belongs)
- The user can browse `_trash/` at any time to see what's pending deletion

## Offline caching note

Box Drive has a known issue: if Box Drive is set to space-saver mode, files Claude tries to read may come back empty because Box hasn't downloaded them locally yet. Recommended fix: set Box Drive to keep the knowledge base folder fully downloaded at all times. On macOS, right-click the knowledge base folder in Finder and select "Make Available Offline". This ensures Claude can always read the files without waiting for a download.

If you encounter empty files or read errors, the most likely cause is a caching issue, not a missing file.

## Naming conventions

Apply these consistently regardless of access mode:

- Lowercase, hyphen-separated slugs: `meeting-notes-2026-04-15.md`
- Date-prefix time-sensitive files: `YYYY-MM-DD-filename`
- Deleted files (pending cleanup): `_DELETED_YYYY-MM-DD_original-filename`
- No spaces in filenames
- Underscore-prefixed folders for system use: `_trash/`, `_meta/`

## Behaviour rules

- **Confirm before destructive operations.** Before trashing a file or overwriting content, confirm with the user unless the instruction was unambiguous.
- **External sharing constraint (connector only).** The Box connector restricts uploads to folders that are not externally shared. If an upload fails for this reason, report it clearly and suggest the user adjust the folder's sharing settings in Box Drive.
- **Large binaries.** Flag move/copy limitations for files over ~10 MB before attempting. Offer to create a fresh version at the destination instead of retrieving and re-uploading the original.
