#!/usr/bin/env python3
"""
Substrate Index (v0.3.0)

Walks the substrate directory tree, discovers scopes via scope.md files,
and produces a global JSON index at exfu/derived/index.json.

The index gives any agent a whole-substrate picture in one read: every scope,
its tree position, which folder-types are populated, and version pins.

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

# Standard folder-types in the catalogue
FOLDER_TYPES = [
    "ontology", "context", "docs", "skills", "librarians",
    "todo", "reminders", "inbox", "databases", "visualisations",
]

# Directories to skip when walking
SKIP_NAMES = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__",
    ".DS_Store", ".idea", ".vscode", ".claude", ".omc",
}

# Phrases that indicate a pointer (external system) in agent.md
POINTER_PHRASES = [
    "tasks are tracked in",
    "lives in",
    "managed by",
    "use the",
    "connector",
    "not stored locally",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate substrate index (v0.3)")
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


def scan_folder_types(scope_dir):
    """
    Scan a scope directory for folder-types and their status.
    Returns dict of folder-type name to status, including only
    types that are present (data or pointer) or in the standard catalogue.
    """
    result = {}
    for ft in FOLDER_TYPES:
        ft_dir = scope_dir / ft
        if ft_dir.exists():
            status = detect_folder_type_status(ft_dir)
            result[ft] = status
    return result


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
    folder_types = scan_folder_types(scope_dir)

    # Only include folder-types that aren't all empty
    folder_types = {k: v for k, v in folder_types.items() if v != "empty"} or \
                   {k: v for k, v in scan_folder_types(scope_dir).items()}

    entry = {
        "name": name,
        "path": None,  # set by caller with relative path
        "type": "scope",
        "parent": parent if parent != "none" else None,
        "exfu_version": exfu_version,
        "folder_types": folder_types,
    }

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

    # Find version directories (match v followed by digits)
    for entry in sorted(exfu_dir.iterdir()):
        if entry.is_dir() and re.match(r"v\d", entry.name):
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
        # Default to highest version
        highest = sorted(versions.keys())[-1]
        versions[highest]["is_latest"] = True

    return versions


def set_relative_paths(scopes, root, base_path):
    """
    Recursively set relative paths on scope entries.
    """
    for scope in scopes:
        scope_name_lower = scope["name"].lower().replace(" ", "-")
        # Try to find the actual directory
        if "children" in scope:
            set_relative_paths(scope["children"], root, base_path)


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
        folder_types = scan_folder_types(user_dir)
        user_entry = {
            "name": user_fields.get("name", "user"),
            "path": "user/",
            "type": "user",
            "parent": None,
            "exfu_version": user_fields.get("exfu"),
            "folder_types": folder_types,
        }
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
    scope_count = len(index["scopes"])
    version_count = len(index["exfu_versions"])
    print(
        f"Indexed {scope_count} scopes across {version_count} version(s), "
        f"wrote exfu/derived/index.json, took {elapsed:.2f}s."
    )


if __name__ == "__main__":
    main()
