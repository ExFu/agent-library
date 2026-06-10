#!/usr/bin/env python3
"""
Dashboard Generator (v0.3.0)

Reads the substrate index, librarian registry, and librarian log, plus
workspace content from individual scopes, and generates a self-contained
HTML dashboard at exfu/derived/dashboard/index.html.

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
                                content_lines.append({
                                    "filename": f.name,
                                    "text": text.strip(),
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


def render_scope_card(scope, is_user=False):
    """Render a scope card as HTML."""
    name = esc(scope.get("name", "Unknown"))
    purpose = esc(scope.get("purpose", ""))
    exfu_ver = scope.get("exfu_version")
    folder_types = scope.get("folder_types", {})

    card_class = "card user-scope" if is_user else "card"

    parts = [f'<div class="{card_class}">']
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

    # Version summary
    parts = []
    if versions:
        ver_items = []
        for ver_name, ver_info in sorted(versions.items()):
            label = esc(ver_name)
            count = len(ver_info.get("scopes_using", []))
            is_latest = ver_info.get("is_latest", False)
            suffix = " (latest)" if is_latest else ""
            ver_items.append(f"{label}{suffix} -- {count} scope(s)")
        parts.append(
            '<div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:1rem;">'
            f'ExFu versions: {", ".join(ver_items)}'
            "</div>"
        )

    # Render scope cards
    for scope in scopes:
        is_user = scope.get("type") == "user"
        purpose = scope.get("purpose", "")
        # Try to get purpose from scope.md frontmatter if not in index
        parts.append(render_scope_card(scope, is_user=is_user))

    return "\n".join(parts)


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

    parts = ['<div class="card">']
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
    parts.append(f'<span class="lib-meta-item"><strong>Kind:</strong> {kind}</span>')
    if consecutive > 0:
        parts.append(
            f'<span class="lib-meta-item" style="color:var(--red)">'
            f"<strong>Failures:</strong> {consecutive} consecutive</span>"
        )
    parts.append("</div>")  # lib-meta
    parts.append("</div>")  # lib-info

    # Status badge
    parts.append('<div class="lib-status">')
    parts.append(f'<span class="lib-status-label {status_class}">{status_label}</span>')
    if last_run:
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


def render_librarian_dashboard(registry_data, log_data):
    """Render the librarian dashboard view."""
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

    # Group librarians by cadence
    by_cadence = {}
    for lib in librarians:
        cad = lib.get("cadence", "other")
        by_cadence.setdefault(cad, []).append(lib)

    for cadence_name in sorted(by_cadence.keys()):
        cadence_libs = by_cadence[cadence_name]
        cadence_info = cadences.get(cadence_name, {})
        last_run = cadence_info.get("last_run")

        parts.append('<div class="cadence-section">')
        parts.append(
            f'<div class="cadence-header">{esc(cadence_name)}'
        )
        if last_run:
            parts.append(
                f'<span class="cadence-meta">Last run: {time_ago(last_run)}</span>'
            )
        parts.append("</div>")

        for lib in cadence_libs:
            parts.append(render_librarian_card(lib))

        parts.append("</div>")

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


def render_workspace_folder(items, folder_label):
    """Render a workspace folder section (todo, reminders, or inbox)."""
    if not items:
        return (
            f'<div class="workspace-section">'
            f"<h3>{esc(folder_label)}</h3>"
            f'<div class="workspace-empty">No {esc(folder_label.lower())} found across scopes.</div>'
            f"</div>"
        )

    parts = [f'<div class="workspace-section">', f"<h3>{esc(folder_label)}</h3>"]

    for item in items:
        scope_name = esc(item["scope_name"])
        pointer = item.get("pointer_target")
        content_files = item.get("content_files", [])
        agent_tasks = item.get("agent_tasks", [])

        parts.append('<div class="workspace-scope">')
        parts.append(f'<div class="workspace-scope-name">{scope_name}</div>')

        if pointer:
            parts.append(f'<div class="workspace-pointer">{esc(pointer)}</div>')
        elif content_files:
            for cf in content_files:
                text = esc(cf["text"])
                parts.append(f'<div class="workspace-content">{text}</div>')
        elif agent_tasks:
            parts.append('<div class="workspace-content">')
            parts.append("\n".join(esc(t) for t in agent_tasks))
            parts.append("</div>")
        else:
            parts.append(f'<div class="workspace-empty">Empty</div>')

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

    parts = []
    parts.append(render_workspace_folder(todo_items, "Todo"))
    parts.append(render_workspace_folder(reminder_items, "Reminders"))
    parts.append(render_workspace_folder(inbox_items, "Inbox"))

    return "\n".join(parts)


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
    log_data = load_json(derived_dir / "agent-log.json")

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
    librarian_html = render_librarian_dashboard(registry_data, log_data)
    workspace_html = render_workspace_views(root, index_data)

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
      <button class="tab active" data-tab="tab-map">Substrate Map</button>
      <button class="tab" data-tab="tab-librarians">Scheduled agents</button>
      <button class="tab" data-tab="tab-workspace">Workspace</button>
    </div>

    <div id="tab-map" class="tab-panel active">
      {substrate_map_html}
    </div>

    <div id="tab-librarians" class="tab-panel">
      {librarian_html}
    </div>

    <div id="tab-workspace" class="tab-panel">
      {workspace_html}
    </div>

    <footer>
      Generated by the ExFu dashboard librarian{' -- index from ' + esc(index_ts) if index_ts else ''}
    </footer>
  </div>

  <script>{render_tab_js()}</script>
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

    # Write output
    output_dir = root / "exfu" / "derived" / "dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(html_content, encoding="utf-8")

    elapsed = time.monotonic() - start
    size_kb = len(html_content) / 1024

    print(
        f"Dashboard generated at exfu/derived/dashboard/index.html "
        f"({size_kb:.1f} KB, took {elapsed:.2f}s)"
    )


if __name__ == "__main__":
    main()
