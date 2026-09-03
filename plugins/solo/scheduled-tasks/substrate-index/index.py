#!/usr/bin/env python3
"""
Substrate Index

Walks the substrate directory tree, discovers scopes via scope.md files,
and produces a global JSON index at exfu/derived/index.json.

The index gives any agent a whole-substrate picture in one read: every scope,
its tree position, which folder-types are populated, version pins, and any
declared lifecycle assertion (status: stale) from scope.md.

Since 0.11.0 each scope entry also carries:

- "docket": present when the scope has a docket/ folder. Per-file status for
  the three entry files (data | pointer | empty), the pointer text declared
  for each in agent.md's "Local deviations:" (`todo: tracked in ClickUp, not
  stored locally`), the count of armed triggers, and the channel names.
- "deprecated": the deprecated folder-types (todo/, reminders/, inbox/) this
  scope still holds with content, so the dashboard, the boot skill and the
  docket migration can find candidates without walking the tree.

Usage:
    python3 index.py /path/to/substrate-root
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Standard folder-types in the catalogue. The three deprecated names stay so
# scopes that still hold them keep indexing.
FOLDER_TYPES = [
    "ontology", "context", "skills", "librarians", "scheduled",
    "docket", "todo", "reminders", "inbox", "databases", "visualisations",
]

# Folder-types superseded by docket/ (ontology.md#deprecated). Still indexed,
# never scaffolded.
DEPRECATED_FOLDER_TYPES = ["todo", "reminders", "inbox"]

# The docket's entry files, by the name used before the colon in a pointer
# line and as the stem of the JSONL file.
DOCKET_ENTRY_FILES = ["todo", "reminders", "agent-backlog"]

# A per-file pointer line in docket/agent.md's "Local deviations:", e.g.
# "- todo: tracked in ClickUp, not stored locally". The file name before the
# colon is explicit; the text after it has to say the data is elsewhere.
DOCKET_POINTER_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(todo|reminders|agent-backlog)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)
DOCKET_POINTER_WORDS = ("tracked in", "not stored locally", "managed in", "lives in")

# Directories to skip when walking
SKIP_NAMES = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__",
    ".DS_Store", ".idea", ".vscode", ".claude", ".omc",
}

# Phrases that indicate a pointer (external system) in agent.md. Only the
# deprecated folder-types are judged this way; docket/ uses the explicit
# per-file line form above.
POINTER_PHRASES = [
    "tasks are tracked in",
    "lives in",
    "managed by",
    "use the",
    "connector",
    "not stored locally",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate substrate index")
    parser.add_argument("root", help="Path to the substrate root folder")
    return parser.parse_args()


def parse_yaml_frontmatter(text):
    """
    Extract YAML frontmatter from a markdown file.
    Returns a dict of key-value pairs (simple single-line values only).
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}

    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^(\w[\w-]*):\s*(.+)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def read_scope_md(scope_dir):
    """
    Read and parse scope.md in the given directory.
    Returns parsed fields dict, or None if scope.md doesn't exist.
    """
    scope_file = scope_dir / "scope.md"
    if not scope_file.exists():
        return None
    try:
        text = scope_file.read_text(encoding="utf-8", errors="replace")
        return parse_yaml_frontmatter(text)
    except OSError:
        return None


def scope_status(fields):
    """
    Read the lifecycle assertion from parsed scope.md fields.
    "stale" is the only recognised assertion; anything else (including
    absence) means the scope is active and yields None.
    """
    value = (fields or {}).get("status", "").strip().lower()
    return "stale" if value == "stale" else None


def detect_folder_type_status(folder_dir):
    """
    Determine the status of a folder-type directory.
    Returns "data", "pointer", or "empty".
    """
    if not folder_dir.exists() or not folder_dir.is_dir():
        return "empty"

    # Check what files exist
    try:
        files = list(folder_dir.iterdir())
    except PermissionError:
        return "empty"

    file_names = {f.name for f in files if f.is_file()}
    boilerplate = {"agent.md", "readme.md"}
    has_content = bool(file_names - boilerplate)

    # Check for pointer pattern in agent.md
    agent_md = folder_dir / "agent.md"
    if agent_md.exists():
        try:
            agent_text = agent_md.read_text(encoding="utf-8", errors="replace").lower()
            for phrase in POINTER_PHRASES:
                if phrase in agent_text:
                    return "pointer"
        except OSError:
            pass

    # Has files beyond boilerplate, or subdirectories with content
    if has_content:
        return "data"

    # Check subdirectories for content
    subdirs = [f for f in files if f.is_dir() and f.name not in SKIP_NAMES]
    for subdir in subdirs:
        try:
            if any(subdir.iterdir()):
                return "data"
        except PermissionError:
            pass

    return "empty"


def read_jsonl_rows(path):
    """
    Rows of a JSONL file as dicts. Blank and unparseable lines are skipped
    (a half-written line under sync must not sink the whole index), and so
    are tombstoned rows (deleted: true).
    """
    rows = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and not row.get("deleted"):
            rows.append(row)
    return rows


def parse_docket_pointers(agent_text):
    """
    Per-file pointer declarations from docket/agent.md: {"todo": "tracked in
    ClickUp, not stored locally", ...}. Only lines in the explicit
    "<file>: <text>" form count, and a file is a pointer only when one of its
    lines says the data is elsewhere, so a stray "todo:" heading never reads
    as a pointer. Several lines for one file (the pointer, then how to reach
    the tool) join with "; " so the URL travels with the declaration.
    """
    lines_by_file = {}
    for line in agent_text.split("\n"):
        m = DOCKET_POINTER_RE.match(line)
        if m:
            lines_by_file.setdefault(m.group(1).lower(), []).append(m.group(2).strip())
    pointers = {}
    for name, lines in lines_by_file.items():
        if any(w in text.lower() for text in lines for w in DOCKET_POINTER_WORDS):
            pointers[name] = "; ".join(lines)
    return pointers


def scan_docket(folder_dir):
    """
    Status of a docket/ folder, judged per file.

    A file is "data" when it exists and holds at least one row with status
    "open" (tombstones excluded): a file holding only done or archived rows
    is on nobody's plate, so it reads "empty" until compaction removes it.
    A file is "pointer" when agent.md declares a pointer line for it and
    nothing local carries open rows. Otherwise "empty".

    Returns (folder_status, docket_obj). The folder is "data" if any file is,
    else "pointer" if any file is, else "empty".
    """
    agent_text = ""
    agent_md = folder_dir / "agent.md"
    if agent_md.exists():
        try:
            agent_text = agent_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            agent_text = ""
    pointers = parse_docket_pointers(agent_text)

    files = {}
    for name in DOCKET_ENTRY_FILES:
        path = folder_dir / f"{name}.jsonl"
        has_open = False
        if path.is_file():
            has_open = any(
                str(r.get("status", "open")).lower() == "open"
                for r in read_jsonl_rows(path)
            )
        if has_open:
            files[name] = "data"
        elif name in pointers:
            files[name] = "pointer"
        else:
            files[name] = "empty"

    triggers_path = folder_dir / "triggers.jsonl"
    armed = 0
    if triggers_path.is_file():
        armed = sum(
            1 for r in read_jsonl_rows(triggers_path)
            if str(r.get("status", "armed")).lower() == "armed"
        )

    channels_path = folder_dir / "channels.jsonl"
    channels = []
    if channels_path.is_file():
        for r in read_jsonl_rows(channels_path):
            name = r.get("name")
            if name and name not in channels:
                channels.append(name)

    statuses = set(files.values())
    if "data" in statuses:
        folder_status = "data"
    elif "pointer" in statuses:
        folder_status = "pointer"
    else:
        folder_status = "empty"

    docket = {
        "files": files,
        "pointers": pointers,
        "triggers": armed,
        "channels": channels,
    }
    return folder_status, docket


def scan_folder_types(scope_dir):
    """
    Scan a scope directory for folder-types and their status.
    Returns (folder_types, docket): a dict of folder-type name to status for
    every type present on disk, and the docket object (or None when the
    scope has no docket/ folder).
    """
    result = {}
    docket = None
    for ft in FOLDER_TYPES:
        ft_dir = scope_dir / ft
        if not ft_dir.exists():
            continue
        if ft == "docket":
            status, docket = scan_docket(ft_dir)
        else:
            status = detect_folder_type_status(ft_dir)
        result[ft] = status
    return result, docket


def deprecated_present(folder_types):
    """Deprecated folder-types this scope still holds with content."""
    return [
        ft for ft in DEPRECATED_FOLDER_TYPES
        if folder_types.get(ft) in ("data", "pointer")
    ]


def scan_scopes_dir(scopes_dir, parent_name):
    """
    Recursively scan a scopes/ directory for child scopes.
    Returns a list of scope entry dicts.

    Handles grouping folders (directories without scope.md) by
    recursing into them looking for actual scopes.
    """
    if not scopes_dir.exists() or not scopes_dir.is_dir():
        return []

    children = []
    try:
        entries = sorted(scopes_dir.iterdir())
    except PermissionError:
        return []

    for entry in entries:
        if not entry.is_dir() or entry.name in SKIP_NAMES or entry.name.startswith("."):
            continue

        fields = read_scope_md(entry)
        if fields is not None:
            # This is a scope
            scope_entry = build_scope_entry(entry, fields, parent_name)
            children.append(scope_entry)
        else:
            # Grouping folder -- recurse looking for scopes inside
            deeper = scan_scopes_dir(entry, parent_name)
            children.extend(deeper)

    return children


def build_scope_entry(scope_dir, fields, default_parent):
    """
    Build a scope entry dict from a scope directory and its parsed fields.
    """
    name = fields.get("name", scope_dir.name)
    parent = fields.get("parent", default_parent)
    exfu_version = fields.get("exfu")
    all_types, docket = scan_folder_types(scope_dir)

    # Only include folder-types that aren't all empty
    folder_types = {k: v for k, v in all_types.items() if v != "empty"} or all_types

    entry = {
        "name": name,
        "path": None,  # set by caller with relative path
        "type": "scope",
        "parent": parent if parent != "none" else None,
        "exfu_version": exfu_version,
        "folder_types": folder_types,
        "deprecated": deprecated_present(all_types),
    }
    if docket is not None:
        entry["docket"] = docket

    status = scope_status(fields)
    if status:
        entry["status"] = status

    # Recurse into scopes/ for children
    child_scopes = scan_scopes_dir(scope_dir / "scopes", name)
    if child_scopes:
        entry["children"] = child_scopes

    return entry


def discover_versions(exfu_dir):
    """
    Discover exfu version directories and which is latest.
    Returns a dict of version info.
    """
    versions = {}
    if not exfu_dir.exists():
        return versions

    # Find version directories: timestamp-named (YYYYMMDD-HHMM) or legacy v-prefixed
    for entry in sorted(exfu_dir.iterdir()):
        if entry.is_dir() and re.match(r"v\d|\d{8}-\d{4}$", entry.name):
            versions[entry.name] = {"is_latest": False, "scopes_using": []}

    # Determine latest
    latest = None
    latest_link = exfu_dir / "latest"
    latest_txt = exfu_dir / "latest.txt"

    if latest_link.is_symlink():
        target = latest_link.resolve().name
        latest = target
    elif latest_txt.exists():
        try:
            latest = latest_txt.read_text(encoding="utf-8").strip()
        except OSError:
            pass

    if latest and latest in versions:
        versions[latest]["is_latest"] = True
    elif versions:
        # Default to newest: timestamp identifiers outrank legacy v-prefixed ones;
        # within an era, lexicographic order is newest-last
        highest = max(versions, key=lambda n: (not n.startswith("v"), n))
        versions[highest]["is_latest"] = True

    return versions


def count_scopes(scopes):
    """
    Count scopes recursively, including nested children.
    """
    total = 0
    for scope in scopes:
        total += 1
        total += count_scopes(scope.get("children", []))
    return total


def build_index(root):
    """
    Build the complete index for a substrate root.
    Returns the index dict.
    """
    root = Path(root).resolve()
    exfu_dir = root / "exfu"

    # Discover versions
    versions = discover_versions(exfu_dir)

    scopes = []

    # 1. Scan user/ scope
    user_dir = root / "user"
    user_fields = read_scope_md(user_dir)
    if user_fields is not None:
        folder_types, docket = scan_folder_types(user_dir)
        user_entry = {
            "name": user_fields.get("name", "user"),
            "path": "user/",
            "type": "user",
            "parent": None,
            "exfu_version": user_fields.get("exfu"),
            "folder_types": folder_types,
            "deprecated": deprecated_present(folder_types),
        }
        if docket is not None:
            user_entry["docket"] = docket
        user_status = scope_status(user_fields)
        if user_status:
            user_entry["status"] = user_status
        scopes.append(user_entry)

    # 2. Scan scopes/ directory
    scopes_dir = root / "scopes"
    if scopes_dir.exists():
        try:
            for entry in sorted(scopes_dir.iterdir()):
                if not entry.is_dir() or entry.name in SKIP_NAMES or entry.name.startswith("."):
                    continue

                fields = read_scope_md(entry)
                if fields is not None:
                    scope_entry = build_scope_entry(entry, fields, "root")
                    scope_entry["path"] = f"scopes/{entry.name}/"
                    # Set paths on children recursively
                    _set_child_paths(scope_entry, f"scopes/{entry.name}/")
                    scopes.append(scope_entry)
                else:
                    # Grouping folder
                    deeper = scan_scopes_dir(entry, "root")
                    for s in deeper:
                        s["path"] = f"scopes/{entry.name}/{s.get('name', '').lower().replace(' ', '-')}/"
                    scopes.extend(deeper)
        except PermissionError:
            pass

    # Populate version usage
    _collect_version_usage(scopes, versions)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    index = {
        "generated": now,
        "substrate_root": str(root),
        "exfu_versions": versions,
        "scopes": scopes,
    }

    return index


def _set_child_paths(scope_entry, parent_path):
    """Recursively set path on child scopes."""
    if "children" not in scope_entry:
        return
    for child in scope_entry["children"]:
        child_slug = child.get("name", "").lower().replace(" ", "-")
        child["path"] = f"{parent_path}scopes/{child_slug}/"
        _set_child_paths(child, child["path"])


def _collect_version_usage(scopes, versions):
    """Walk scope tree and populate version usage lists."""
    for scope in scopes:
        ver = scope.get("exfu_version")
        if ver and ver in versions:
            versions[ver]["scopes_using"].append(scope["name"])
        if "children" in scope:
            _collect_version_usage(scope["children"], versions)


def main():
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    start = time.monotonic()

    index = build_index(root)

    # Ensure exfu/derived/ exists
    derived_dir = root / "exfu" / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)

    output_path = derived_dir / "index.json"
    output_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    elapsed = time.monotonic() - start
    scope_count = count_scopes(index["scopes"])
    version_count = len(index["exfu_versions"])
    print(
        f"Indexed {scope_count} scopes across {version_count} version(s), "
        f"wrote exfu/derived/index.json, took {elapsed:.2f}s."
    )


if __name__ == "__main__":
    main()
