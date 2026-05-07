#!/usr/bin/env python3
"""
Substrate Folder Index

Walks the substrate folder tree and generates a folder-level map at
_meta/substrate-index.md. Each folder is annotated with its Purpose and a
brief note on what it holds, extracted from the folder's README.md.

Usage:
    python3 index.py /path/to/substrate-root
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Folders to skip entirely (never indexed, never recursed into).
# Only system/hidden folders and the two reserved substrate areas are excluded.
# Every other folder — including custom ones the user has created — is indexed.
SKIP_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".DS_Store",
    "_trash",   # soft-delete area; not indexed
    "_meta",    # system infrastructure; the index itself lives here
    ".idea",
    ".vscode",
    ".claude",
}

# Cap individual description fields at this many characters
MAX_FIELD_CHARS = 120

# Rough cap on total output size (bytes). Index is truncated with a note if exceeded.
MAX_OUTPUT_BYTES = 50 * 1024  # 50 KB


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a substrate folder index")
    parser.add_argument("root", help="Path to the substrate root folder")
    return parser.parse_args()


def _first_sentences(text: str, max_chars: int) -> str:
    """Return the first 1-2 sentences of text, capped at max_chars."""
    text = text.strip()
    if not text:
        return ""
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    sentence_end = re.compile(r"(?<=[.!?])\s+")
    parts = sentence_end.split(text, maxsplit=2)
    result = parts[0].rstrip()
    if len(parts) > 1 and len(result) + 1 + len(parts[1]) <= max_chars:
        result = result + " " + parts[1].rstrip()
    if len(result) > max_chars:
        result = result[:max_chars].rstrip() + "..."
    return result


def _cap(text: str) -> str:
    """Cap text at MAX_FIELD_CHARS."""
    if len(text) <= MAX_FIELD_CHARS:
        return text
    return text[:MAX_FIELD_CHARS].rstrip() + "..."


def extract_section(readme_text: str, heading: str) -> str:
    """
    Extract the body of a markdown section identified by a heading.

    Looks for `## <heading>` (case-insensitive) and returns the text up to
    the next same-or-higher-level heading, or end of file.
    """
    pattern = re.compile(
        r"^##\s+" + re.escape(heading) + r"\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(readme_text)
    if not match:
        return ""

    start = match.end()
    # Find the next ## or # heading after this one
    next_heading = re.search(r"^#{1,2}\s+", readme_text[start:], re.MULTILINE)
    if next_heading:
        body = readme_text[start : start + next_heading.start()]
    else:
        body = readme_text[start:]

    return body.strip()


def first_paragraph(text: str) -> str:
    """Return the first non-empty paragraph of text."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    for p in paragraphs:
        p = p.strip()
        # Skip headings and empty lines
        if p and not p.startswith("#"):
            # Collapse internal newlines (common in soft-wrapped markdown)
            return re.sub(r"\s*\n\s*", " ", p)
    return ""


def parse_readme(folder_path: Path):
    """
    Parse a README.md in the given folder.

    Returns (why, holds) as strings. Either may be empty.
    - why: first 1-2 sentences of the Purpose section (or first paragraph)
    - holds: first sentence of the Contents section (or "(not specified)")
    """
    readme = folder_path / "README.md"
    if not readme.exists():
        return None, None  # Signal: no README

    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, None

    # Try Purpose section first
    purpose_body = extract_section(text, "Purpose")
    if purpose_body:
        why = _first_sentences(first_paragraph(purpose_body) or purpose_body, MAX_FIELD_CHARS)
    else:
        # Fall back to first non-heading paragraph in the whole file
        why = _first_sentences(first_paragraph(text), MAX_FIELD_CHARS)

    why = _cap(why) if why else ""

    # Try Contents section
    contents_body = extract_section(text, "Contents")
    if contents_body:
        holds = _cap(_first_sentences(first_paragraph(contents_body) or contents_body, MAX_FIELD_CHARS))
    else:
        holds = ""

    return why, holds


def collect_folders(root: Path):
    """
    Walk the folder tree and return a list of (rel_path, depth) tuples,
    sorted in tree order (parents before children, alphabetically within
    each level).
    """
    folders = []

    def _walk(current: Path, depth: int):
        try:
            entries = sorted(current.iterdir())
        except PermissionError:
            return
        for entry in entries:
            if not entry.is_dir():
                continue
            if entry.name in SKIP_NAMES or entry.name.startswith("."):
                continue
            rel = entry.relative_to(root)
            folders.append((rel, depth))
            _walk(entry, depth + 1)

    _walk(root, 1)
    return folders


def heading_level(depth: int) -> str:
    """Map folder depth to a markdown heading level (max level 6)."""
    level = min(depth + 1, 6)  # depth 1 -> ##, depth 2 -> ###, etc.
    return "#" * level


def build_index(root: Path) -> tuple[str, int]:
    """
    Build the index markdown string.

    Returns (markdown_text, folder_count).
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folders = collect_folders(root)

    lines = [
        "# Substrate folder index",
        "",
        f"Auto-generated {now} (machine local time). Do not edit by hand.",
        "",
        "This is a folder-only map of the substrate. Files are not listed; for that, scan a folder directly. Each folder is annotated with its Purpose and a brief note on what it holds, drawn from the folder's own README.md.",
        "",
        "---",
        "",
    ]

    for rel_path, depth in folders:
        abs_path = root / rel_path
        why, holds = parse_readme(abs_path)

        hdr = heading_level(depth)
        # Show path with trailing slash for clarity
        lines.append(f"{hdr} {rel_path}/")

        if why is None:
            # No README at all
            lines.append("**Why:** (no README — purpose unknown)")
            lines.append("**Holds:** (no README — contents unknown)")
        else:
            why_str = why if why else "(not specified)"
            holds_str = holds if holds else "(not specified)"
            lines.append(f"**Why:** {why_str}")
            lines.append(f"**Holds:** {holds_str}")

        lines.append("")

    return "\n".join(lines), len(folders)


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

    # Build index
    index_text, folder_count = build_index(root)

    # Check size; append a note if over limit
    if len(index_text.encode("utf-8")) > MAX_OUTPUT_BYTES:
        index_text += (
            "\n---\n\n"
            "_Note: this substrate is large. The index above covers all folders found "
            "but the output approached the size limit. If some entries appear truncated, "
            "scan the folder directly._\n"
        )

    # Ensure _meta/ exists
    meta_dir = root / "_meta"
    meta_dir.mkdir(exist_ok=True)

    output_path = meta_dir / "substrate-index.md"
    output_path.write_text(index_text, encoding="utf-8")

    elapsed = time.monotonic() - start
    print(
        f"Indexed {folder_count} folders, wrote _meta/substrate-index.md, "
        f"took {elapsed:.2f}s."
    )


if __name__ == "__main__":
    main()
