#!/usr/bin/env python3
"""
Librarian helper (v0.3.0)

Librarians are agent instructions: markdown definitions that Claude reads
and carries out inside a scheduled session. This helper does NOT run
librarians. It handles the two deterministic chores around the agentic
work, as plain tool calls:

    due     -- report which librarians are due for a cadence, in
               dependency order, with definition paths and health notes
    record  -- record one librarian's outcome: update registry health
               and append to the run log

Usage:
    python3 librarians.py due /path/to/substrate-root nightly
    python3 librarians.py record /path/to/substrate-root nightly-index \\
        --status success --detail "Indexed 4 scopes; no anomalies"

Exit codes:
    0 -- ok (including "nothing due")
    1 -- helper failed (bad arguments, unreadable registry, unknown name,
         circular dependencies)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_RETENTION_DAYS = 90
VALID_STATUSES = ("success", "failure", "skipped")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registry_path(root):
    return root / "exfu" / "derived" / "librarian-registry.json"


def log_path(root):
    return root / "exfu" / "derived" / "librarian-log.json"


def load_json(path):
    """Load JSON from path. Returns (data, error_string)."""
    if not path.exists():
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (json.JSONDecodeError, OSError) as e:
        return None, str(e)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def topological_sort(librarians):
    """
    Sort librarians by depends_on. Returns ordered list.
    Raises ValueError on circular dependencies.
    """
    by_name = {lib["name"]: lib for lib in librarians}
    visited = set()
    visiting = set()
    order = []

    def visit(name):
        if name in visited:
            return
        if name in visiting:
            raise ValueError(f"Circular dependency detected involving '{name}'")
        visiting.add(name)
        lib = by_name.get(name)
        if lib:
            for dep in lib.get("depends_on", []):
                if dep in by_name:
                    visit(dep)
        visiting.discard(name)
        visited.add(name)
        if name in by_name:
            order.append(by_name[name])

    for lib in librarians:
        visit(lib["name"])

    return order


def cmd_due(root, cadence):
    """Print the due librarians for a cadence, dependency-ordered."""
    reg_file = registry_path(root)
    registry, err = load_json(reg_file)
    if err:
        print(f"Error reading registry: {err}", file=sys.stderr)
        return 1
    if registry is None:
        print(f"No librarian registry at {reg_file}. Nothing to run.")
        return 0

    all_libs = registry.get("librarians", [])
    by_name = {lib["name"]: lib for lib in all_libs}
    due = [
        lib for lib in all_libs
        if lib.get("cadence") == cadence and lib.get("enabled", True)
    ]

    if not due:
        print(f"No enabled librarians for cadence '{cadence}'. Nothing to run.")
        return 0

    try:
        ordered = topological_sort(due)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    warnings = []
    print(f"{len(ordered)} {cadence} librarian(s) due, in dependency order:")
    print()

    for i, lib in enumerate(ordered, 1):
        name = lib["name"]
        source = lib.get("source", "")
        def_path = (root / source) if source else None

        print(f"{i}. {name}")
        if def_path and def_path.exists():
            print(f"   definition: {def_path}")
        elif source:
            print(f"   definition: {def_path}  [MISSING]")
            warnings.append(
                f"{name}: definition file not found at {source} -- "
                "record it as failure unless you can locate it"
            )
        else:
            print("   definition: (none recorded)")
            warnings.append(f"{name}: registry entry has no source path")

        deps = lib.get("depends_on", [])
        print(f"   depends_on: {', '.join(deps) if deps else '(none)'}")

        last_status = lib.get("last_status")
        last_run = lib.get("last_run")
        failures = lib.get("consecutive_failures", 0)
        if last_run:
            print(f"   last: {last_status} at {last_run}; consecutive failures: {failures}")
        else:
            print("   last: never run")

        for dep in deps:
            dep_lib = by_name.get(dep)
            if dep_lib is None:
                warnings.append(f"{name}: depends on '{dep}' which is not registered")
            elif not dep_lib.get("enabled", True):
                warnings.append(f"{name}: depends on '{dep}' which is disabled")
            elif dep_lib.get("cadence") != cadence:
                warnings.append(
                    f"{name}: depends on '{dep}' ({dep_lib.get('cadence')} cadence) -- "
                    "make sure that cadence has run recently"
                )

        if failures >= 3:
            warnings.append(
                f"{name}: {failures} consecutive failures -- flag this for the user"
            )
        print()

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    print("Read each definition and follow its instructions, then record each outcome:")
    print(f"  python3 {Path(__file__).name} record <root> <name> "
          "--status success|failure|skipped [--detail \"one line\"]")
    return 0


def cmd_record(root, name, status, detail):
    """Record one librarian's outcome in the registry and log."""
    reg_file = registry_path(root)
    registry, err = load_json(reg_file)
    if err:
        print(f"Error reading registry: {err}", file=sys.stderr)
        return 1
    if registry is None:
        print(f"No librarian registry at {reg_file}.", file=sys.stderr)
        return 1

    entry = None
    for lib in registry.get("librarians", []):
        if lib.get("name") == name:
            entry = lib
            break
    if entry is None:
        print(f"No librarian named '{name}' in the registry.", file=sys.stderr)
        return 1

    now = utc_now()

    # Update registry health
    entry["last_run"] = now
    entry["last_status"] = status
    if status == "success":
        entry["consecutive_failures"] = 0
    elif status == "failure":
        entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
    # "skipped" leaves the failure counter untouched

    # Stamp the cadence
    cadence = entry.get("cadence")
    if cadence:
        cadences = registry.setdefault("cadences", {})
        info = cadences.setdefault(
            cadence, {"scheduled_task": f"{cadence}-librarians"}
        )
        info["last_run"] = now

    write_json(reg_file, registry)

    # Append to log
    log_file = log_path(root)
    log_data, log_err = load_json(log_file)
    if log_data is None or log_err or "entries" not in log_data:
        log_data = {"entries": []}

    log_entry = {
        "at": now,
        "cadence": cadence,
        "name": name,
        "status": status,
    }
    if detail:
        log_entry["detail"] = detail
    log_data["entries"].append(log_entry)

    # Trim old entries
    cutoff = datetime.now(timezone.utc).timestamp() - (LOG_RETENTION_DAYS * 86400)
    trimmed = []
    for e in log_data["entries"]:
        try:
            at = datetime.fromisoformat(e["at"].replace("Z", "+00:00"))
            if at.timestamp() >= cutoff:
                trimmed.append(e)
        except (KeyError, ValueError):
            trimmed.append(e)  # keep entries we can't parse
    log_data["entries"] = trimmed

    write_json(log_file, log_data)

    failures = entry.get("consecutive_failures", 0)
    suffix = f" (consecutive failures: {failures})" if failures else ""
    print(f"Recorded {name}: {status}{suffix}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic chores around agentic librarian runs"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_due = sub.add_parser("due", help="List due librarians for a cadence")
    p_due.add_argument("root", help="Path to the substrate root folder")
    p_due.add_argument("cadence", help="Cadence group (e.g. nightly, weekly)")

    p_rec = sub.add_parser("record", help="Record one librarian's outcome")
    p_rec.add_argument("root", help="Path to the substrate root folder")
    p_rec.add_argument("name", help="Librarian name as registered")
    p_rec.add_argument(
        "--status", required=True, choices=VALID_STATUSES,
        help="Outcome of the run",
    )
    p_rec.add_argument(
        "--detail", default="",
        help="One line of what happened (becomes the log detail)",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    if args.command == "due":
        sys.exit(cmd_due(root, args.cadence))
    elif args.command == "record":
        sys.exit(cmd_record(root, args.name, args.status, args.detail))


if __name__ == "__main__":
    main()
