#!/usr/bin/env python3
"""
Dashboard Generator (v0.3.1)

Reads the substrate index, the scheduled-agent registry, and the run log,
plus workspace content from individual scopes, and generates a
self-contained HTML dashboard at exfu/visualisations/dashboard/index.html
(the substrate's visualisations gallery). Falls back to the pre-rename
registry/log filenames so it works on substrates that predate the
scheduled-agent vocabulary.

Usage:
    python3 dashboard-generator.py /path/to/substrate-root
"""

import argparse
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate the ExFu substrate dashboard (v0.3)"
    )
    parser.add_argument("root", help="Path to the substrate root folder")
    return parser.parse_args()


def load_json(path):
    """Load a JSON file. Returns None if missing or unparseable."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except (json.JSONDecodeError, OSError):
        return None


def read_file_text(path, max_bytes=8192):
    """Read a text file up to max_bytes. Returns empty string on failure."""
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[:max_bytes]
    except OSError:
        return ""


def parse_yaml_frontmatter(text):
    """Extract simple YAML frontmatter key-value pairs from markdown."""
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


def strip_frontmatter(text):
    """Remove a leading YAML frontmatter block from markdown text."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).strip()
    return text


def deslug(filename):
    """Turn a filename into a human-readable title."""
    stem = filename.rsplit(".", 1)[0]
    undated = re.sub(r"^\d{4}-\d{2}-\d{2}[-_]?", "", stem)
    words = (undated or stem).replace("_", " ").replace("-", " ").strip()
    if not words:
        return filename
    return words[:1].upper() + words[1:]


def first_snippet(text, max_len=140):
    """First meaningful line of a markdown body, for item summaries."""
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<!--"):
            continue
        s = s.lstrip(">-* ").strip()
        if not s:
            continue
        if len(s) > max_len:
            return s[:max_len].rstrip() + "..."
        return s
    return ""


def file_age_label(mtime):
    """Quiet age label for an item file."""
    if not mtime:
        return ""
    days = int((time.time() - mtime) // 86400)
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    return f"{days} days ago"


# Known external tools for pointer chips
POINTER_TOOLS = [
    "ClickUp", "Linear", "Todoist", "Asana", "Notion", "Trello",
    "Jira", "Things", "Apple Reminders", "Monday", "Airtable", "HubSpot",
]


def pointer_tool_name(pointer_text):
    """Extract a known tool name from pointer text, if present."""
    low = (pointer_text or "").lower()
    for tool in POINTER_TOOLS:
        if tool.lower() in low:
            return tool
    return None


def inline_md(s):
    """Escape, then render the inline markdown we tolerate (bold, wikilinks)."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[\[(.+?)\]\]", r"\1", s)
    return s


CHECKBOX_RE = re.compile(r"^[-*] \[( |x|X)\]\s*(.*)$")


def render_markdown_mini(text, max_items=10):
    """
    Render a constrained markdown subset to dashboard HTML: headings become
    section labels, checkboxes become task rows, bullets become list rows,
    other lines render as plain text. Everything is escaped; long content
    truncates with an explicit count, never silently.
    """
    out = []
    shown = 0
    hidden = 0
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line.startswith("<!--") or line == "---":
            continue
        if line.startswith("#"):
            label = line.lstrip("#").strip()
            if label:
                out.append(f'<div class="ws-heading">{inline_md(label)}</div>')
            continue
        if shown >= max_items:
            hidden += 1
            continue
        m = CHECKBOX_RE.match(line)
        if m:
            done = m.group(1).lower() == "x"
            cls = "ws-task ws-done" if done else "ws-task"
            mark = "&#10003;" if done else ""
            out.append(
                f'<div class="{cls}"><span class="ws-box">{mark}</span>'
                f"<span>{inline_md(m.group(2))}</span></div>"
            )
            shown += 1
            continue
        if line.startswith(("- ", "* ")):
            out.append(f'<div class="ws-bullet">{inline_md(line[2:].strip())}</div>')
            shown += 1
            continue
        out.append(f'<div class="ws-line">{inline_md(line.lstrip(">").strip())}</div>')
        shown += 1
    if hidden:
        out.append(f'<div class="ws-more">... and {hidden} more</div>')
    return "\n".join(out)


# Phrases that indicate a pointer (external system) in agent.md
POINTER_PHRASES = [
    "tasks are tracked in",
    "lives in",
    "managed by",
    "use the",
    "connector",
    "not stored locally",
]


def detect_pointer_target(agent_text):
    """
    Check if agent.md text describes a pointer to an external system.
    Returns a short description of the pointer target, or None.
    """
    lower = agent_text.lower()
    for phrase in POINTER_PHRASES:
        if phrase in lower:
            # Try to extract the relevant line
            for line in agent_text.split("\n"):
                if phrase in line.lower():
                    cleaned = line.strip().lstrip("-").lstrip("*").strip()
                    return cleaned
            return "External system"
    return None


# ---------------------------------------------------------------------------
# Workspace content collection
# ---------------------------------------------------------------------------

def collect_workspace_items(root, scopes, folder_name):
    """
    Collect workspace items (todo/reminders/inbox) across all scopes.
    Returns a list of dicts with scope_name, scope_path, folder_type,
    pointer_target (or None), and content.
    """
    items = []

    def _process_scope(scope):
        name = scope.get("name", "Unknown")
        rel_path = scope.get("path", "")
        folder_types = scope.get("folder_types", {})
        ft_status = folder_types.get(folder_name, "empty")

        if ft_status == "empty":
            # Still check if the folder exists on disk (index may be stale)
            folder_dir = root / rel_path / folder_name
            if not folder_dir.exists():
                pass  # truly empty, skip
            else:
                ft_status = "data"  # folder exists but index said empty

        if ft_status in ("data", "pointer"):
            folder_dir = root / rel_path / folder_name
            agent_path = folder_dir / "agent.md"
            agent_text = read_file_text(agent_path)

            pointer_target = detect_pointer_target(agent_text)

            # Collect content files beyond boilerplate
            content_lines = []
            if folder_dir.exists():
                try:
                    for f in sorted(folder_dir.iterdir()):
                        if f.is_file() and f.name not in ("agent.md", "readme.md"):
                            text = read_file_text(f, max_bytes=4096)
                            if text.strip():
                                try:
                                    mtime = f.stat().st_mtime
                                except OSError:
                                    mtime = 0
                                content_lines.append({
                                    "filename": f.name,
                                    "text": text.strip(),
                                    "mtime": mtime,
                                })
                except PermissionError:
                    pass

            # Also extract any task-like lines from agent.md itself
            agent_tasks = []
            for line in agent_text.split("\n"):
                stripped = line.strip()
                if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
                    agent_tasks.append(stripped)

            items.append({
                "scope_name": name,
                "scope_path": rel_path,
                "folder_type": ft_status,
                "pointer_target": pointer_target,
                "content_files": content_lines,
                "agent_tasks": agent_tasks,
                "agent_text": agent_text,
            })

        # Recurse into children
        for child in scope.get("children", []):
            _process_scope(child)

    for scope in scopes:
        _process_scope(scope)

    return items


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def esc(text):
    """HTML-escape a string."""
    return html.escape(str(text)) if text else ""


def format_timestamp(ts_str):
    """Format an ISO timestamp to a human-readable string."""
    if not ts_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        return str(ts_str)


def time_ago(ts_str):
    """Return a human-friendly 'time ago' string."""
    if not ts_str:
        return "never"
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 0:
            return "just now"
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            mins = seconds // 60
            return f"{mins}m ago"
        if seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        days = seconds // 86400
        if days == 1:
            return "1 day ago"
        return f"{days} days ago"
    except (ValueError, AttributeError):
        return "unknown"


def health_status(lib):
    """Determine health status: healthy, warning, or failing."""
    consecutive = lib.get("consecutive_failures", 0)
    last_status = lib.get("last_status")
    if consecutive >= 3:
        return "failing"
    if consecutive >= 1 or last_status == "failure":
        return "warning"
    if last_status == "success":
        return "healthy"
    if last_status is None:
        return "unknown"
    return "healthy"


def dot_color(status):
    """CSS colour for a folder-type status dot."""
    if status == "data":
        return "#5a8a3c"   # warm green
    if status == "pointer":
        return "#4a7fa5"   # muted blue
    return "#b8a898"       # warm grey for empty


def health_color(status):
    """CSS colour for librarian health."""
    if status == "healthy":
        return "#5a8a3c"
    if status == "warning":
        return "#c4883a"
    if status == "failing":
        return "#b04a3a"
    return "#b8a898"


def render_css():
    """Return the complete CSS block."""
    return """
    :root {
      --bg: #faf6f1;
      --bg-card: #ffffff;
      --bg-card-hover: #fdf9f4;
      --bg-user: #f5ede3;
      --border: #e0d5c8;
      --border-light: #ebe3d8;
      --text: #3d3428;
      --text-muted: #8a7d6e;
      --text-light: #a69882;
      --accent: #c4883a;
      --accent-light: #e8c9a0;
      --green: #5a8a3c;
      --green-bg: #eef5e8;
      --amber: #c4883a;
      --amber-bg: #fdf3e6;
      --red: #b04a3a;
      --red-bg: #faeae8;
      --blue: #4a7fa5;
      --blue-bg: #eaf2f8;
      --grey: #b8a898;
      --tab-active: #c4883a;
      --tab-inactive: #d4c8b8;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      --mono: "SF Mono", "Fira Code", "Fira Mono", Menlo, Consolas, monospace;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
    }

    header {
      text-align: center;
      margin-bottom: 2rem;
    }

    header h1 {
      font-size: 1.6rem;
      font-weight: 600;
      color: var(--text);
      letter-spacing: -0.02em;
    }

    header .subtitle {
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-top: 0.25rem;
    }

    /* Tabs */
    .tabs {
      display: flex;
      gap: 0;
      border-bottom: 2px solid var(--border);
      margin-bottom: 1.5rem;
    }

    .tab {
      padding: 0.6rem 1.2rem;
      cursor: pointer;
      border: none;
      background: none;
      font-family: var(--font);
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--text-muted);
      border-bottom: 2px solid transparent;
      margin-bottom: -2px;
      transition: color 0.15s, border-color 0.15s;
    }

    .tab:hover {
      color: var(--text);
    }

    .tab.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
    }

    .tab-panel {
      display: none;
    }

    .tab-panel.active {
      display: block;
    }

    /* Cards */
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.2rem;
      margin-bottom: 0.75rem;
      transition: background 0.15s;
    }

    .card:hover {
      background: var(--bg-card-hover);
    }

    .card.user-scope {
      background: var(--bg-user);
      border-color: var(--accent-light);
    }

    .card.user-scope:hover {
      background: #f0e6d8;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 0.4rem;
    }

    .card-name {
      font-size: 1rem;
      font-weight: 600;
    }

    .card-badge {
      font-size: 0.72rem;
      font-weight: 500;
      padding: 0.15rem 0.5rem;
      border-radius: 10px;
      background: var(--border-light);
      color: var(--text-muted);
      white-space: nowrap;
    }

    .card-purpose {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }

    /* Folder-type dots */
    .folder-dots {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }

    .folder-dot {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.72rem;
      color: var(--text-muted);
    }

    .folder-dot .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
      flex-shrink: 0;
    }

    /* Scope nesting */
    .scope-children {
      margin-left: 1.5rem;
      padding-left: 0.75rem;
      border-left: 2px solid var(--border-light);
    }

    /* Librarian cards */
    .lib-card {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 0.75rem;
      align-items: start;
    }

    .lib-health-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-top: 0.3rem;
      flex-shrink: 0;
    }

    .lib-info {
      min-width: 0;
    }

    .lib-name {
      font-weight: 600;
      font-size: 0.95rem;
    }

    .lib-desc {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 0.15rem;
    }

    .lib-meta {
      display: flex;
      gap: 0.75rem;
      margin-top: 0.35rem;
      flex-wrap: wrap;
    }

    .lib-meta-item {
      font-size: 0.75rem;
      color: var(--text-light);
    }

    .lib-meta-item strong {
      color: var(--text-muted);
      font-weight: 500;
    }

    .lib-status {
      text-align: right;
      white-space: nowrap;
    }

    .lib-status-label {
      font-size: 0.78rem;
      font-weight: 500;
      padding: 0.15rem 0.55rem;
      border-radius: 10px;
    }

    .status-healthy { background: var(--green-bg); color: var(--green); }
    .status-warning { background: var(--amber-bg); color: var(--amber); }
    .status-failing { background: var(--red-bg); color: var(--red); }
    .status-unknown { background: var(--border-light); color: var(--text-muted); }

    .lib-last-run {
      font-size: 0.72rem;
      color: var(--text-light);
      margin-top: 0.25rem;
    }

    /* Run history */
    .run-history {
      margin-top: 1.5rem;
    }

    .run-history h3 {
      font-size: 0.95rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
      color: var(--text);
    }

    .run-entry {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem 0.75rem;
      border-bottom: 1px solid var(--border-light);
      font-size: 0.82rem;
    }

    .run-entry:last-child {
      border-bottom: none;
    }

    .run-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .run-cadence {
      color: var(--text-muted);
      min-width: 4rem;
    }

    .run-time {
      color: var(--text-light);
      min-width: 7rem;
    }

    .run-results {
      color: var(--text-muted);
      flex: 1;
    }

    /* Workspace views */
    .workspace-section {
      margin-bottom: 1.5rem;
    }

    .workspace-section h3 {
      font-size: 0.95rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
    }

    .workspace-scope {
      margin-bottom: 0.75rem;
    }

    .workspace-scope-name {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 0.3rem;
    }

    .workspace-pointer {
      font-size: 0.82rem;
      color: var(--blue);
      background: var(--blue-bg);
      padding: 0.4rem 0.75rem;
      border-radius: 6px;
      display: inline-block;
    }

    .workspace-content {
      font-size: 0.82rem;
      color: var(--text);
      padding: 0.4rem 0.75rem;
      background: var(--bg-card);
      border: 1px solid var(--border-light);
      border-radius: 6px;
      white-space: pre-wrap;
      font-family: var(--mono);
      line-height: 1.6;
      max-height: 300px;
      overflow-y: auto;
    }

    .workspace-empty {
      font-size: 0.82rem;
      color: var(--text-light);
      font-style: italic;
    }

    /* Cadence groups */
    .cadence-section {
      margin-top: 1.5rem;
    }

    .cadence-header {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
      padding-bottom: 0.3rem;
      border-bottom: 1px solid var(--border-light);
    }

    .cadence-meta {
      font-size: 0.72rem;
      color: var(--text-light);
      font-weight: 400;
      text-transform: none;
      letter-spacing: 0;
      float: right;
    }

    /* Empty states */
    .empty-state {
      text-align: center;
      padding: 3rem 1rem;
      color: var(--text-muted);
    }

    .empty-state h3 {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
    }

    .empty-state p {
      font-size: 0.9rem;
      color: var(--text-light);
      max-width: 400px;
      margin: 0 auto;
    }

    /* Footer */
    footer {
      text-align: center;
      margin-top: 3rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border-light);
      font-size: 0.75rem;
      color: var(--text-light);
    }

    /* Responsive */
    /* View toggle bar + graph filters */
    .view-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.6rem;
      margin-bottom: 1rem;
    }
    .view-toggle {
      display: inline-flex;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }
    .view-toggle button {
      border: none;
      background: var(--bg-card);
      color: var(--text-muted);
      font-family: var(--font);
      font-size: 0.82rem;
      font-weight: 600;
      padding: 0.35rem 0.9rem;
      cursor: pointer;
    }
    .view-toggle button.active {
      background: var(--accent);
      color: #fff;
    }
    .graph-filters {
      display: inline-flex;
      gap: 1rem;
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .graph-filters label { display: inline-flex; align-items: center; gap: 0.3rem; cursor: pointer; }
    .graph-mount svg { width: 100%; height: auto; display: block; }
    .gnode:hover circle { stroke: var(--accent); stroke-width: 2; }
    .gnode text { font-family: var(--font); }
    .card[data-scope] { cursor: pointer; }
    .card[data-scope]:hover { background: var(--bg-card-hover); border-color: var(--accent-light); }

    /* Container boxes for grouping folders */
    .group-box {
      border: 1.5px dashed var(--border);
      border-radius: 10px;
      padding: 0.9rem 0.9rem 0.2rem;
      margin-bottom: 0.75rem;
      background: rgba(255, 255, 255, 0.35);
    }
    .group-label {
      font-size: 0.72rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--text-light);
      margin-bottom: 0.5rem;
    }

    /* Guidance + hints */
    .guidance {
      color: var(--text-muted);
      font-size: 0.85rem;
      background: var(--bg-user);
      border-radius: 8px;
      padding: 0.6rem 0.9rem;
      margin: 1rem 0 0.5rem;
    }
    .hint {
      display: inline-block;
      position: relative;
      width: 1rem;
      height: 1rem;
      line-height: 1rem;
      text-align: center;
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--text-light);
      border: 1px solid var(--border);
      border-radius: 50%;
      margin-left: 0.4rem;
      cursor: help;
      vertical-align: middle;
    }
    .hint-pop {
      display: none;
      position: absolute;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%);
      width: 240px;
      background: var(--text);
      color: #f7f3ee;
      font-size: 0.78rem;
      font-weight: 400;
      line-height: 1.4;
      text-align: left;
      text-transform: none;
      letter-spacing: normal;
      padding: 0.55rem 0.7rem;
      border-radius: 8px;
      z-index: 30;
    }
    .hint:hover .hint-pop, .hint:focus .hint-pop { display: block; }

    /* Agent groups */
    details.agent-group {
      margin-bottom: 0.75rem;
    }
    details.agent-group > summary {
      cursor: pointer;
      list-style: none;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 0.4rem 0.2rem;
      color: var(--text);
    }
    details.agent-group > summary::before {
      content: "\\25B8";
      display: inline-block;
      margin-right: 0.5rem;
      color: var(--text-light);
      transition: transform 0.15s;
    }
    details.agent-group[open] > summary::before { transform: rotate(90deg); }
    .group-count {
      display: inline-block;
      background: var(--bg-user);
      color: var(--text-muted);
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: 10px;
      padding: 0.05rem 0.5rem;
      margin-left: 0.5rem;
    }
    details.exfu-group > summary { color: var(--text-muted); }
    details.exfu-group .card { opacity: 0.85; }

    /* Node sidebar */
    #side-panel {
      position: fixed;
      top: 0;
      right: 0;
      width: 320px;
      max-width: 88vw;
      height: 100vh;
      background: var(--bg-card);
      border-left: 1px solid var(--border);
      box-shadow: -6px 0 24px rgba(61, 52, 40, 0.08);
      padding: 1.2rem 1.2rem 2rem;
      overflow-y: auto;
      z-index: 40;
    }
    #side-panel h3 { font-size: 1.1rem; margin-bottom: 0.2rem; }
    #side-panel p { font-size: 0.88rem; color: var(--text-muted); margin: 0.4rem 0; }
    .panel-tag { font-size: 0.75rem; color: var(--accent); font-weight: 600; }
    .panel-section {
      font-size: 0.72rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--text-light);
      margin: 0.9rem 0 0.25rem;
    }
    .panel-mono { font-family: var(--mono); font-size: 0.78rem; color: var(--text-muted); }
    .panel-muted { color: var(--text-light); font-size: 0.8rem; }
    .panel-guidance {
      margin-top: 1.2rem;
      font-size: 0.8rem;
      color: var(--text-muted);
      background: var(--bg-user);
      border-radius: 8px;
      padding: 0.5rem 0.7rem;
    }
    .panel-prose { font-size: 0.83rem; color: var(--text); }
    .panel-prose .ws-heading { margin-top: 0.45rem; }
    details.panel-doc {
      border: 1px solid var(--border-light);
      border-radius: 6px;
      padding: 0.35rem 0.6rem;
      margin: 0.3rem 0;
      background: var(--bg-card);
    }
    details.panel-doc > summary {
      cursor: pointer;
      list-style: none;
      font-size: 0.83rem;
      font-weight: 600;
      color: var(--text-muted);
    }
    details.panel-doc > summary::before {
      content: "\\25B8";
      display: inline-block;
      margin-right: 0.4rem;
      color: var(--text-light);
      transition: transform 0.15s;
    }
    details.panel-doc[open] > summary::before { transform: rotate(90deg); }
    details.panel-doc[open] > summary { margin-bottom: 0.3rem; }
    .path-link { color: var(--blue); text-decoration: none; border-bottom: 1px dotted var(--blue); }
    .path-link:hover { color: var(--accent); border-bottom-color: var(--accent); }
    .copy-btn {
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text-muted);
      font-family: var(--font);
      font-size: 0.68rem;
      border-radius: 9px;
      padding: 0.05rem 0.5rem;
      margin-left: 0.4rem;
      cursor: pointer;
      vertical-align: middle;
    }
    .copy-btn:hover { color: var(--accent); border-color: var(--accent-light); }

    .panel-close {
      position: absolute;
      top: 0.6rem;
      right: 0.8rem;
      border: none;
      background: none;
      font-size: 1.3rem;
      color: var(--text-light);
      cursor: pointer;
    }

    /* Map meta + legend */
    .map-meta {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.5rem;
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }
    .map-legend { display: inline-flex; gap: 1rem; }
    .legend-item { display: inline-flex; align-items: center; gap: 0.35rem; }
    .legend-item .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }

    .card-eyebrow {
      font-size: 0.72rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--text-light);
      margin-bottom: 0.15rem;
    }

    .card-dim { opacity: 0.65; }

    .kind-badge {
      background: var(--amber-bg);
      color: var(--amber);
      font-size: 0.72rem;
      padding: 0.1rem 0.5rem;
      border-radius: 10px;
    }

    /* Workspace rendering */
    .chip {
      display: inline-block;
      background: var(--blue-bg);
      color: var(--blue);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.15rem 0.6rem;
      border-radius: 12px;
      white-space: nowrap;
    }
    .chip-quiet {
      background: var(--bg-user);
      color: var(--text-muted);
      font-weight: 500;
      margin-left: 0.5rem;
    }
    .ws-pointer-row { display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap; }
    .ws-pointer-detail { color: var(--text-muted); font-size: 0.85rem; }
    .ws-heading {
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--text-light);
      margin: 0.6rem 0 0.3rem;
    }
    .ws-task { display: flex; gap: 0.5rem; align-items: baseline; padding: 0.15rem 0; font-size: 0.9rem; }
    .ws-box {
      width: 1rem;
      height: 1rem;
      flex: none;
      border: 1.5px solid var(--border);
      border-radius: 4px;
      font-size: 0.7rem;
      line-height: 1rem;
      text-align: center;
      color: var(--green);
      background: var(--bg-card);
    }
    .ws-done { color: var(--text-light); }
    .ws-done .ws-box { background: var(--green-bg); border-color: var(--green-bg); }
    .ws-done span:last-child { text-decoration: line-through; }
    .ws-bullet { padding: 0.12rem 0 0.12rem 1rem; position: relative; font-size: 0.9rem; }
    .ws-bullet::before { content: "\\2022"; position: absolute; left: 0.25rem; color: var(--accent-light); }
    .ws-line { padding: 0.12rem 0; font-size: 0.9rem; }
    .ws-more { color: var(--text-light); font-size: 0.8rem; padding: 0.3rem 0; font-style: italic; }
    .ws-filename { font-weight: 600; font-size: 0.85rem; margin-top: 0.5rem; }
    .ws-body { margin-bottom: 0.4rem; }

    .inbox-card {
      border: 1px solid var(--border-light);
      border-radius: 6px;
      padding: 0.5rem 0.75rem;
      margin: 0.4rem 0;
      background: var(--bg-card);
    }
    .inbox-title { font-weight: 600; font-size: 0.9rem; }
    .inbox-snippet { color: var(--text-muted); font-size: 0.85rem; margin-top: 0.1rem; }
    .inbox-age { color: var(--text-light); font-size: 0.75rem; margin-top: 0.2rem; }

    @media (max-width: 700px) {
      .container { padding: 1rem; }
      .lib-card { grid-template-columns: auto 1fr; }
      .lib-status { grid-column: 1 / -1; text-align: left; }
      .scope-children { margin-left: 0.75rem; }
      .tab { padding: 0.5rem 0.8rem; font-size: 0.82rem; }
    }
    """


def render_tab_js():
    """Return the tab-switching JavaScript."""
    return """
    document.addEventListener('DOMContentLoaded', function() {
      var tabs = document.querySelectorAll('.tab');
      var panels = document.querySelectorAll('.tab-panel');

      tabs.forEach(function(tab) {
        tab.addEventListener('click', function() {
          var target = tab.getAttribute('data-tab');

          tabs.forEach(function(t) { t.classList.remove('active'); });
          panels.forEach(function(p) { p.classList.remove('active'); });

          tab.classList.add('active');
          var panel = document.getElementById(target);
          if (panel) panel.classList.add('active');
        });
      });
    });
    """


def grouping_label(scope):
    """Grouping-folder path between scopes/ and the scope dir, or ''."""
    segs = [s for s in scope.get("path", "").strip("/").split("/") if s]
    middle = segs[1:-1]
    if len(segs) > 2 and "scopes" not in middle and scope.get("type") != "user":
        return " / ".join(middle)
    return ""


def hint(text):
    """A small '?' that reveals an explanation on hover or focus."""
    return (
        '<span class="hint" tabindex="0">?'
        f'<span class="hint-pop">{esc(text)}</span></span>'
    )


def render_graph_js():
    """Client-side code: view toggles, radial graphs, node sidebar."""
    return """
(function () {
  var D = window.EXFU_DATA || { scopes: [], agents: [] };

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }
  function trunc(s, n) { return s.length > n ? s.slice(0, n - 1) + '...' : s; }
  function px(v) { return Math.round(v * 10) / 10; }

  var COL = {
    border: '#e0d5c8', text: '#3d3428', muted: '#8a7d6e', light: '#a69882',
    accent: '#c4883a', user: '#f5ede3', card: '#ffffff',
    green: '#5a8a3c', amber: '#c4883a', red: '#b04a3a', grey: '#b8a898',
    blue: '#4a7fa5'
  };
  function healthColor(st) {
    if (st === 'healthy') return COL.green;
    if (st === 'warning') return COL.amber;
    if (st === 'failing') return COL.red;
    return COL.grey;
  }

  function scopeByName(n) {
    for (var i = 0; i < D.scopes.length; i++) if (D.scopes[i].name === n) return D.scopes[i];
    return null;
  }
  function agentsForScope(name) {
    return D.agents.filter(function (a) { return a.scope === name && a.origin !== 'exfu'; });
  }

  /* ---- radial layout ---- */
  function layoutScopeGraph(showGroups, showAgents) {
    var nodes = [], edges = [];
    var user = null, tops = [], byName = {};
    D.scopes.forEach(function (s) {
      byName[s.name] = s;
      if (s.type === 'user') user = s;
      else if (s.parent === 'root') tops.push(s);
    });
    var cx = 450, cy = 320;
    nodes.push({ id: 'u', x: cx, y: cy, r: 30, stype: 'user', name: user ? user.name : 'You', data: user });

    var ring = [], seenGroups = {};
    tops.forEach(function (s) {
      if (s.group && showGroups) {
        if (!seenGroups[s.group]) {
          seenGroups[s.group] = true;
          ring.push({ kind: 'group', label: s.group,
                      members: tops.filter(function (t) { return t.group === s.group; }) });
        }
      } else {
        ring.push({ kind: 'scope', scope: s });
      }
    });

    var weights = ring.map(function (e) {
      if (e.kind === 'group') return Math.max(1.6, e.members.length);
      var w = 1 + (e.scope.children || []).length * 0.6;
      if (showAgents) w += agentsForScope(e.scope.name).length * 0.3;
      return w;
    });
    var total = weights.reduce(function (a, b) { return a + b; }, 0) || 1;
    var angle = -Math.PI / 2;

    function addScopeNode(s, x, y, baseAngle, span) {
      var fts = s.folderTypes || {};
      var size = 13 + Math.min(12, Object.keys(fts).length * 2);
      var id = 's:' + s.name;
      nodes.push({ id: id, x: x, y: y, r: size, stype: 'scope', name: s.name, data: s });
      var kids = (s.children || []).map(function (n) { return byName[n]; }).filter(Boolean);
      kids.forEach(function (k, i) {
        var ka = baseAngle + (i - (kids.length - 1) / 2) * Math.min(0.5, span / Math.max(1, kids.length));
        var kx = cx + Math.cos(ka) * (Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) + 115);
        var ky = cy + Math.sin(ka) * (Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) + 115);
        edges.push({ x1: x, y1: y, x2: kx, y2: ky, dash: false });
        addScopeNode(k, kx, ky, ka, span / 2);
      });
      if (showAgents) {
        var ags = agentsForScope(s.name);
        ags.forEach(function (a, i) {
          var aa = baseAngle + (i - (ags.length - 1) / 2) * 0.22 + 0.0;
          var rr = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) + 70;
          var ax = cx + Math.cos(aa) * rr, ay = cy + Math.sin(aa) * rr;
          edges.push({ x1: x, y1: y, x2: ax, y2: ay, dash: true });
          nodes.push({ id: 'a:' + a.name, x: ax, y: ay, r: 7, stype: 'agent', name: a.name, data: a });
        });
      }
    }

    ring.forEach(function (e, idx) {
      var span = (weights[idx] / total) * Math.PI * 2;
      var mid = angle + span / 2;
      angle += span;
      var R1 = 165;
      var x = cx + Math.cos(mid) * R1, y = cy + Math.sin(mid) * R1;
      if (e.kind === 'group') {
        nodes.push({ id: 'g:' + e.label, x: x, y: y, r: 12, stype: 'group', name: e.label, data: e });
        edges.push({ x1: cx, y1: cy, x2: x, y2: y, dash: true });
        e.members.forEach(function (m, i) {
          var ma = mid + (i - (e.members.length - 1) / 2) * Math.min(0.45, span / e.members.length);
          var mx = cx + Math.cos(ma) * (R1 + 120), my = cy + Math.sin(ma) * (R1 + 120);
          edges.push({ x1: x, y1: y, x2: mx, y2: my, dash: false });
          addScopeNode(m, mx, my, ma, span / Math.max(1, e.members.length));
        });
      } else {
        edges.push({ x1: cx, y1: cy, x2: x, y2: y, dash: false });
        addScopeNode(e.scope, x, y, mid, span);
      }
    });
    return { nodes: nodes, edges: edges, w: 900, h: 640 };
  }

  function layoutAgentsGraph(showLib, showBiz, showExfu) {
    var nodes = [], edges = [];
    var cx = 450, cy = 300;
    nodes.push({ id: 'u', x: cx, y: cy, r: 28, stype: 'user', name: 'You', data: null });
    var hubs = {};
    D.agents.forEach(function (a) {
      if (a.origin === 'exfu') { if (!showExfu) return; }
      else if (a.kind === 'librarian' && !showLib) return;
      else if (a.kind === 'agent' && !showBiz) return;
      var hub = a.origin === 'exfu' ? 'ExFu' : (a.scope || 'Your substrate');
      (hubs[hub] = hubs[hub] || []).push(a);
    });
    var names = Object.keys(hubs);
    var n = names.length || 1;
    names.forEach(function (h, i) {
      var ang = -Math.PI / 2 + (i / n) * Math.PI * 2;
      var hx = cx + Math.cos(ang) * 150, hy = cy + Math.sin(ang) * 150;
      var hubScope = scopeByName(h);
      nodes.push({ id: 'h:' + h, x: hx, y: hy, r: 14,
                   stype: hubScope ? 'scope' : 'group', name: h, data: hubScope || { label: h } });
      edges.push({ x1: cx, y1: cy, x2: hx, y2: hy, dash: false });
      hubs[h].forEach(function (a, j) {
        var aa = ang + (j - (hubs[h].length - 1) / 2) * 0.3;
        var ax = cx + Math.cos(aa) * 255, ay = cy + Math.sin(aa) * 255;
        edges.push({ x1: hx, y1: hy, x2: ax, y2: ay, dash: true });
        nodes.push({ id: 'a:' + a.name, x: ax, y: ay, r: 8, stype: 'agent', name: a.name, data: a });
      });
    });
    return { nodes: nodes, edges: edges, w: 900, h: 600 };
  }

  function drawGraph(mount, model) {
    var s = '<svg viewBox="0 0 ' + model.w + ' ' + model.h + '" xmlns="http://www.w3.org/2000/svg">';
    model.edges.forEach(function (e) {
      s += '<line x1="' + px(e.x1) + '" y1="' + px(e.y1) + '" x2="' + px(e.x2) + '" y2="' + px(e.y2) +
           '" stroke="' + COL.border + '" stroke-width="1.3"' + (e.dash ? ' stroke-dasharray="4 4"' : '') + '/>';
    });
    model.nodes.forEach(function (nd) {
      s += '<g class="gnode" data-stype="' + nd.stype + '" data-name="' + esc(nd.name) + '" cursor="pointer">';
      var fill = COL.card, stroke = COL.border, dash = '';
      if (nd.stype === 'user') { fill = COL.user; stroke = COL.accent; }
      if (nd.stype === 'group') { fill = '#faf6f1'; dash = ' stroke-dasharray="3 3"'; }
      if (nd.stype === 'agent') {
        fill = healthColor(nd.data && nd.data.status);
        stroke = 'none';
        if (nd.data && nd.data.status === 'unregistered') { fill = COL.card; stroke = COL.grey; dash = ' stroke-dasharray="3 2"'; }
      }
      s += '<circle cx="' + px(nd.x) + '" cy="' + px(nd.y) + '" r="' + nd.r + '" fill="' + fill + '"' +
           (stroke === 'none' ? '' : ' stroke="' + stroke + '" stroke-width="1.5"') + dash + '/>';
      var fs = nd.stype === 'user' ? 13 : (nd.stype === 'agent' ? 10 : 12);
      var fw = nd.stype === 'agent' ? 'normal' : '600';
      var col = nd.stype === 'agent' ? COL.muted : COL.text;
      s += '<text x="' + px(nd.x) + '" y="' + px(nd.y + nd.r + (nd.stype === 'agent' ? 11 : 15)) +
           '" text-anchor="middle" font-size="' + fs + '" font-weight="' + fw + '" fill="' + col + '">' +
           esc(trunc(nd.name, 18)) + '</text>';
      s += '</g>';
    });
    s += '</svg>';
    mount.innerHTML = s;
  }

  /* ---- sidebar ---- */
  function dotRow(label, color) {
    return '<span class="folder-dot"><span class="dot" style="background:' + color + '"></span>' + esc(label) + '</span>';
  }
  function openPanel(html) {
    var p = document.getElementById('side-panel');
    p.querySelector('.panel-body').innerHTML = html;
    p.hidden = false;
  }
  function panelForScope(sc) {
    if (!sc) return;
    var h = '<h3>' + esc(sc.name) + '</h3>';
    if (sc.type === 'user') h += '<div class="panel-tag">your personal scope</div>';
    if (sc.purpose) h += '<p>' + esc(sc.purpose) + '</p>';
    if (sc.aboutHtml) {
      h += '<div class="panel-section">About</div><div class="panel-prose">' + sc.aboutHtml + '</div>';
    }
    var absPath = (D.root || '') + '/' + (sc.path || '');
    h += '<div class="panel-section">Where</div><div class="panel-mono">' +
         '<a class="path-link" href="file://' + encodeURI(absPath) + '">' + esc(sc.path || '') + '</a>' +
         ' <button class="copy-btn" data-copy="' + esc(absPath) + '">copy</button>' +
         '</div>';
    if (sc.version) h += '<div class="panel-section">Conventions</div><div>ExFu ' + esc(sc.version) + '</div>';
    var fts = sc.folderTypes || {};
    var keys = Object.keys(fts).sort();
    if (keys.length) {
      h += '<div class="panel-section">What lives here</div><div class="folder-dots">';
      keys.forEach(function (k) {
        h += dotRow(k, fts[k] === 'pointer' ? COL.blue : COL.green);
      });
      h += '</div>';
    }
    var ags = agentsForScope(sc.name);
    if (ags.length) {
      h += '<div class="panel-section">Agents</div>';
      ags.forEach(function (a) {
        h += '<div>' + dotRow(a.name, healthColor(a.status)) +
             ' <span class="panel-muted">' + esc(a.cadence || '') + '</span></div>';
      });
    }
    if ((sc.children || []).length) {
      h += '<div class="panel-section">Inside it</div><div>' + sc.children.map(esc).join(', ') + '</div>';
    }
    if (sc.context && sc.context.length) {
      h += '<div class="panel-section">Context</div>';
      sc.context.forEach(function (c, i) {
        h += '<details class="panel-doc"' + (i === 0 ? ' open' : '') + '>' +
             '<summary>' + esc(c.title) + '</summary>' +
             '<div class="panel-prose">' + c.html + '</div></details>';
      });
      if (sc.contextMore) {
        h += '<div class="panel-muted">... and ' + sc.contextMore + ' more in the folder</div>';
      }
    }
    h += '<div class="panel-guidance">Ask your AI about this scope by name -- it knows where everything lives.</div>';
    openPanel(h);
  }
  function panelForAgent(a) {
    if (!a) return;
    var h = '<h3>' + esc(a.name) + '</h3>';
    h += '<div class="panel-tag">' + (a.kind === 'agent' ? 'business agent' : 'librarian') +
         (a.origin === 'exfu' ? ' &middot; ships with ExFu' : '') + '</div>';
    if (a.description) h += '<p>' + esc(a.description) + '</p>';
    h += '<div class="panel-section">Status</div><div>' + dotRow(
      a.registered ? a.status : 'not installed', healthColor(a.status)) + '</div>';
    if (a.cadence) h += '<div class="panel-section">Cadence</div><div>' + esc(a.cadence) + '</div>';
    if (a.scope) h += '<div class="panel-section">Scope</div><div>' + esc(a.scope) + '</div>';
    h += '<div class="panel-guidance">' + (a.registered
      ? 'To change or pause it, just tell your AI.'
      : 'Staged, not yet running. Tell your AI "install ' + esc(a.name) + '" to switch it on.') + '</div>';
    openPanel(h);
  }
  function panelForGroup(g) {
    var label = g && (g.label || g.name) || '';
    var h = '<h3>' + esc(label) + ' /</h3>' +
            '<div class="panel-tag">grouping folder</div>' +
            '<p>Organisation only -- it gathers related scopes but is not a scope itself.</p>';
    var members = D.scopes.filter(function (s) { return s.group === label; });
    if (members.length) {
      h += '<div class="panel-section">Contains</div><div>' +
           members.map(function (m) { return esc(m.name); }).join(', ') + '</div>';
    }
    openPanel(h);
  }

  function onNodeClick(g) {
    var t = g.getAttribute('data-stype'), n = g.getAttribute('data-name');
    if (t === 'agent') panelForAgent(D.agents.filter(function (a) { return a.name === n; })[0]);
    else if (t === 'group') panelForGroup({ label: n });
    else panelForScope(scopeByName(n));
  }

  /* ---- wiring ---- */
  function renderGraphs() {
    var sg = document.getElementById('scope-graph');
    if (sg && sg.offsetParent !== null) {
      drawGraph(sg, layoutScopeGraph(
        document.getElementById('f-groups').checked,
        document.getElementById('f-agents').checked));
    }
    var ag = document.getElementById('agents-graph');
    if (ag && ag.offsetParent !== null) {
      drawGraph(ag, layoutAgentsGraph(
        document.getElementById('f-lib').checked,
        document.getElementById('f-biz').checked,
        document.getElementById('f-exfu').checked));
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.view-toggle button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var bar = btn.closest('.tab-panel');
        bar.querySelectorAll('.view-toggle button').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var target = btn.getAttribute('data-view');
        bar.querySelectorAll('[data-pane]').forEach(function (p) {
          p.style.display = p.getAttribute('data-pane') === target ? '' : 'none';
        });
        renderGraphs();
      });
    });
    document.querySelectorAll('.graph-filters input').forEach(function (cb) {
      cb.addEventListener('change', renderGraphs);
    });
    document.addEventListener('click', function (ev) {
      var g = ev.target.closest ? ev.target.closest('.gnode') : null;
      if (g) { onNodeClick(g); return; }
      var card = ev.target.closest ? ev.target.closest('[data-scope]') : null;
      if (card && !(ev.target.closest('a') || ev.target.closest('button'))) {
        panelForScope(scopeByName(card.getAttribute('data-scope')));
      }
    });
    var closeBtn = document.querySelector('#side-panel .panel-close');
    if (closeBtn) closeBtn.addEventListener('click', function () {
      document.getElementById('side-panel').hidden = true;
    });
    document.addEventListener('click', function (ev) {
      var b = ev.target.closest ? ev.target.closest('.copy-btn') : null;
      if (!b) return;
      var t = b.getAttribute('data-copy') || '';
      function done() {
        b.textContent = 'copied';
        setTimeout(function () { b.textContent = 'copy'; }, 1500);
      }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = t;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) {}
        document.body.removeChild(ta);
        done();
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(t).then(done, fallback);
      } else {
        fallback();
      }
    });
  });
})();
"""


def render_scope_card(scope, is_user=False):
    """Render a scope card as HTML."""
    name = esc(scope.get("name", "Unknown"))
    purpose = esc(scope.get("purpose", ""))
    exfu_ver = scope.get("exfu_version")
    folder_types = scope.get("folder_types", {})

    card_class = "card user-scope" if is_user else "card"

    parts = [f'<div class="{card_class}" data-scope="{name}">']

    parts.append('<div class="card-header">')
    parts.append(f'<span class="card-name">{name}</span>')

    badges = []
    if is_user:
        badges.append("personal")
    if exfu_ver:
        badges.append(esc(exfu_ver))
    if badges:
        parts.append(f'<span class="card-badge">{" / ".join(badges)}</span>')

    parts.append("</div>")

    if purpose:
        parts.append(f'<div class="card-purpose">{purpose}</div>')

    # Folder-type dots
    if folder_types:
        parts.append('<div class="folder-dots">')
        for ft_name, ft_status in sorted(folder_types.items()):
            color = dot_color(ft_status)
            label = esc(ft_name)
            parts.append(
                f'<span class="folder-dot">'
                f'<span class="dot" style="background:{color}"></span>'
                f'{label}</span>'
            )
        parts.append("</div>")

    parts.append("</div>")

    # Children
    children = scope.get("children", [])
    if children:
        parts.append('<div class="scope-children">')
        for child in children:
            parts.append(render_scope_card(child, is_user=False))
        parts.append("</div>")

    return "\n".join(parts)


def render_substrate_map(index_data):
    """Render the substrate map view."""
    if index_data is None:
        return (
            '<div class="empty-state">'
            "<h3>No substrate index found</h3>"
            "<p>Run the nightly index first to populate this view. "
            "The index librarian walks your substrate and builds the map.</p>"
            "</div>"
        )

    scopes = index_data.get("scopes", [])
    versions = index_data.get("exfu_versions", {})

    if not scopes:
        return (
            '<div class="empty-state">'
            "<h3>No scopes found</h3>"
            "<p>Your substrate exists but has no scopes yet. "
            "Create your first scope to see it here.</p>"
            "</div>"
        )

    # Conventions summary + legend
    parts = []
    ver_items = []
    if versions:
        for ver_name, ver_info in sorted(versions.items()):
            label = esc(ver_name)
            count = len(ver_info.get("scopes_using", []))
            is_latest = ver_info.get("is_latest", False)
            suffix = ", the latest" if is_latest else ""
            ver_items.append(f"ExFu {label}{suffix} -- followed by {count} scope{'s' if count != 1 else ''}")
    parts.append('<div class="map-meta">')
    if ver_items:
        parts.append(f'<span class="map-conventions">Conventions: {", ".join(ver_items)}</span>')
    parts.append(
        '<span class="map-legend">'
        '<span class="legend-item"><span class="dot" style="background:#5a8a3c"></span>stored here</span>'
        '<span class="legend-item"><span class="dot" style="background:#4a7fa5"></span>managed elsewhere</span>'
        "</span>"
    )
    parts.append("</div>")

    # Render scope cards; grouped scopes sit inside container boxes
    rendered_groups = set()
    for scope in scopes:
        is_user = scope.get("type") == "user"
        grp = grouping_label(scope)
        if not grp:
            parts.append(render_scope_card(scope, is_user=is_user))
            continue
        if grp in rendered_groups:
            continue
        rendered_groups.add(grp)
        members = [s for s in scopes if grouping_label(s) == grp]
        parts.append(
            f'<div class="group-box"><div class="group-label">{esc(grp)} /'
            + hint("A grouping folder: organisation only, not a scope of its own.")
            + "</div>"
        )
        for m in members:
            parts.append(render_scope_card(m, is_user=False))
        parts.append("</div>")

    parts.append(
        '<div class="guidance">To create a scope, tell your AI: '
        '"Set up a new scope for ..." -- it scaffolds the folders and the next '
        "index picks it up.</div>"
    )

    return "\n".join(parts)


def find_unregistered_definitions(root, index_data, registry_data):
    """
    Scheduled-agent definition files sitting in scope librarians/ or
    scheduled/ folders but absent from the registry. A legitimate resting
    state -- staged work awaiting the user's approval -- worth surfacing.
    """
    registered = set()
    if registry_data:
        registered = {a.get("name") for a in registry_data.get("agents", [])}
    found = []

    def _scan_scope(scope):
        rel = scope.get("path", "")
        for folder, default_kind in (("librarians", "librarian"), ("scheduled", "agent")):
            d = root / rel / folder
            if not d.is_dir():
                continue
            try:
                files = sorted(d.iterdir())
            except OSError:
                continue
            for f in files:
                if (not f.is_file() or f.suffix != ".md"
                        or f.name in ("agent.md", "readme.md")):
                    continue
                fields = parse_yaml_frontmatter(read_file_text(f, max_bytes=2048))
                name = fields.get("name")
                if not name or "cadence" not in fields or name in registered:
                    continue
                found.append({
                    "name": name,
                    "kind": fields.get("kind", default_kind),
                    "cadence": fields.get("cadence", ""),
                    "description": fields.get("description", ""),
                    "scope": scope.get("name", ""),
                })
        for child in scope.get("children", []):
            _scan_scope(child)

    if index_data:
        for scope in index_data.get("scopes", []):
            _scan_scope(scope)
    return found


def render_librarian_card(lib):
    """Render a single librarian card."""
    name = esc(lib.get("name", "unknown"))
    desc = esc(lib.get("description", ""))
    cadence = esc(lib.get("cadence", ""))
    kind = esc(lib.get("kind", "librarian"))
    enabled = lib.get("enabled", True)
    last_run = lib.get("last_run")
    consecutive = lib.get("consecutive_failures", 0)

    status = health_status(lib)
    color = health_color(status)

    status_class = f"status-{status}"
    status_label = status.capitalize()

    if not enabled:
        status_class = "status-unknown"
        status_label = "Disabled"

    parts = ['<div class="card card-dim">' if not enabled else '<div class="card">']
    parts.append('<div class="lib-card">')

    # Health dot
    parts.append(
        f'<div class="lib-health-dot" style="background:{color}"></div>'
    )

    # Info
    parts.append('<div class="lib-info">')
    parts.append(f'<div class="lib-name">{name}</div>')
    if desc:
        parts.append(f'<div class="lib-desc">{desc}</div>')

    parts.append('<div class="lib-meta">')
    if cadence:
        parts.append(f'<span class="lib-meta-item"><strong>Cadence:</strong> {cadence}</span>')
    if kind == "agent":
        parts.append('<span class="kind-badge">business agent</span>')
    if consecutive > 0:
        parts.append(
            f'<span class="lib-meta-item" style="color:var(--red)">'
            f"<strong>Failures:</strong> {consecutive} consecutive</span>"
        )
    parts.append("</div>")  # lib-meta
    parts.append("</div>")  # lib-info

    # Status badge. The dashboard generator renders itself as "this run":
    # the page being viewed IS its output, so stale registry data about it
    # would be misleading. It never adjusts state for any other agent.
    is_self = lib.get("name") == "dashboard-generator"
    if is_self and enabled and status == "unknown":
        status_class = "status-healthy"
        status_label = "Healthy"
    parts.append('<div class="lib-status">')
    parts.append(f'<span class="lib-status-label {status_class}">{status_label}</span>')
    if is_self:
        parts.append('<div class="lib-last-run">this run</div>')
    elif last_run:
        parts.append(f'<div class="lib-last-run">{time_ago(last_run)}</div>')
    else:
        parts.append('<div class="lib-last-run">Not yet run</div>')
    parts.append("</div>")  # lib-status

    parts.append("</div>")  # lib-card
    parts.append("</div>")  # card

    return "\n".join(parts)


def render_log_entry(entry):
    """Render a single log entry (one librarian outcome)."""
    cadence = esc(entry.get("cadence", "") or "")
    name = esc(entry.get("name", ""))
    at = entry.get("at", "")
    status = entry.get("status", "")
    detail = esc(entry.get("detail", "") or "")

    if status == "failure":
        dot_col = "var(--red)"
    elif status == "skipped":
        dot_col = "var(--amber)"
    else:
        dot_col = "var(--green)"

    text = f"{name}: {esc(status)}"
    if detail:
        text += f" -- {detail}"

    return (
        '<div class="run-entry">'
        f'<span class="run-dot" style="background:{dot_col}"></span>'
        f'<span class="run-cadence">{cadence}</span>'
        f'<span class="run-time">{format_timestamp(at)}</span>'
        f'<span class="run-results">{text}</span>'
        "</div>"
    )


def render_librarian_dashboard(registry_data, log_data, unregistered=None):
    """Render the scheduled-agents view."""
    if registry_data is None:
        return (
            '<div class="empty-state">'
            "<h3>No agent registry found</h3>"
            "<p>The scheduled-agent framework has not been set up yet. "
            "Once scheduled agents are registered, their health will appear here.</p>"
            "</div>"
        )

    librarians = registry_data.get("agents", [])
    cadences = registry_data.get("cadences", {})

    if not librarians:
        return (
            '<div class="empty-state">'
            "<h3>No scheduled agents registered</h3>"
            "<p>The registry exists but has no scheduled agents. "
            "Register one to see it here.</p>"
            "</div>"
        )

    parts = []

    # Status strip: one line per cadence with its last run
    strip_bits = []
    for cadence_name in sorted(cadences.keys()):
        last_run = cadences.get(cadence_name, {}).get("last_run")
        strip_bits.append(
            f"<strong>{esc(cadence_name.capitalize())}</strong>: {time_ago(last_run)}"
        )
    if strip_bits:
        parts.append(
            '<div class="map-meta"><span>'
            + " &nbsp;&middot;&nbsp; ".join(strip_bits)
            + "</span>"
            + '<span class="map-conventions">'
            + hint(
                "Agents are recurring jobs your AI runs for you on a schedule "
                "(e.g. Claude Cowork Scheduled tasks). Librarians are special "
                "agents that keep the substrate itself tidy; business agents do "
                "your domain work, like scanning listings or drafting digests."
            )
            + " what's an agent?</span></div>"
        )

    # Your agents first, grouped by scope so you can collapse or focus
    exfu_agents = [a for a in librarians if a.get("origin", "user") == "exfu"]
    user_agents = [a for a in librarians if a.get("origin", "user") != "exfu"]

    if user_agents:
        by_scope = {}
        for a in user_agents:
            by_scope.setdefault(a.get("scope_name") or "Your substrate", []).append(a)
        for scope_name in sorted(by_scope.keys()):
            group = sorted(
                by_scope[scope_name],
                key=lambda l: 0 if l.get("kind", "librarian") == "librarian" else 1,
            )
            parts.append('<details class="agent-group" open>')
            parts.append(
                f"<summary>{esc(scope_name)}"
                f'<span class="group-count">{len(group)}</span></summary>'
            )
            for lib in group:
                parts.append(render_librarian_card(lib))
            parts.append("</details>")
    elif not unregistered:
        parts.append(
            '<div class="guidance">No agents of your own yet. To create one, '
            "describe the job to your AI: \"Every Monday, scan ... and note "
            'anything new in scope X." It writes the definition and stages it '
            "here for your approval.</div>"
        )

    # Definitions found in the substrate but not registered
    if unregistered:
        parts.append('<div class="cadence-section">')
        parts.append('<div class="cadence-header">Found, not installed</div>')
        for u in unregistered:
            meta_bits = []
            if u.get("cadence"):
                meta_bits.append(
                    f'<span class="lib-meta-item"><strong>Cadence:</strong> {esc(u["cadence"])}</span>'
                )
            if u.get("scope"):
                meta_bits.append(
                    f'<span class="lib-meta-item"><strong>Scope:</strong> {esc(u["scope"])}</span>'
                )
            if u.get("kind") == "agent":
                meta_bits.append('<span class="kind-badge">business agent</span>')
            desc_html = (
                f'<div class="lib-desc">{esc(u["description"])}</div>'
                if u.get("description") else ""
            )
            parts.append(
                '<div class="card card-dim"><div class="lib-card">'
                '<div class="lib-health-dot" style="background:#b8a898"></div>'
                '<div class="lib-info">'
                f'<div class="lib-name">{esc(u["name"])}</div>'
                f"{desc_html}"
                f'<div class="lib-meta">{"".join(meta_bits)}</div>'
                "</div>"
                '<div class="lib-status">'
                '<span class="lib-status-label status-unknown">Not installed</span>'
                '<div class="lib-last-run">ask your AI to install it</div>'
                "</div></div></div>"
            )
        parts.append("</div>")

    # ExFu's own agents: collapsed by default, at the bottom. Housekeeping,
    # not headline.
    if exfu_agents:
        parts.append('<details class="agent-group exfu-group">')
        parts.append(
            f"<summary>ExFu agents"
            f'<span class="group-count">{len(exfu_agents)}</span>'
            + hint(
                "These ship with ExFu and keep the foundations healthy: the "
                "index that maps your scopes, the inbox sweep, and this "
                "dashboard. You rarely need to touch them."
            )
            + "</summary>"
        )
        for lib in exfu_agents:
            parts.append(render_librarian_card(lib))
        parts.append("</details>")

    parts.append(
        '<div class="guidance">To create an agent, describe the job to your AI '
        "in a conversation: \"Every Monday, scan ... and note anything new in "
        'scope X." It writes the definition into that scope and stages it here '
        "for your approval.</div>"
    )

    # Run history
    if log_data and log_data.get("entries"):
        entries = log_data["entries"]
        # Show the last 15 outcomes, most recent first
        recent = list(reversed(entries[-15:]))

        parts.append('<div class="run-history">')
        parts.append("<h3>Recent runs</h3>")
        for entry in recent:
            parts.append(render_log_entry(entry))
        parts.append("</div>")

    return "\n".join(parts)


def render_workspace_folder(items, folder_label, folder_kind):
    """
    Render a workspace section (todo, reminders, or inbox).
    Sections with nothing to show are simply absent.
    """
    if not items:
        return ""

    parts = [f'<div class="workspace-section">', f"<h3>{esc(folder_label)}</h3>"]

    for item in items:
        scope_name = esc(item["scope_name"])
        pointer = item.get("pointer_target")
        content_files = item.get("content_files", [])
        agent_tasks = item.get("agent_tasks", [])

        # done.md / archive.md hold what's finished -- not "on my plate"
        content_files = [
            cf for cf in content_files
            if cf["filename"] not in ("done.md", "archive.md")
        ]

        # Nothing left to show for this scope? Show nothing.
        if not (pointer or content_files or agent_tasks):
            continue

        parts.append('<div class="workspace-scope">')
        parts.append(f'<div class="workspace-scope-name">{scope_name}</div>')

        if pointer:
            tool = pointer_tool_name(pointer)
            chip = f"Managed in {tool}" if tool else "Managed elsewhere"
            parts.append(
                '<div class="ws-pointer-row">'
                f'<span class="chip">{esc(chip)}</span>'
                f'<span class="ws-pointer-detail">{inline_md(pointer)}</span>'
                "</div>"
            )
        elif folder_kind == "inbox" and content_files:
            for cf in content_files[:8]:
                fields = parse_yaml_frontmatter(cf["text"])
                body = strip_frontmatter(cf["text"])
                title = deslug(cf["filename"])
                snippet = first_snippet(body)
                age = file_age_label(cf.get("mtime"))
                status = fields.get("status", "")
                parts.append('<div class="inbox-card">')
                title_html = esc(title)
                if status:
                    title_html += f'<span class="chip chip-quiet">{esc(status)}</span>'
                parts.append(f'<div class="inbox-title">{title_html}</div>')
                if snippet:
                    parts.append(f'<div class="inbox-snippet">{inline_md(snippet)}</div>')
                if age:
                    parts.append(f'<div class="inbox-age">{esc(age)}</div>')
                parts.append("</div>")
            if len(content_files) > 8:
                parts.append(
                    f'<div class="ws-more">... and {len(content_files) - 8} more</div>'
                )
        elif content_files:
            for cf in content_files:
                body = strip_frontmatter(cf["text"])
                if len(content_files) > 1:
                    parts.append(
                        f'<div class="ws-filename">{esc(deslug(cf["filename"]))}</div>'
                    )
                parts.append(f'<div class="ws-body">{render_markdown_mini(body)}</div>')
        elif agent_tasks:
            parts.append(
                f'<div class="ws-body">{render_markdown_mini(chr(10).join(agent_tasks))}</div>'
            )
        else:
            parts.append('<div class="workspace-empty">Empty</div>')

        parts.append("</div>")

    parts.append("</div>")
    return "\n".join(parts)


def render_workspace_views(root, index_data):
    """Render the workspace views tab."""
    if index_data is None:
        return (
            '<div class="empty-state">'
            "<h3>No substrate index found</h3>"
            "<p>Run the nightly index first. Workspace views need the index "
            "to know where to look for todo, reminders, and inbox items.</p>"
            "</div>"
        )

    scopes = index_data.get("scopes", [])

    todo_items = collect_workspace_items(root, scopes, "todo")
    reminder_items = collect_workspace_items(root, scopes, "reminders")
    inbox_items = collect_workspace_items(root, scopes, "inbox")

    # Filter out empty items (no pointer, no content, no tasks)
    def has_content(item):
        return (
            item.get("pointer_target")
            or item.get("content_files")
            or item.get("agent_tasks")
        )

    todo_items = [i for i in todo_items if has_content(i)]
    reminder_items = [i for i in reminder_items if has_content(i)]
    inbox_items = [i for i in inbox_items if has_content(i)]

    if not todo_items and not reminder_items and not inbox_items:
        return (
            '<div class="empty-state">'
            "<h3>Nothing in your workspace yet</h3>"
            "<p>Todo items, reminders, and inbox items from your scopes "
            "will appear here once they have content.</p>"
            "</div>"
        )

    parts = [
        render_workspace_folder(todo_items, "Todo", "todo"),
        render_workspace_folder(reminder_items, "Reminders", "reminders"),
        render_workspace_folder(inbox_items, "Inbox", "inbox"),
    ]

    return "\n".join(p for p in parts if p)


def flatten_scopes(index_data):
    """All scopes (user + working + nested) as a flat list."""
    flat = []

    def _walk(s):
        flat.append(s)
        for c in s.get("children", []):
            _walk(c)

    if index_data:
        for s in index_data.get("scopes", []):
            _walk(s)
    return flat


def enrich_agents(registry_data, unregistered, scopes_flat):
    """
    Attach origin (exfu | user) and scope_name to every agent entry.
    Origin comes from the definition's source path: the convention base's
    own agents are ExFu's; everything else belongs to the user.
    """
    paths = sorted(
        ((s.get("path", ""), s.get("name", "")) for s in scopes_flat),
        key=lambda t: -len(t[0]),
    )
    if registry_data:
        for a in registry_data.get("agents", []):
            src = str(a.get("source", ""))
            a["origin"] = "exfu" if src.startswith("exfu/") else "user"
            a["scope_name"] = ""
            if a["origin"] == "user":
                for p, n in paths:
                    if p and src.startswith(p):
                        a["scope_name"] = n
                        break
    for u in unregistered or []:
        u["origin"] = "user"
        u["scope_name"] = u.get("scope", "")


def collect_scope_docs(root, scope):
    """
    Scope-level prose for the sidebar: the scope.md body, a root readme.md
    if one exists, and capped excerpts of the context/ folder (its own
    readme.md first -- that's the human intro). Pre-rendered to safe HTML.
    """
    base = root / scope.get("path", "")
    about_parts = []
    sc_text = read_file_text(base / "scope.md", max_bytes=4096)
    if sc_text:
        body = strip_frontmatter(sc_text)
        # drop the protective header blockquote; it's plumbing
        body = "\n".join(
            l for l in body.split("\n") if not l.strip().startswith(">")
        ).strip()
        if body:
            about_parts.append(render_markdown_mini(body, max_items=12))
    rd = read_file_text(base / "readme.md", max_bytes=2048)
    if rd and rd.strip():
        about_parts.append(render_markdown_mini(strip_frontmatter(rd), max_items=12))

    context_items = []
    more = 0
    cdir = base / "context"
    if cdir.is_dir():
        try:
            entries = list(cdir.iterdir())
        except OSError:
            entries = []
        files = [
            f for f in sorted(entries)
            if f.is_file() and f.suffix == ".md" and f.name != "agent.md"
        ]
        files.sort(key=lambda f: 0 if f.name == "readme.md" else 1)
        subdirs = [f for f in entries if f.is_dir()]
        for f in files[:8]:
            text = strip_frontmatter(read_file_text(f, max_bytes=1600))
            if not text.strip():
                continue
            context_items.append({
                "title": ("About this folder" if f.name == "readme.md"
                          else deslug(f.name)),
                "html": render_markdown_mini(text, max_items=12),
            })
        more = max(0, len(files) - 8) + len(subdirs)
    return "\n".join(about_parts), context_items, more


def build_dashboard_data(root, registry_data, unregistered, scopes_flat):
    """The JSON payload the client-side graph views and sidebar render from."""
    scopes = []
    for s in scopes_flat:
        about_html, context_items, context_more = collect_scope_docs(root, s)
        scopes.append({
            "name": s.get("name", ""),
            "path": s.get("path", ""),
            "type": s.get("type", "scope"),
            "parent": s.get("parent"),
            "version": s.get("exfu_version"),
            "purpose": s.get("purpose", ""),
            "folderTypes": s.get("folder_types", {}),
            "group": grouping_label(s),
            "children": [c.get("name", "") for c in s.get("children", [])],
            "aboutHtml": about_html,
            "context": context_items,
            "contextMore": context_more,
        })
    agents = []
    if registry_data:
        for a in registry_data.get("agents", []):
            agents.append({
                "name": a.get("name", ""),
                "kind": a.get("kind", "librarian"),
                "cadence": a.get("cadence", ""),
                "description": a.get("description", ""),
                "scope": a.get("scope_name", ""),
                "origin": a.get("origin", "user"),
                "status": health_status(a),
                "lastRun": a.get("last_run"),
                "registered": True,
            })
    for u in unregistered or []:
        agents.append({
            "name": u.get("name", ""),
            "kind": u.get("kind", "librarian"),
            "cadence": u.get("cadence", ""),
            "description": u.get("description", ""),
            "scope": u.get("scope", ""),
            "origin": "user",
            "status": "unregistered",
            "lastRun": None,
            "registered": False,
        })
    return {"scopes": scopes, "agents": agents, "root": str(root)}


def render_view_bar(pane_prefix, filters_html):
    """List/Map toggle plus graph-only filter checkboxes."""
    return (
        '<div class="view-bar">'
        '<div class="view-toggle">'
        f'<button class="active" data-view="{pane_prefix}-list">List</button>'
        f'<button data-view="{pane_prefix}-graph">Map</button>'
        "</div>"
        f'<div class="graph-filters" data-pane="{pane_prefix}-graph" style="display:none">'
        f"{filters_html}"
        "</div>"
        "</div>"
    )


def enrich_scopes_with_purpose(root, scopes):
    """
    Walk the scope tree and add 'purpose' from scope.md if not present.
    Modifies scopes in place.
    """
    for scope in scopes:
        if "purpose" not in scope or not scope["purpose"]:
            rel_path = scope.get("path", "")
            scope_md = root / rel_path / "scope.md"
            if scope_md.exists():
                text = read_file_text(scope_md)
                fields = parse_yaml_frontmatter(text)
                scope["purpose"] = fields.get("purpose", "")
        for child in scope.get("children", []):
            enrich_scopes_with_purpose(root, [child])


def generate_dashboard(root):
    """Generate the complete dashboard HTML."""
    root = Path(root).resolve()
    derived_dir = root / "exfu" / "derived"

    # Load data
    index_data = load_json(derived_dir / "index.json")
    registry_data = load_json(derived_dir / "agent-registry.json")
    if registry_data is None:
        # Pre-rename substrate: librarian-registry.json with a "librarians" key
        registry_data = load_json(derived_dir / "librarian-registry.json")
        if registry_data and "agents" not in registry_data:
            registry_data["agents"] = registry_data.get("librarians", [])
    log_data = load_json(derived_dir / "agent-log.json")
    if log_data is None:
        log_data = load_json(derived_dir / "librarian-log.json")

    # Enrich scopes with purpose text from scope.md
    if index_data and index_data.get("scopes"):
        enrich_scopes_with_purpose(root, index_data["scopes"])

    # Figure out generated timestamp
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    index_ts = ""
    if index_data:
        index_ts = format_timestamp(index_data.get("generated", ""))

    # Render views
    substrate_map_html = render_substrate_map(index_data)
    unregistered = find_unregistered_definitions(root, index_data, registry_data)
    scopes_flat = flatten_scopes(index_data)
    enrich_agents(registry_data, unregistered, scopes_flat)
    librarian_html = render_librarian_dashboard(registry_data, log_data, unregistered)
    workspace_html = render_workspace_views(root, index_data)

    # Client-side payload for the graph views and sidebar
    data_json = json.dumps(
        build_dashboard_data(root, registry_data, unregistered, scopes_flat)
    ).replace("</", "<\\/")

    scope_filters = (
        '<label><input type="checkbox" id="f-groups" checked> grouping folders</label>'
        '<label><input type="checkbox" id="f-agents"> agents</label>'
    )
    agent_filters = (
        '<label><input type="checkbox" id="f-lib" checked> librarians</label>'
        '<label><input type="checkbox" id="f-biz" checked> business agents</label>'
        '<label><input type="checkbox" id="f-exfu"> ExFu agents</label>'
    )

    # Assemble page
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ExFu Dashboard</title>
  <style>{render_css()}</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>ExFu Dashboard</h1>
      <div class="subtitle">Substrate snapshot -- generated {esc(now)}</div>
    </header>

    <div class="tabs">
      <button class="tab active" data-tab="tab-map">Your scopes</button>
      <button class="tab" data-tab="tab-librarians">Agents</button>
      <button class="tab" data-tab="tab-workspace">Workspace</button>
    </div>

    <div id="tab-map" class="tab-panel active">
      {render_view_bar("scopes", scope_filters)}
      <div data-pane="scopes-list">
      {substrate_map_html}
      </div>
      <div data-pane="scopes-graph" style="display:none">
        <div id="scope-graph" class="graph-mount"></div>
        <div class="guidance">Click any node to see what lives there. You sit in the middle; every scope radiates out from you.</div>
      </div>
    </div>

    <div id="tab-librarians" class="tab-panel">
      {render_view_bar("agents", agent_filters)}
      <div data-pane="agents-list">
      {librarian_html}
      </div>
      <div data-pane="agents-graph" style="display:none">
        <div id="agents-graph" class="graph-mount"></div>
        <div class="guidance">Each agent hangs off the scope it works for. Click one for its story.</div>
      </div>
    </div>

    <div id="tab-workspace" class="tab-panel">
      {workspace_html}
    </div>

    <footer>
      Generated by the ExFu dashboard librarian{' -- index from ' + esc(index_ts) if index_ts else ''}
    </footer>
  </div>

  <div id="side-panel" hidden>
    <button class="panel-close" aria-label="Close">&times;</button>
    <div class="panel-body"></div>
  </div>

  <script>window.EXFU_DATA = {data_json};</script>
  <script>{render_tab_js()}</script>
  <script>{render_graph_js()}</script>
</body>
</html>"""

    return page


def main():
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    start = time.monotonic()

    html_content = generate_dashboard(root)

    # Write output into the visualisations gallery
    output_dir = root / "exfu" / "visualisations" / "dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(html_content, encoding="utf-8")

    elapsed = time.monotonic() - start
    size_kb = len(html_content) / 1024

    print(
        f"Dashboard generated at exfu/visualisations/dashboard/index.html "
        f"({size_kb:.1f} KB, took {elapsed:.2f}s)"
    )


if __name__ == "__main__":
    main()
