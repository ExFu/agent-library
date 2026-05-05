#!/usr/bin/env python3
"""
Box Knowledge Base Cleanup

Two-phase cleanup for the Box-based substrate:
1. Collect: Move _DELETED_-prefixed files into _trash/, preserving directory hierarchy
2. Purge: Permanently delete anything in _trash/ older than the retention period

Usage:
    python3 cleanup.py /path/to/knowledge-base [--retention-days 60] [--dry-run]
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Box knowledge base cleanup")
    parser.add_argument("root", help="Path to the knowledge base root folder")
    parser.add_argument(
        "--retention-days",
        type=int,
        default=60,
        help="Days to keep files in _trash/ before permanent deletion (default: 60)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    return parser.parse_args()


def collect_deleted_files(root: Path, trash_dir: Path, dry_run: bool) -> list[dict]:
    """Find _DELETED_-prefixed files and move them to _trash/."""
    collected = []
    deleted_pattern = re.compile(r"^_DELETED_\d{4}-\d{2}-\d{2}_(.+)$")

    for dirpath, dirnames, filenames in os.walk(root):
        dirpath = Path(dirpath)

        # Skip _trash/ and _meta/
        dirnames[:] = [
            d for d in dirnames if d not in ("_trash", "_meta", ".DS_Store")
        ]

        for filename in filenames:
            match = deleted_pattern.match(filename)
            if not match:
                continue

            source = dirpath / filename
            original_name = match.group(1)
            rel_dir = dirpath.relative_to(root)
            dest_dir = trash_dir / rel_dir
            dest = dest_dir / original_name

            record = {
                "source": str(source),
                "dest": str(dest),
                "original_name": original_name,
                "rel_path": str(rel_dir / original_name),
            }

            if dry_run:
                record["action"] = "would move"
            else:
                try:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(dest))
                    record["action"] = "moved"
                except OSError as e:
                    record["action"] = f"error: {e}"

            collected.append(record)

    return collected


def purge_old_trash(trash_dir: Path, retention_days: int, dry_run: bool) -> list[dict]:
    """Permanently delete files in _trash/ older than retention period."""
    purged = []
    cutoff = datetime.now() - timedelta(days=retention_days)

    if not trash_dir.exists():
        return purged

    for dirpath, dirnames, filenames in os.walk(trash_dir, topdown=False):
        dirpath = Path(dirpath)

        for filename in filenames:
            if filename == ".DS_Store":
                continue

            filepath = dirpath / filename
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

            if mtime >= cutoff:
                continue

            rel_path = filepath.relative_to(trash_dir)
            record = {
                "path": str(rel_path),
                "trashed_on": mtime.strftime("%Y-%m-%d"),
                "age_days": (datetime.now() - mtime).days,
            }

            if dry_run:
                record["action"] = "would delete"
            else:
                try:
                    filepath.unlink()
                    record["action"] = "deleted"
                except OSError as e:
                    record["action"] = f"error: {e}"

            purged.append(record)

        # Clean up empty directories (skip trash root)
        if dirpath != trash_dir and not any(dirpath.iterdir()):
            if not dry_run:
                try:
                    dirpath.rmdir()
                except OSError:
                    pass

    return purged


def main():
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    trash_dir = root / "_trash"
    trash_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    prefix = "[DRY RUN] " if args.dry_run else ""

    print(f"{prefix}Box Cleanup — {today}")
    print(f"Root: {root}")
    print(f"Retention: {args.retention_days} days")
    print()

    # Phase 1: Collect
    collected = collect_deleted_files(root, trash_dir, args.dry_run)
    print(f"Collected: {len(collected)} files moved to _trash/")
    for item in collected:
        print(f"  {item['action']}: {item['original_name']} (from {item['rel_path']})")
    if not collected:
        print("  No pending deletions found.")
    print()

    # Phase 2: Purge
    purged = purge_old_trash(trash_dir, args.retention_days, args.dry_run)
    print(
        f"Purged: {len(purged)} files permanently deleted (older than {args.retention_days} days)"
    )
    for item in purged:
        print(
            f"  {item['action']}: {item['path']} (trashed {item['trashed_on']}, {item['age_days']} days ago)"
        )
    if not purged:
        print("  No files old enough to purge.")
    print()

    # Errors summary
    errors = [
        item
        for item in collected + purged
        if item.get("action", "").startswith("error")
    ]
    if errors:
        print(f"Errors: {len(errors)}")
        for item in errors:
            print(f"  {item.get('path', item.get('source'))}: {item['action']}")
    else:
        print("Errors: none")


if __name__ == "__main__":
    main()
