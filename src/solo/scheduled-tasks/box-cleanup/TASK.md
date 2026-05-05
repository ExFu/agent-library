---
name: box-cleanup-task
description: Scheduled task that runs the cleanup script for the Box knowledge base. Collects _DELETED_ files into _trash/ (preserving hierarchy) and permanently deletes anything in _trash/ older than 60 days. Runs daily via Claude Desktop Cowork.
---

# Box Cleanup Scheduled Task

## What this task does

Runs a Python script daily that performs two-phase cleanup:

1. **Collect:** Finds files prefixed with `_DELETED_` anywhere in the knowledge base and moves them into `_trash/`, preserving directory hierarchy and restoring original filenames. This catches deletions made via the Box MCP connector.

2. **Purge:** Permanently deletes anything in `_trash/` older than 60 days. Files younger than 60 days are left alone — they're recoverable.

Box Drive syncs all changes back to Box automatically.

## One-time setup

### Install the script

The cleanup script is included with the ExFu plugin. During the install, the install skill copies it into your knowledge base at:

```
[BOX_KNOWLEDGE_BASE_PATH]/_meta/cleanup.py
```

If you need to restore it manually, the script is also available in the plugin at:
`${CLAUDE_PLUGIN_ROOT}/solo/scheduled-tasks/box-cleanup/cleanup.py`

### Create the scheduled task

1. Open **Claude Desktop**
2. Go to the **Cowork** tab
3. Click **Scheduled** in the left sidebar
4. Click **+ New task** in the upper right
5. Paste the task prompt below (with the path replaced)
6. Set the schedule to **Daily**
7. Click **Save**

The task runs every day while Claude Desktop is open and Box Drive is mounted. If the computer is asleep or the app is closed when it's due, it runs automatically next time the app opens.

## Task prompt

Replace `[BOX_KNOWLEDGE_BASE_PATH]` with the actual local path, then paste:

---

Run the Box knowledge base cleanup script:

```
python3 [BOX_KNOWLEDGE_BASE_PATH]/_meta/cleanup.py [BOX_KNOWLEDGE_BASE_PATH]
```

Report the output. If the script is missing or fails to run, report the error — do not attempt to recreate or fix the script.

---

## Testing

After setup, do a dry run to verify the script works:

```
python3 [BOX_KNOWLEDGE_BASE_PATH]/_meta/cleanup.py [BOX_KNOWLEDGE_BASE_PATH] --dry-run
```

This shows what the script would do without making any changes.

## Notes

- The script requires Python 3.8+ (standard on macOS, may need installing on Windows)
- Box Drive must be mounted and synced for deletions to propagate to Box
- Each run is saved as a Cowork session in the Scheduled sidebar — review past runs there
- The task needs filesystem access to the Box folder granted in Cowork
- The 60-day retention period is configurable via the `--retention-days` flag if the user wants to change it
- If the script encounters an error on a specific file, it skips it and logs the error — the file will be retried on the next run
