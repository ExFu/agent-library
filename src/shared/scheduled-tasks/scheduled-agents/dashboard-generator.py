#!/usr/bin/env python3
"""
Dashboard Generator (v0.3.4)

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
    rows = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line.startswith("<!--") or line == "---":
            continue
        if line.startswith("#"):
            label = line.lstrip("#").strip()
            if label:
                rows.append(("h", f'<div class="ws-heading">{inline_md(label)}</div>'))
            continue
        m = CHECKBOX_RE.match(line)
        if m:
            done = m.group(1).lower() == "x"
            cls = "ws-task ws-done" if done else "ws-task"
            mark = "&#10003;" if done else ""
            rows.append((
                "i",
                f'<div class="{cls}"><span class="ws-box">{mark}</span>'
                f"<span>{inline_md(m.group(2))}</span></div>",
            ))
            continue
        if line.startswith(("- ", "* ")):
            rows.append(("i", f'<div class="ws-bullet">{inline_md(line[2:].strip())}</div>'))
            continue
        rows.append(("i", f'<div class="ws-line">{inline_md(line.lstrip(">").strip())}</div>'))

    # Nothing is ever hidden for good: overflow folds into an expander.
    out, extra, shown = [], [], 0
    for kind, row in rows:
        if not extra and (kind == "h" or shown < max_items):
            out.append(row)
            if kind == "i":
                shown += 1
        else:
            extra.append(row)
    if extra:
        plural = "" if len(extra) == 1 else "s"
        out.append(
            f'<details class="ws-more"><summary>and {len(extra)} more line{plural}</summary>'
            + "".join(extra) + "</details>"
        )
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


def _font_face_css():
    """
    Embed the brand display font (Source Serif 4 variable) as a data URI so
    the dashboard stays a single self-contained file with no network fetches.
    The woff2 ships with the plugin next to this script; if it's missing the
    page falls back to Georgia and nothing breaks.
    """
    import base64
    font_path = Path(__file__).resolve().parent / "fonts" / "source-serif-4-variable.woff2"
    try:
        encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return (
        "@font-face {\n"
        "  font-family: 'Source Serif 4';\n"
        "  font-style: normal;\n"
        "  font-weight: 200 900;\n"
        "  font-display: swap;\n"
        f"  src: url(data:font/woff2;base64,{encoded}) format('woff2');\n"
        "}\n"
    )


# A whisper of paper grain, inlined so nothing is fetched.
_GRAIN = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/>"
    "<feColorMatrix type='saturate' values='0'/></filter>"
    "<rect width='160' height='160' filter='url(%23n)' opacity='0.35'/></svg>"
)


def render_css():
    """The dashboard's design system: the website's Grounded Editorial,
    translated to a working surface. Paper, ink, rust; serif display over a
    humanist text stack; restraint over chrome."""
    return _font_face_css() + """
    :root {
      --paper: #F7F5F2;
      --paper-deep: #F0EBE4;
      --card: #FFFFFF;
      --ink: #161513;
      --ink-soft: #45403A;
      --muted: #8A847C;
      --faint: #B3ACA2;
      --line: #E5DFD6;
      --line-soft: #EFEAE3;
      --rust: #BA432F;
      --rust-deep: #A33A28;
      --rust-soft: #F5E4DF;
      --green: #5A7A4C;
      --green-soft: #E9EFE3;
      --amber: #C08A3E;
      --amber-soft: #F6ECDB;
      --red: #B04A3A;
      --red-soft: #F7E7E3;
      --blue: #5B7B9A;
      --blue-soft: #E8EEF4;
      --grey: #B8B1A6;
      --serif: 'Source Serif 4', Georgia, 'Times New Roman', serif;
      --sans: 'Avenir Next', 'Seravek', -apple-system, 'Segoe UI', system-ui, sans-serif;
      --mono: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
      --shadow-1: 0 1px 2px rgba(22, 21, 19, 0.05);
      --shadow-2: 0 6px 18px -8px rgba(22, 21, 19, 0.18);
      --ease: cubic-bezier(0.16, 1, 0.3, 1);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: var(--sans);
      background: var(--paper);
      color: var(--ink);
      line-height: 1.55;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      background-image: url("GRAIN_URL");
      opacity: 0.05;
      pointer-events: none;
      z-index: 1;
    }
    .container { position: relative; z-index: 2; max-width: 1140px; margin: 0 auto; padding: 3rem 1.6rem 4rem; }

    /* Header: editorial, left-aligned, serif-led */
    header { margin-bottom: 2.2rem; }
    header .eyebrow {
      font-size: 0.68rem;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--rust);
      margin-bottom: 0.5rem;
    }
    header h1 {
      font-family: var(--serif);
      font-size: clamp(1.9rem, 4vw, 2.6rem);
      font-weight: 600;
      letter-spacing: -0.015em;
      line-height: 1.1;
    }
    header .subtitle { color: var(--muted); font-size: 0.88rem; margin-top: 0.55rem; }

    /* Tabs: quiet uppercase nav with a rust underline */
    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      border-bottom: 1px solid var(--line);
      margin-bottom: 1.6rem;
    }
    .tab {
      appearance: none;
      border: none;
      background: none;
      font-family: var(--sans);
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--muted);
      padding: 0.6rem 0.9rem;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      cursor: pointer;
      transition: color 0.18s var(--ease);
    }
    .tab:hover { color: var(--ink); }
    .tab.active { color: var(--rust); border-bottom-color: var(--rust); }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; animation: rise 0.5s var(--ease) both; }

    @keyframes rise {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: none; }
    }
    @media (prefers-reduced-motion: reduce) {
      .tab-panel.active, .card { animation: none !important; }
    }

    /* Cards */
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 1rem 1.1rem;
      box-shadow: var(--shadow-1);
      transition: transform 0.25s var(--ease), box-shadow 0.25s var(--ease), border-color 0.25s var(--ease);
      animation: rise 0.5s var(--ease) both;
    }
    .scope-grid .card:nth-child(2) { animation-delay: 0.03s; }
    .scope-grid .card:nth-child(3) { animation-delay: 0.06s; }
    .scope-grid .card:nth-child(4) { animation-delay: 0.09s; }
    .scope-grid .card:nth-child(5) { animation-delay: 0.12s; }
    .scope-grid .card:nth-child(6) { animation-delay: 0.15s; }
    .scope-grid .card:nth-child(n+7) { animation-delay: 0.18s; }

    /* Scope cards live in a grid; the personal scope is the hero */
    .scope-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(265px, 1fr));
      gap: 0.85rem;
      align-items: start;
    }
    .card[data-scope] { cursor: pointer; }
    .card[data-scope]:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-2);
      border-color: #D9D2C7;
    }
    .user-scope {
      grid-column: 1 / -1;
      background: linear-gradient(135deg, #F4EEE6 0%, #F7F3ED 100%);
      border-left: 3px solid var(--rust);
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.4rem 1.2rem;
    }
    .user-scope .card-header { margin-bottom: 0; }
    .user-scope .card-name { font-size: 1.35rem; }
    .user-scope .card-purpose { margin: 0; flex: 1 1 16rem; }
    .card-header { display: flex; align-items: baseline; justify-content: space-between; gap: 0.6rem; margin-bottom: 0.15rem; }
    .card-name {
      font-family: var(--serif);
      font-size: 1.08rem;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .card-badge {
      font-size: 0.66rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      background: var(--paper-deep);
      padding: 0.18rem 0.55rem;
      border-radius: 999px;
      white-space: nowrap;
    }
    .card-purpose {
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.45;
      margin: 0.15rem 0 0.55rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .folder-dots { display: flex; flex-wrap: wrap; gap: 0.25rem 0.7rem; margin-top: 0.45rem; }
    .folder-dot { display: inline-flex; align-items: center; gap: 0.32rem; font-size: 0.72rem; color: var(--muted); }
    .folder-dot .dot, .legend-item .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex: none; }
    .scope-children { grid-column: 1 / -1; border-left: 2px solid var(--line); margin: -0.2rem 0 0 1rem; padding-left: 0.9rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 0.85rem; }

    /* Grouping folders: a labelled field the grid flows through */
    .group-box {
      grid-column: 1 / -1;
      border: 1px dashed #D9D2C7;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.4);
      padding: 0.85rem 0.9rem 0.9rem;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(255px, 1fr));
      gap: 0.85rem;
    }
    .group-label {
      grid-column: 1 / -1;
      font-family: var(--serif);
      font-style: italic;
      font-size: 0.85rem;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }
    .group-label::after { content: ""; flex: 1; height: 1px; background: var(--line-soft); }

    /* View bar */
    .view-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.7rem; margin-bottom: 1.1rem; }
    .view-toggle { display: inline-flex; background: var(--paper-deep); border-radius: 999px; padding: 3px; }
    .view-toggle button {
      appearance: none;
      border: none;
      background: none;
      font-family: var(--sans);
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      color: var(--muted);
      padding: 0.34rem 1rem;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.2s var(--ease);
    }
    .view-toggle button.active { background: var(--rust); color: #FCF9F6; box-shadow: var(--shadow-1); }
    .graph-filters { display: inline-flex; flex-wrap: wrap; gap: 0.9rem; font-size: 0.78rem; color: var(--muted); }
    .graph-filters label { display: inline-flex; align-items: center; gap: 0.35rem; cursor: pointer; }
    .graph-filters input { accent-color: var(--rust); }

    /* Map */
    .map-meta { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.5rem; font-size: 0.8rem; color: var(--muted); margin-bottom: 1rem; }
    .map-legend { display: inline-flex; gap: 1rem; }
    .legend-item { display: inline-flex; align-items: center; gap: 0.35rem; }
    .graph-mount { border: 1px solid var(--line); border-radius: 12px; background:
      radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.85), rgba(255,255,255,0) 70%), var(--paper-deep); }
    .graph-mount svg { width: 100%; height: auto; display: block; }
    .gnode { cursor: pointer; }
    .gnode circle { transition: stroke 0.15s var(--ease); }
    .gnode:hover > circle { stroke: var(--rust); stroke-width: 2; }
    .gnode text { font-family: var(--sans); }
    .gedge { transition: opacity 0.2s; }

    /* Agents */
    .cadence-section { margin-bottom: 1.4rem; }
    .cadence-header {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--faint);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid var(--line-soft);
      margin-bottom: 0.7rem;
    }
    .cadence-meta { font-weight: 500; letter-spacing: 0.02em; text-transform: none; font-size: 0.78rem; }
    .lib-card { display: flex; gap: 0.85rem; align-items: flex-start; }
    .lib-health-dot { width: 9px; height: 9px; border-radius: 50%; margin-top: 0.45rem; flex: none; }
    .lib-info { flex: 1; min-width: 0; }
    .lib-name { font-family: var(--serif); font-weight: 600; font-size: 1rem; }
    .lib-desc { color: var(--muted); font-size: 0.83rem; margin-top: 0.1rem; }
    .lib-meta { display: flex; flex-wrap: wrap; gap: 0.3rem 1.1rem; margin-top: 0.45rem; font-size: 0.76rem; color: var(--muted); }
    .lib-meta-item strong { font-weight: 600; color: var(--ink-soft); }
    .lib-status { text-align: right; flex: none; }
    .lib-status-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; padding: 0.22rem 0.65rem; border-radius: 999px; }
    .status-healthy { background: var(--green-soft); color: var(--green); }
    .status-warning { background: var(--amber-soft); color: var(--amber); }
    .status-failing { background: var(--red-soft); color: var(--red); }
    .status-unknown { background: var(--paper-deep); color: var(--muted); }
    .lib-last-run { color: var(--faint); font-size: 0.74rem; margin-top: 0.35rem; }
    .card-dim { opacity: 0.62; }
    .kind-badge { background: var(--amber-soft); color: var(--amber); font-size: 0.68rem; font-weight: 600; padding: 0.12rem 0.55rem; border-radius: 999px; }
    details.agent-group { margin-bottom: 0.9rem; }
    details.agent-group > summary {
      cursor: pointer;
      list-style: none;
      font-family: var(--serif);
      font-weight: 600;
      font-size: 1.02rem;
      padding: 0.45rem 0.1rem;
      display: flex;
      align-items: center;
    }
    details.agent-group > summary::-webkit-details-marker { display: none; }
    details.agent-group > summary::before {
      content: "\\25B8";
      font-family: var(--sans);
      display: inline-block;
      margin-right: 0.55rem;
      color: var(--faint);
      font-size: 0.8rem;
      transition: transform 0.18s var(--ease);
    }
    details.agent-group[open] > summary::before { transform: rotate(90deg); }
    details.agent-group .card { margin-bottom: 0.6rem; }
    .group-count {
      background: var(--paper-deep);
      color: var(--muted);
      font-family: var(--sans);
      font-size: 0.68rem;
      font-weight: 600;
      border-radius: 999px;
      padding: 0.08rem 0.55rem;
      margin-left: 0.55rem;
    }
    details.exfu-group > summary { color: var(--muted); font-style: italic; }
    details.exfu-group .card { opacity: 0.85; }

    .run-history { margin-top: 1.6rem; }
    .run-history h3 { font-family: var(--serif); font-size: 1.05rem; margin-bottom: 0.5rem; }
    .run-entry { display: flex; gap: 0.8rem; align-items: baseline; font-size: 0.8rem; padding: 0.42rem 0.1rem; border-bottom: 1px solid var(--line-soft); }
    .run-dot { width: 7px; height: 7px; border-radius: 50%; flex: none; transform: translateY(-1px); }
    .run-cadence { color: var(--faint); width: 4.2rem; flex: none; }
    .run-time { color: var(--muted); font-family: var(--mono); font-size: 0.72rem; width: 11rem; flex: none; }
    .run-results { color: var(--ink-soft); }

    /* Workspace views */
    .workspace-section { margin-bottom: 1.6rem; }
    .workspace-section h3 { font-family: var(--serif); font-size: 1.15rem; margin-bottom: 0.6rem; }
    .workspace-scope { margin: 0 0 1rem; padding: 0.9rem 1rem; background: var(--card); border: 1px solid var(--line); border-radius: 10px; box-shadow: var(--shadow-1); }
    .workspace-scope-name {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--rust);
      margin-bottom: 0.4rem;
    }
    .workspace-empty { color: var(--faint); font-style: italic; font-size: 0.85rem; }
    .chip {
      display: inline-block;
      background: var(--blue-soft);
      color: var(--blue);
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.16rem 0.6rem;
      border-radius: 999px;
      white-space: nowrap;
    }
    .chip-quiet { background: var(--paper-deep); color: var(--muted); font-weight: 500; margin-left: 0.5rem; }
    .ws-pointer-row { display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap; }
    .ws-pointer-detail { color: var(--muted); font-size: 0.83rem; }
    .ws-heading {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--faint);
      margin: 0.7rem 0 0.3rem;
    }
    .ws-task { display: flex; gap: 0.55rem; align-items: baseline; padding: 0.18rem 0; font-size: 0.88rem; }
    .ws-box {
      width: 1rem; height: 1rem; flex: none;
      border: 1.5px solid var(--line);
      border-radius: 5px;
      font-size: 0.68rem; line-height: 0.95rem; text-align: center;
      color: var(--green);
      background: var(--card);
    }
    .ws-done { color: var(--faint); }
    .ws-done .ws-box { background: var(--green-soft); border-color: var(--green-soft); }
    .ws-done span:last-child { text-decoration: line-through; }
    .ws-bullet { padding: 0.14rem 0 0.14rem 1.05rem; position: relative; font-size: 0.88rem; }
    .ws-bullet::before { content: "\\2022"; position: absolute; left: 0.3rem; color: var(--rust); opacity: 0.5; }
    .ws-line { padding: 0.14rem 0; font-size: 0.88rem; }
    .ws-filename { font-family: var(--serif); font-weight: 600; font-size: 0.92rem; margin-top: 0.7rem; }
    .ws-body { margin-bottom: 0.4rem; }
    details.ws-more {
      margin: 0.3rem 0;
    }
    details.ws-more > summary {
      cursor: pointer;
      list-style: none;
      color: var(--rust);
      font-size: 0.78rem;
      font-weight: 600;
    }
    details.ws-more > summary::-webkit-details-marker { display: none; }
    details.ws-more > summary:hover { color: var(--rust-deep); text-decoration: underline; }
    .inbox-card { border: 1px solid var(--line-soft); border-radius: 8px; padding: 0.55rem 0.8rem; margin: 0.45rem 0; background: var(--card); }
    .inbox-title { font-family: var(--serif); font-weight: 600; font-size: 0.92rem; }
    .inbox-snippet { color: var(--muted); font-size: 0.83rem; margin-top: 0.12rem; }
    .inbox-age { color: var(--faint); font-size: 0.72rem; margin-top: 0.25rem; }

    /* Guidance + hints */
    .guidance {
      color: var(--ink-soft);
      font-size: 0.84rem;
      background: var(--paper-deep);
      border-left: 3px solid var(--rust);
      border-radius: 0 8px 8px 0;
      padding: 0.65rem 0.95rem;
      margin: 1.2rem 0 0.5rem;
    }
    .hint {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      position: relative;
      width: 1.02rem;
      height: 1.02rem;
      font-size: 0.66rem;
      font-weight: 700;
      font-family: var(--sans);
      font-style: normal;
      color: var(--muted);
      border: 1px solid var(--line);
      border-radius: 50%;
      margin-left: 0.45rem;
      cursor: help;
      vertical-align: middle;
      transition: all 0.15s var(--ease);
    }
    .hint:hover, .hint:focus { color: var(--rust); border-color: var(--rust); outline: none; }
    .hint-pop {
      display: none;
      position: absolute;
      bottom: 1.6rem;
      left: 50%;
      transform: translateX(-50%);
      width: 250px;
      background: var(--ink);
      color: #F4F1EC;
      font-size: 0.76rem;
      font-weight: 400;
      letter-spacing: normal;
      line-height: 1.45;
      text-align: left;
      text-transform: none;
      padding: 0.6rem 0.75rem;
      border-radius: 8px;
      box-shadow: var(--shadow-2);
      z-index: 60;
    }
    .hint:hover .hint-pop, .hint:focus .hint-pop { display: block; }

    /* Empty states */
    .empty-state { text-align: center; padding: 2.6rem 1rem; color: var(--muted); }
    .empty-state h3 { font-family: var(--serif); font-size: 1.2rem; color: var(--ink-soft); margin-bottom: 0.4rem; }
    .empty-state p { font-size: 0.86rem; max-width: 30rem; margin: 0 auto; }

    /* Embedded scope views */
    .viz-frame { width: 100%; height: 74vh; border: 1px solid var(--line); border-radius: 12px; background: var(--card); }
    .viz-byline { font-size: 0.78rem; color: var(--muted); margin-bottom: 0.6rem; }

    /* Split-pane shell: the substrate on the left, the always-open
       reading panel on the right (default half the window, drag to taste) */
    .shell { display: flex; height: 100vh; }
    .main { flex: 1 1 auto; min-width: 0; overflow-y: auto; }
    body.resizing { cursor: col-resize; user-select: none; }
    #side-panel {
      position: relative;
      flex: 0 0 auto;
      width: clamp(320px, var(--panel-w, 50vw), 75vw);
      height: 100vh;
      background: var(--card);
      border-left: 1px solid var(--line);
      box-shadow: -14px 0 36px rgba(22, 21, 19, 0.07);
      overflow: hidden;
      z-index: 5;
    }
    #side-panel .panel-body {
      height: 100%;
      overflow-y: auto;
      padding: 1.5rem 1.6rem 2.4rem;
    }
    #panel-grip {
      position: absolute;
      top: 0;
      left: 0;
      width: 9px;
      height: 100%;
      cursor: col-resize;
      z-index: 6;
    }
    #panel-grip:hover, #panel-grip.dragging { background: linear-gradient(90deg, var(--rust-soft), transparent); }
    #side-panel h3 { font-family: var(--serif); font-size: 1.3rem; font-weight: 600; letter-spacing: -0.01em; margin: 0.2rem 0 0.15rem; }
    #side-panel p { font-size: 0.86rem; color: var(--muted); margin: 0.35rem 0; }
    .panel-tag { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--rust); }
    .panel-section {
      font-size: 0.66rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--faint);
      margin: 1.05rem 0 0.3rem;
    }
    .panel-mono { font-family: var(--mono); font-size: 0.76rem; color: var(--muted); }
    .panel-muted { color: var(--faint); font-size: 0.78rem; }
    .panel-prose { font-size: 0.84rem; color: var(--ink-soft); }
    .panel-prose .ws-heading { margin-top: 0.5rem; }
    details.panel-doc {
      border: 1px solid var(--line-soft);
      border-radius: 8px;
      padding: 0.4rem 0.65rem;
      margin: 0.32rem 0;
      background: var(--card);
    }
    details.panel-doc > summary {
      cursor: pointer;
      list-style: none;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--ink-soft);
    }
    details.panel-doc > summary::-webkit-details-marker { display: none; }
    details.panel-doc > summary::before {
      content: "\\25B8";
      display: inline-block;
      margin-right: 0.45rem;
      color: var(--faint);
      transition: transform 0.15s var(--ease);
    }
    details.panel-doc[open] > summary::before { transform: rotate(90deg); }
    details.panel-doc[open] > summary { margin-bottom: 0.3rem; }
    .path-link { color: var(--blue); text-decoration: none; border-bottom: 1px dotted var(--blue); }
    .path-link:hover { color: var(--rust); border-bottom-color: var(--rust); }
    .copy-btn {
      border: 1px solid var(--line);
      background: var(--card);
      color: var(--muted);
      font-family: var(--sans);
      font-size: 0.66rem;
      font-weight: 600;
      border-radius: 999px;
      padding: 0.08rem 0.55rem;
      margin-left: 0.45rem;
      cursor: pointer;
      vertical-align: middle;
      transition: all 0.15s var(--ease);
    }
    .copy-btn:hover { color: var(--rust); border-color: var(--rust); }
    .panel-guidance {
      margin-top: 1.3rem;
      font-size: 0.8rem;
      color: var(--ink-soft);
      background: var(--paper-deep);
      border-left: 3px solid var(--rust);
      border-radius: 0 8px 8px 0;
      padding: 0.55rem 0.75rem;
    }
    /* Workspace item cards: one card per task, reminder, capture */
    .item-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 0.7rem;
    }
    .item-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.7rem 0.85rem;
      box-shadow: var(--shadow-1);
      cursor: pointer;
      transition: transform 0.2s var(--ease), box-shadow 0.2s var(--ease), border-color 0.2s var(--ease);
      animation: rise 0.45s var(--ease) both;
    }
    .item-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-2); border-color: #D9D2C7; }
    .item-scope {
      font-size: 0.62rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--rust);
      margin-bottom: 0.3rem;
    }
    .item-title {
      font-family: var(--serif);
      font-weight: 600;
      font-size: 0.93rem;
      line-height: 1.35;
      display: flex;
      gap: 0.45rem;
      align-items: baseline;
    }
    .item-title .ws-box { transform: translateY(2px); }
    .item-done .item-title { color: var(--faint); text-decoration: line-through; }
    .item-meta {
      color: var(--muted);
      font-size: 0.78rem;
      margin-top: 0.3rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .panel-row[data-agent] { cursor: pointer; }
    .panel-row[data-agent]:hover { color: var(--rust); }

    /* Graph: second-brain conventions -- dim the world, light the neighbourhood */
    .graph-mount { touch-action: none; }
    .graph-mount svg { cursor: grab; }
    .gnode circle, .gnode text, .gedge { transition: opacity 0.18s var(--ease); }
    .gnode.g-dim { opacity: 0.13; }
    .gedge.g-dim { opacity: 0.08; }
    .gedge.g-hot { stroke: var(--rust); opacity: 0.85; }
    .gnode.g-focus text, .gnode:hover text { fill: var(--ink); font-weight: 700; }

    footer {
      margin-top: 3rem;
      padding-top: 1.1rem;
      border-top: 1px solid var(--line);
      color: var(--faint);
      font-size: 0.76rem;
      text-align: center;
    }

    @media (max-width: 700px) {
      .container { padding: 2rem 1rem 3rem; }
      .scope-grid, .group-box, .scope-children { grid-template-columns: 1fr; }
      .lib-card { flex-wrap: wrap; }
      .lib-status { text-align: left; width: 100%; display: flex; gap: 0.7rem; align-items: baseline; }
      .shell { flex-direction: column; height: auto; }
      .main { overflow: visible; }
      #side-panel {
        width: auto;
        height: auto;
        max-height: 70vh;
        border-left: none;
        border-top: 1px solid var(--line);
      }
      #side-panel .panel-body { height: auto; max-height: 70vh; }
      .run-time { width: auto; }
    }
    """.replace("GRAIN_URL", _GRAIN)


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


def render_graph_js():
    """Client-side code: split-pane sidebar, second-brain style graphs,
    item/agent detail panels."""
    return """
(function () {
  var D = window.EXFU_DATA || { scopes: [], agents: [], workspace: {} };
  var SVGNS = 'http://www.w3.org/2000/svg';

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }
  function trunc(s, n) { return s.length > n ? s.slice(0, n - 1) + '...' : s; }

  var COL = {
    line: '#DCD5CA', ink: '#161513', inkSoft: '#45403A', muted: '#8A847C',
    faint: '#B3ACA2', rust: '#BA432F', rustSoft: '#F5E4DF', card: '#FFFFFF',
    paper: '#F0EBE4', green: '#5A7A4C', amber: '#C08A3E', red: '#B04A3A',
    grey: '#B8B1A6', blue: '#5B7B9A'
  };
  function healthColor(st) {
    if (st === 'healthy') return COL.green;
    if (st === 'warning') return COL.amber;
    if (st === 'failing') return COL.red;
    return COL.grey;
  }
  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function scopeByName(n) {
    for (var i = 0; i < D.scopes.length; i++) if (D.scopes[i].name === n) return D.scopes[i];
    return null;
  }
  function agentsForScope(name) {
    return D.agents.filter(function (a) { return a.scope === name && a.origin !== 'exfu'; });
  }

  /* ================= graph models ================= */

  function modelScopeGraph(showGroups, showAgents) {
    var nodes = [], edges = [], byId = {};
    var W = 960, H = 680, cx = W / 2, cy = H / 2;
    function add(n) { n.deg = 0; nodes.push(n); byId[n.id] = n; return n; }
    function link(a, b, rest) {
      edges.push({ a: a, b: b, rest: rest });
      if (byId[a]) byId[a].deg++;
      if (byId[b]) byId[b].deg++;
    }
    var user = null, tops = [], byName = {};
    D.scopes.forEach(function (s) {
      byName[s.name] = s;
      if (s.type === 'user') user = s;
      else if (s.parent === 'root') tops.push(s);
    });
    add({ id: 'u', x: cx, y: cy, stype: 'user', pinned: true,
          name: user ? user.name : 'You', data: user });
    var ring = [], seen = {};
    tops.forEach(function (s) {
      if (s.group && showGroups) {
        if (!seen[s.group]) {
          seen[s.group] = true;
          ring.push({ kind: 'group', label: s.group,
                      members: tops.filter(function (t) { return t.group === s.group; }) });
        }
      } else ring.push({ kind: 'scope', scope: s });
    });
    function scopeNode(s, x, y, parentId, depth) {
      var n = add({ id: 's:' + s.name, x: x, y: y, stype: 'scope', name: s.name, data: s });
      link(parentId, n.id, depth === 0 ? 150 : 95);
      (s.children || []).forEach(function (cn, i) {
        var c = byName[cn];
        if (c) scopeNode(c, x + 36 + i * 14, y + 70, n.id, depth + 1);
      });
      if (showAgents) {
        agentsForScope(s.name).forEach(function (a, i) {
          var an = add({ id: 'a:' + a.name, x: x + 26 + i * 10, y: y - 52, stype: 'agent',
                         name: a.name, data: a });
          link(n.id, an.id, 52);
        });
      }
    }
    var n = ring.length || 1;
    ring.forEach(function (e, i) {
      var ang = -Math.PI / 2 + (i / n) * Math.PI * 2;
      var x = cx + Math.cos(ang) * 150, y = cy + Math.sin(ang) * 150;
      if (e.kind === 'group') {
        add({ id: 'g:' + e.label, x: x, y: y, stype: 'group', name: e.label, data: e });
        link('u', 'g:' + e.label, 140);
        e.members.forEach(function (m, j) {
          var ma = ang + (j - (e.members.length - 1) / 2) * 0.4;
          scopeNode(m, cx + Math.cos(ma) * 255, cy + Math.sin(ma) * 255, 'g:' + e.label, 1);
        });
      } else scopeNode(e.scope, x, y, 'u', 0);
    });
    return finishModel(nodes, edges, byId, W, H);
  }

  function modelAgentsGraph(showLib, showBiz, showExfu) {
    var nodes = [], edges = [], byId = {};
    var W = 960, H = 620, cx = W / 2, cy = H / 2;
    function add(n) { n.deg = 0; nodes.push(n); byId[n.id] = n; return n; }
    function link(a, b, rest) {
      edges.push({ a: a, b: b, rest: rest });
      if (byId[a]) byId[a].deg++;
      if (byId[b]) byId[b].deg++;
    }
    add({ id: 'u', x: cx, y: cy, stype: 'user', pinned: true, name: 'You', data: null });
    var hubs = {};
    D.agents.forEach(function (a) {
      if (a.origin === 'exfu') { if (!showExfu) return; }
      else if (a.kind === 'librarian' && !showLib) return;
      else if (a.kind === 'agent' && !showBiz) return;
      var hub = a.origin === 'exfu' ? 'ExFu' : (a.scope || 'Your substrate');
      (hubs[hub] = hubs[hub] || []).push(a);
    });
    var names = Object.keys(hubs), n = names.length || 1;
    names.forEach(function (h, i) {
      var ang = -Math.PI / 2 + (i / n) * Math.PI * 2;
      var hub = scopeByName(h);
      add({ id: 'h:' + h, x: cx + Math.cos(ang) * 150, y: cy + Math.sin(ang) * 150,
            stype: hub ? 'scope' : 'group', name: h, data: hub || { label: h } });
      link('u', 'h:' + h, 150);
      hubs[h].forEach(function (a, j) {
        var aa = ang + (j - (hubs[h].length - 1) / 2) * 0.32;
        add({ id: 'a:' + a.name, x: cx + Math.cos(aa) * 245, y: cy + Math.sin(aa) * 245,
              stype: 'agent', name: a.name, data: a });
        link('h:' + h, 'a:' + a.name, 85);
      });
    });
    return finishModel(nodes, edges, byId, W, H);
  }

  function finishModel(nodes, edges, byId, W, H) {
    // node radius by type and degree -- the second-brain convention:
    // small dots, the better-connected slightly larger
    nodes.forEach(function (nd) {
      if (nd.stype === 'user') nd.r = 15;
      else if (nd.stype === 'agent') nd.r = 4.5;
      else if (nd.stype === 'group') nd.r = 5;
      else nd.r = Math.min(13, 6 + nd.deg * 1.1);
    });
    // adjacency for neighbourhood highlighting
    var adj = {};
    edges.forEach(function (e) {
      (adj[e.a] = adj[e.a] || {})[e.b] = true;
      (adj[e.b] = adj[e.b] || {})[e.a] = true;
    });
    return { nodes: nodes, edges: edges, byId: byId, adj: adj, w: W, h: H,
             alpha: 1, tx: 0, ty: 0, scale: 1 };
  }

  /* ================= simulation ================= */

  function tick(model) {
    var nodes = model.nodes, edges = model.edges, byId = model.byId;
    var alpha = model.alpha, i, j;
    for (i = 0; i < nodes.length; i++) { nodes[i].fx = 0; nodes[i].fy = 0; }
    for (i = 0; i < nodes.length; i++) {
      for (j = i + 1; j < nodes.length; j++) {
        var a = nodes[i], b = nodes[j];
        var dx = b.x - a.x, dy = b.y - a.y;
        var d2 = dx * dx + dy * dy + 0.01;
        var d = Math.sqrt(d2);
        var f = 2100 / d2;
        var fx = (dx / d) * f, fy = (dy / d) * f;
        a.fx -= fx; a.fy -= fy; b.fx += fx; b.fy += fy;
      }
    }
    edges.forEach(function (e) {
      var a = byId[e.a], b = byId[e.b];
      if (!a || !b) return;
      var dx = b.x - a.x, dy = b.y - a.y;
      var d = Math.sqrt(dx * dx + dy * dy) || 1;
      var f = 0.05 * (d - e.rest);
      var fx = (dx / d) * f, fy = (dy / d) * f;
      a.fx += fx; a.fy += fy; b.fx -= fx; b.fy -= fy;
    });
    var cx = model.w / 2, cy = model.h / 2;
    nodes.forEach(function (nd) {
      if (nd.pinned || nd.dragging) return;
      nd.fx += (cx - nd.x) * 0.004;
      nd.fy += (cy - nd.y) * 0.004;
      nd.vx = ((nd.vx || 0) + nd.fx * alpha) * 0.85;
      nd.vy = ((nd.vy || 0) + nd.fy * alpha) * 0.85;
      nd.x += nd.vx; nd.y += nd.vy;
    });
    model.alpha = Math.max(0, model.alpha * 0.985);
  }

  function ensureRunning(model) {
    if (model._running) return;
    model._running = true;
    function loop() {
      tick(model);
      paint(model);
      var hot = model.alpha > 0.02 ||
        model.nodes.some(function (n) { return n.dragging; });
      if (hot) requestAnimationFrame(loop);
      else model._running = false;
    }
    requestAnimationFrame(loop);
  }
  function heat(model, amount) {
    model.alpha = Math.max(model.alpha, amount);
    if (reduceMotion) {
      for (var k = 0; k < 280 && model.alpha > 0.02; k++) tick(model);
      paint(model);
      return;
    }
    ensureRunning(model);
  }

  /* ================= rendering ================= */

  function paint(model) {
    if (model._zoomG) {
      model._zoomG.setAttribute('transform',
        'translate(' + model.tx + ' ' + model.ty + ') scale(' + model.scale + ')');
    }
    model.edges.forEach(function (e) {
      var a = model.byId[e.a], b = model.byId[e.b];
      if (!e.el || !a || !b) return;
      e.el.setAttribute('x1', a.x.toFixed(1));
      e.el.setAttribute('y1', a.y.toFixed(1));
      e.el.setAttribute('x2', b.x.toFixed(1));
      e.el.setAttribute('y2', b.y.toFixed(1));
    });
    model.nodes.forEach(function (nd) {
      if (!nd.el) return;
      nd.el.setAttribute('transform', 'translate(' + nd.x.toFixed(1) + ' ' + nd.y.toFixed(1) + ')');
    });
  }

  function setFocus(model, id) {
    var neigh = id ? (model.adj[id] || {}) : null;
    model.nodes.forEach(function (nd) {
      if (!nd.el) return;
      var on = !id || nd.id === id || (neigh && neigh[nd.id]);
      nd.el.classList.toggle('g-dim', !on);
      nd.el.classList.toggle('g-focus', !!id && nd.id === id);
    });
    model.edges.forEach(function (e) {
      if (!e.el) return;
      var on = !id || e.a === id || e.b === id;
      e.el.classList.toggle('g-dim', !on);
      e.el.classList.toggle('g-hot', !!id && on);
    });
  }

  function buildSvg(mount, model) {
    mount.innerHTML = '';
    var svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + model.w + ' ' + model.h);
    var zoomG = document.createElementNS(SVGNS, 'g');
    model._zoomG = zoomG;
    var edgeLayer = document.createElementNS(SVGNS, 'g');
    var nodeLayer = document.createElementNS(SVGNS, 'g');
    zoomG.appendChild(edgeLayer); zoomG.appendChild(nodeLayer);
    svg.appendChild(zoomG);
    model.edges.forEach(function (e) {
      var l = document.createElementNS(SVGNS, 'line');
      l.setAttribute('class', 'gedge');
      l.setAttribute('stroke', COL.line);
      l.setAttribute('stroke-width', '1');
      e.el = l;
      edgeLayer.appendChild(l);
    });
    model.nodes.forEach(function (nd) {
      var g = document.createElementNS(SVGNS, 'g');
      g.setAttribute('class', 'gnode');
      g.setAttribute('data-stype', nd.stype);
      g.setAttribute('data-name', nd.name);
      var fill = COL.inkSoft, stroke = 'none', dash = '';
      if (nd.stype === 'user') { fill = COL.rust; }
      if (nd.stype === 'group') { fill = COL.paper; stroke = COL.faint; dash = '2 2'; }
      if (nd.stype === 'agent') {
        fill = healthColor(nd.data && nd.data.status);
        if (nd.data && nd.data.status === 'unregistered') { fill = COL.card; stroke = COL.grey; dash = '2 2'; }
      }
      if (nd.stype === 'user') {
        var halo = document.createElementNS(SVGNS, 'circle');
        halo.setAttribute('r', nd.r + 9);
        halo.setAttribute('fill', COL.rust);
        halo.setAttribute('opacity', '0.12');
        g.appendChild(halo);
      }
      var c = document.createElementNS(SVGNS, 'circle');
      c.setAttribute('r', nd.r);
      c.setAttribute('fill', fill);
      if (stroke !== 'none') { c.setAttribute('stroke', stroke); c.setAttribute('stroke-width', '1.4'); }
      if (dash) c.setAttribute('stroke-dasharray', dash);
      var t = document.createElementNS(SVGNS, 'text');
      t.setAttribute('text-anchor', 'middle');
      t.setAttribute('y', nd.r + (nd.stype === 'agent' ? 11 : 14));
      t.setAttribute('font-size', nd.stype === 'user' ? '12.5' : '10.5');
      t.setAttribute('font-weight', nd.stype === 'user' ? '700' : '500');
      t.setAttribute('fill', COL.muted);
      t.textContent = trunc(nd.name, 20);
      nd.el = g;
      g.appendChild(c); g.appendChild(t);
      nodeLayer.appendChild(g);

      g.addEventListener('pointerenter', function () { setFocus(model, nd.id); });
      g.addEventListener('pointerleave', function () { setFocus(model, null); });
    });
    mount._svg = svg;
    mount._model = model;
    mount.appendChild(svg);
    wireGraphPointer(mount, model);
  }

  function wireGraphPointer(mount, model) {
    var svg = mount._svg;
    function toLocal(ev) {
      var pt = svg.createSVGPoint();
      pt.x = ev.clientX; pt.y = ev.clientY;
      var m = svg.getScreenCTM();
      if (!m) return null;
      var p = pt.matrixTransform(m.inverse());
      // undo the zoom/pan transform to model space
      return { x: (p.x - model.tx) / model.scale, y: (p.y - model.ty) / model.scale };
    }
    svg.addEventListener('wheel', function (ev) {
      ev.preventDefault();
      var p0 = toLocal(ev);
      if (!p0) return;
      var factor = ev.deltaY < 0 ? 1.12 : 0.89;
      var next = Math.max(0.45, Math.min(3.2, model.scale * factor));
      // keep the point under the cursor stationary
      model.tx += (p0.x * model.scale) - (p0.x * next);
      model.ty += (p0.y * model.scale) - (p0.y * next);
      model.scale = next;
      paint(model);
    }, { passive: false });

    svg.addEventListener('pointerdown', function (ev) {
      var g = ev.target.closest ? ev.target.closest('.gnode') : null;
      var startX = ev.clientX, startY = ev.clientY;
      var moved = false;
      svg.setPointerCapture(ev.pointerId);
      if (g) {
        var nd = null;
        model.nodes.forEach(function (n) { if (n.el === g) nd = n; });
        if (!nd) return;
        nd.dragging = true; nd.vx = 0; nd.vy = 0;
        function onMoveNode(e2) {
          var p = toLocal(e2);
          if (!p) return;
          if (Math.abs(e2.clientX - startX) + Math.abs(e2.clientY - startY) > 3) moved = true;
          nd.x = p.x; nd.y = p.y;
          heat(model, 0.5);
        }
        function onUpNode() {
          nd.dragging = false;
          heat(model, 0.3);
          svg.removeEventListener('pointermove', onMoveNode);
          svg.removeEventListener('pointerup', onUpNode);
          if (!moved) onNodeClick(g);
        }
        svg.addEventListener('pointermove', onMoveNode);
        svg.addEventListener('pointerup', onUpNode);
      } else {
        var tx0 = model.tx, ty0 = model.ty;
        function onMovePan(e2) {
          model.tx = tx0 + (e2.clientX - startX) * (model.w / svg.clientWidth);
          model.ty = ty0 + (e2.clientY - startY) * (model.w / svg.clientWidth);
          paint(model);
        }
        function onUpPan() {
          svg.removeEventListener('pointermove', onMovePan);
          svg.removeEventListener('pointerup', onUpPan);
        }
        svg.addEventListener('pointermove', onMovePan);
        svg.addEventListener('pointerup', onUpPan);
      }
    });
  }

  function runGraph(mount, model) {
    if (model.nodes.length <= 1) {
      mount.innerHTML = '<div class="empty-state"><h3>Nothing to map</h3>' +
        '<p>Adjust the filters above to bring nodes back.</p></div>';
      return;
    }
    buildSvg(mount, model);
    model.alpha = 1;
    heat(model, 1);
  }

  /* ================= panels ================= */

  function dotRow(label, color) {
    return '<span class="folder-dot"><span class="dot" style="background:' + color + '"></span>' + esc(label) + '</span>';
  }
  function openPanel(html) {
    var p = document.getElementById('side-panel');
    p.querySelector('.panel-body').innerHTML = html;
    p.scrollTop = 0;
  }
  function pathRow(absPath, shown) {
    return '<div class="panel-mono">' +
      '<a class="path-link" target="_blank" rel="noopener" title="Open the folder" href="file://' +
      encodeURI(absPath) + '">' + esc(shown) + '</a>' +
      ' <button class="copy-btn" data-copy="' + esc(absPath) + '">copy</button></div>';
  }

  function panelForScope(sc) {
    if (!sc) return;
    var h = '<h3>' + esc(sc.name) + '</h3>';
    if (sc.type === 'user') h += '<div class="panel-tag">your personal scope</div>';
    if (sc.purpose) h += '<p>' + esc(sc.purpose) + '</p>';
    if (sc.aboutHtml) {
      h += '<div class="panel-section">About</div><div class="panel-prose">' + sc.aboutHtml + '</div>';
    }
    h += '<div class="panel-section">Where</div>' + pathRow((D.root || '') + '/' + (sc.path || ''), sc.path || '');
    if (sc.version) h += '<div class="panel-section">Conventions</div><div>ExFu ' + esc(sc.version) + '</div>';
    var fts = sc.folderTypes || {};
    var keys = Object.keys(fts).sort();
    if (keys.length) {
      h += '<div class="panel-section">What lives here</div><div class="folder-dots">';
      keys.forEach(function (k) { h += dotRow(k, fts[k] === 'pointer' ? COL.blue : COL.green); });
      h += '</div>';
    }
    var ags = agentsForScope(sc.name);
    if (ags.length) {
      h += '<div class="panel-section">Agents</div>';
      ags.forEach(function (a) {
        h += '<div class="panel-row" data-agent="' + esc(a.name) + '">' + dotRow(a.name, healthColor(a.status)) +
             ' <span class="panel-muted">' + esc(a.cadence || '') + '</span></div>';
      });
    }
    if ((sc.children || []).length) {
      h += '<div class="panel-section">Inside it</div><div>' + sc.children.map(esc).join(', ') + '</div>';
    }
    var ctx = sc.context || [];
    if (ctx.length) {
      h += '<div class="panel-section">Context</div>';
      var head = ctx.slice(0, 6), rest = ctx.slice(6);
      head.forEach(function (c, i) {
        h += '<details class="panel-doc"' + (i === 0 ? ' open' : '') + '><summary>' + esc(c.title) +
             '</summary><div class="panel-prose">' + c.html + '</div></details>';
      });
      if (rest.length) {
        h += '<details class="ws-more"><summary>and ' + rest.length + ' more file' +
             (rest.length === 1 ? '' : 's') + '</summary>';
        rest.forEach(function (c) {
          h += '<details class="panel-doc"><summary>' + esc(c.title) +
               '</summary><div class="panel-prose">' + c.html + '</div></details>';
        });
        h += '</details>';
      }
      if (sc.contextMore) {
        h += '<div class="panel-muted">+ ' + sc.contextMore + ' subfolder' +
             (sc.contextMore === 1 ? '' : 's') + ' -- open the folder to browse</div>';
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
    if (a.lastRun) h += '<div class="panel-section">Last run</div><div>' + esc(a.lastRun) + '</div>';
    h += '<div class="panel-guidance">' + (a.registered
      ? 'To change or pause it, just tell your AI.'
      : 'Staged, not yet running. Tell your AI "install ' + esc(a.name) + '" to switch it on.') + '</div>';
    openPanel(h);
  }

  function panelForGroup(g) {
    var label = (g && (g.label || g.name)) || '';
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

  function panelForItem(kind, idx) {
    var list = (D.workspace || {})[kind] || [];
    var it = list[idx];
    if (!it) return;
    var kindLabel = { todos: 'task', reminders: 'reminder', inbox: 'inbox item' }[kind] || kind;
    var h = '<h3>' + esc(it.title) + '</h3>';
    h += '<div class="panel-tag">' + esc(kindLabel) + ' &middot; ' + esc(it.scope) + '</div>';
    if (it.meta) h += '<p>' + esc(it.meta) + '</p>';
    if (it.html) h += '<div class="panel-section">Detail</div><div class="panel-prose">' + it.html + '</div>';
    if (it.pointer) {
      h += '<div class="panel-section">Where it lives</div><div class="panel-prose">' + esc(it.pointer) + '</div>';
    }
    if (it.path) {
      h += '<div class="panel-section">Folder</div>' + pathRow(it.path, it.rel || it.path);
    }
    h += '<div class="panel-guidance">' + (kind === 'inbox'
      ? 'To file it, tell your AI where it belongs -- or let the nightly sweep suggest a home.'
      : 'Mention this to your AI by name to update or complete it.') + '</div>';
    openPanel(h);
  }

  function onNodeClick(g) {
    var t = g.getAttribute('data-stype'), n = g.getAttribute('data-name');
    if (t === 'agent') panelForAgent(D.agents.filter(function (a) { return a.name === n; })[0]);
    else if (t === 'group') panelForGroup({ label: n });
    else panelForScope(scopeByName(n));
  }

  /* ================= wiring ================= */

  function renderGraphs() {
    var sg = document.getElementById('scope-graph');
    if (sg && sg.offsetParent !== null) {
      runGraph(sg, modelScopeGraph(
        document.getElementById('f-groups').checked,
        document.getElementById('f-agents').checked));
    }
    var ag = document.getElementById('agents-graph');
    if (ag && ag.offsetParent !== null) {
      runGraph(ag, modelAgentsGraph(
        document.getElementById('f-lib').checked,
        document.getElementById('f-biz').checked,
        document.getElementById('f-exfu').checked));
    }
  }

  function init() {
    /* the panel is always open; greet with the personal scope first so the
       right pane is never blank, whatever else happens during wiring */
    try {
      var user0 = null;
      D.scopes.forEach(function (s) { if (s.type === 'user') user0 = s; });
      if (user0) panelForScope(user0);
      else openPanel('<h3>Welcome</h3><p>Click anything -- a scope, an agent, a task -- and its story appears here.</p>');
    } catch (e) { if (window.console) console.error('exfu greet', e); }

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
      if (ev.target.closest && ev.target.closest('.gnode')) return; // graph handles itself
      if (ev.target.closest && (ev.target.closest('a') || ev.target.closest('button') || ev.target.closest('.hint'))) {
        // fall through only for copy handling below
      } else {
        var item = ev.target.closest ? ev.target.closest('[data-item]') : null;
        if (item) {
          var parts = item.getAttribute('data-item').split(':');
          panelForItem(parts[0], parseInt(parts[1], 10));
          return;
        }
        var agentCard = ev.target.closest ? ev.target.closest('[data-agent]') : null;
        if (agentCard) {
          var an = agentCard.getAttribute('data-agent');
          panelForAgent(D.agents.filter(function (a) { return a.name === an; })[0]);
          return;
        }
        var card = ev.target.closest ? ev.target.closest('[data-scope]') : null;
        if (card) { panelForScope(scopeByName(card.getAttribute('data-scope'))); return; }
      }
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
      } else fallback();
    });

    /* split-pane divider: window-level listeners, no capture pitfalls */
    var panel = document.getElementById('side-panel');
    var grip = document.getElementById('panel-grip');
    try {
      var saved = localStorage.getItem('exfu-panel-w');
      if (saved) document.documentElement.style.setProperty('--panel-w', saved + 'px');
    } catch (e) {}
    if (grip && panel) {
      grip.addEventListener('pointerdown', function (ev) {
        ev.preventDefault();
        grip.classList.add('dragging');
        document.body.classList.add('resizing');
        function onMove(e2) {
          var w = Math.max(320, Math.min(window.innerWidth * 0.75, window.innerWidth - e2.clientX));
          document.documentElement.style.setProperty('--panel-w', w + 'px');
        }
        function onUp(e3) {
          grip.classList.remove('dragging');
          document.body.classList.remove('resizing');
          window.removeEventListener('pointermove', onMove);
          window.removeEventListener('pointerup', onUp);
          try {
            localStorage.setItem('exfu-panel-w',
              String(Math.round(panel.getBoundingClientRect().width)));
          } catch (e) {}
        }
        window.addEventListener('pointermove', onMove);
        window.addEventListener('pointerup', onUp);
      });
    }

  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
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

    # Render scope cards in a grid; grouped scopes sit inside container boxes
    parts.append('<div class="scope-grid">')
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

    parts.append("</div>")  # /scope-grid

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

    card_open = (
        f'<div class="card card-dim" data-agent="{name}">'
        if not enabled else f'<div class="card" data-agent="{name}">'
    )
    parts = [card_open]
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
                f'<div class="card card-dim" data-agent="{esc(u["name"])}"><div class="lib-card">'
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
            def _inbox_card(cf):
                fields = parse_yaml_frontmatter(cf["text"])
                body = strip_frontmatter(cf["text"])
                title_html = esc(deslug(cf["filename"]))
                status = fields.get("status", "")
                if status:
                    title_html += f'<span class="chip chip-quiet">{esc(status)}</span>'
                bits = ['<div class="inbox-card">',
                        f'<div class="inbox-title">{title_html}</div>']
                snippet = first_snippet(body)
                if snippet:
                    bits.append(f'<div class="inbox-snippet">{inline_md(snippet)}</div>')
                age = file_age_label(cf.get("mtime"))
                if age:
                    bits.append(f'<div class="inbox-age">{esc(age)}</div>')
                bits.append("</div>")
                return "".join(bits)

            for cf in content_files[:8]:
                parts.append(_inbox_card(cf))
            rest = content_files[8:]
            if rest:
                plural = "" if len(rest) == 1 else "s"
                parts.append(
                    f'<details class="ws-more"><summary>and {len(rest)} more item{plural}</summary>'
                    + "".join(_inbox_card(cf) for cf in rest) + "</details>"
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
        for f in files:
            text = strip_frontmatter(read_file_text(f, max_bytes=1600))
            if not text.strip():
                continue
            context_items.append({
                "title": ("About this folder" if f.name == "readme.md"
                          else deslug(f.name)),
                "html": render_markdown_mini(text, max_items=12),
            })
        # Every file ships; the sidebar folds the long tail into an expander.
        # Only subfolders stay behind -- browse those in the folder itself.
        more = len(subdirs)
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


def split_reminder_entries(body):
    """
    Split a reminders file into individual entries. Heading-led blocks become
    entries titled by their heading; a heading-free file yields one entry per
    bullet line; failing both, the whole body is a single entry.
    """
    lines = body.split("\n")
    has_heading = any(l.strip().startswith("#") for l in lines)
    entries = []
    if has_heading:
        title, buf = None, []
        for l in lines:
            s = l.strip()
            if s.startswith("#"):
                if title is not None and "\n".join(buf).strip():
                    entries.append((title, "\n".join(buf).strip()))
                title = s.lstrip("#").strip()
                buf = []
            else:
                buf.append(l)
        if title is not None and "\n".join(buf).strip():
            entries.append((title, "\n".join(buf).strip()))
        return entries
    bullets = [l.strip() for l in lines if l.strip().startswith(("- ", "* "))]
    if bullets:
        return [(b.lstrip("-* ").strip(), b) for b in bullets]
    if body.strip():
        return [(first_snippet(body) or "Reminder", body)]
    return []


def build_workspace_items(root, index_data):
    """
    Workspace content as first-class items: every task, reminder, and inbox
    capture becomes one card on its view and one detail panel in the sidebar.
    One shape for all three ontologies -- the template scope views plug into.
    """
    out = {"todos": [], "reminders": [], "inbox": []}
    if not index_data:
        return out
    scopes = index_data.get("scopes", [])

    for kind, folder in (("todos", "todo"), ("reminders", "reminders"), ("inbox", "inbox")):
        for it in collect_workspace_items(root, scopes, folder):
            scope_name = it.get("scope_name", "")
            rel_folder = f'{it.get("scope_path", "")}{folder}/'
            abs_folder = str(root / it.get("scope_path", "") / folder)
            pointer = it.get("pointer_target")
            content_files = [
                cf for cf in it.get("content_files", [])
                if cf["filename"] not in ("done.md", "archive.md")
            ]
            base = {"scope": scope_name, "path": abs_folder, "rel": rel_folder}

            if pointer:
                tool = pointer_tool_name(pointer)
                out[kind].append(dict(base, **{
                    "title": f"Managed in {tool}" if tool else "Managed elsewhere",
                    "pointer": pointer,
                    "meta": "the folder points at your existing tool",
                    "html": "",
                    "kind": "pointer",
                }))
                continue

            if kind == "todos":
                task_lines = list(it.get("agent_tasks", []))
                for cf in content_files:
                    body = strip_frontmatter(cf["text"])
                    for line in body.split("\n"):
                        if CHECKBOX_RE.match(line.strip()):
                            task_lines.append(line.strip())
                for line in task_lines:
                    m = CHECKBOX_RE.match(line)
                    if not m:
                        continue
                    done = m.group(1).lower() == "x"
                    text = m.group(2).strip()
                    out[kind].append(dict(base, **{
                        "title": text,
                        "done": done,
                        "meta": "done" if done else "open",
                        "html": render_markdown_mini(line, max_items=4),
                        "kind": "task",
                    }))
            elif kind == "reminders":
                for cf in content_files:
                    body = strip_frontmatter(cf["text"])
                    for title, entry_body in split_reminder_entries(body):
                        out[kind].append(dict(base, **{
                            "title": title,
                            "meta": deslug(cf["filename"]),
                            "snippet": first_snippet(entry_body),
                            "html": render_markdown_mini(entry_body, max_items=30),
                            "kind": "reminder",
                        }))
            else:  # inbox
                for cf in content_files:
                    fields = parse_yaml_frontmatter(cf["text"])
                    body = strip_frontmatter(cf["text"])
                    age = file_age_label(cf.get("mtime"))
                    status = fields.get("status", "")
                    meta_bits = [b for b in (age, status) if b]
                    out[kind].append(dict(base, **{
                        "title": deslug(cf["filename"]),
                        "meta": " -- ".join(meta_bits),
                        "snippet": first_snippet(body),
                        "html": render_markdown_mini(body, max_items=30),
                        "kind": "capture",
                    }))
    return out


def render_item_cards(kind, items, label, empty_guidance):
    """One workspace ontology as a grid of clickable item cards."""
    guidance = f'<div class="guidance">{empty_guidance}</div>'
    if not items:
        return (
            f'<div class="empty-state"><h3>Nothing in {esc(label.lower())} yet</h3>'
            "<p>This view fills itself from your scopes.</p></div>" + guidance
        )
    parts = ['<div class="item-grid">']
    for i, it in enumerate(items):
        classes = "item-card"
        if it.get("done"):
            classes += " item-done"
        parts.append(f'<div class="{classes}" data-item="{kind}:{i}">')
        parts.append(f'<div class="item-scope">{esc(it.get("scope", ""))}</div>')
        if it.get("kind") == "pointer":
            parts.append(f'<span class="chip">{esc(it.get("title", ""))}</span>')
            pointer_line = first_snippet(it.get("pointer", "")) or it.get("pointer", "")
            parts.append(f'<div class="item-meta">{esc(pointer_line)}</div>')
        else:
            tick = ""
            if it.get("kind") == "task":
                mark = "&#10003;" if it.get("done") else ""
                tick = f'<span class="ws-box">{mark}</span> '
            parts.append(f'<div class="item-title">{tick}{esc(it.get("title", ""))}</div>')
            snippet = it.get("snippet", "")
            if snippet:
                parts.append(f'<div class="item-meta">{esc(snippet)}</div>')
            elif it.get("meta"):
                parts.append(f'<div class="item-meta">{esc(it.get("meta", ""))}</div>')
        parts.append("</div>")
    parts.append("</div>")
    parts.append(guidance)
    return "\n".join(parts)


def render_workspace_view(root, index_data, kind, label, empty_guidance):
    """
    One workspace folder-type (todo, reminders, inbox) as its own top-level
    view. The same template serves every ontology: collect, filter, render,
    and close with guidance on how to create content when there is none.
    """
    if index_data is None:
        return (
            '<div class="empty-state"><h3>No substrate index found</h3>'
            "<p>Run the nightly index first. This view needs the index to know "
            "where to look.</p></div>"
        )
    items = collect_workspace_items(root, index_data.get("scopes", []), kind)
    items = [
        i for i in items
        if i.get("pointer_target") or i.get("content_files") or i.get("agent_tasks")
    ]
    body = render_workspace_folder(items, label, kind)
    guidance = f'<div class="guidance">{empty_guidance}</div>'
    if not body:
        return (
            f'<div class="empty-state"><h3>Nothing in {esc(label.lower())} yet</h3>'
            "<p>This view fills itself from your scopes.</p></div>" + guidance
        )
    return body + guidance


def discover_scope_views(root, scopes_flat):
    """
    Scope-provided dashboard views -- the pluggable half of the view registry.
    Any scope's visualisations/<name>/ folder carrying a viz.md manifest with
    `view: true` is mounted as a top-level tab, embedded by iframe relative to
    the dashboard's own folder. Drop a bundle in a scope, regenerate, and it
    appears; nothing in the dashboard needs to know about it in advance.
    """
    found = []
    dash_dir = root / "exfu" / "visualisations" / "dashboard"
    for s in scopes_flat:
        vdir = root / s.get("path", "") / "visualisations"
        if not vdir.is_dir():
            continue
        try:
            subs = sorted(vdir.iterdir())
        except OSError:
            continue
        for sub in subs:
            if not sub.is_dir():
                continue
            fields = parse_yaml_frontmatter(
                read_file_text(sub / "viz.md", max_bytes=2048)
            )
            if str(fields.get("view", "")).lower() not in ("true", "yes"):
                continue
            name = fields.get("name") or deslug(sub.name)
            entry = sub / fields.get("entry", "index.html")
            if not entry.exists():
                continue
            rel = os.path.relpath(entry, dash_dir)
            byline = f'From the {esc(s.get("name", ""))} scope'
            desc = fields.get("description", "")
            if desc:
                byline += f" -- {esc(desc)}"
            slug = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
            found.append({
                "id": f"tab-viz-{slug}",
                "label": name,
                "html": (
                    f'<div class="viz-byline">{byline}</div>'
                    f'<iframe class="viz-frame" src="{esc(rel)}" title="{esc(name)}"></iframe>'
                ),
            })
    return found


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

    # Client-side payload for the graph views and sidebar
    workspace_items = build_workspace_items(root, index_data)
    payload = build_dashboard_data(root, registry_data, unregistered, scopes_flat)
    payload["workspace"] = workspace_items
    data_json = json.dumps(payload).replace("</", "<\\/")

    scope_filters = (
        '<label><input type="checkbox" id="f-groups" checked> grouping folders</label>'
        '<label><input type="checkbox" id="f-agents"> agents</label>'
    )
    agent_filters = (
        '<label><input type="checkbox" id="f-lib" checked> librarians</label>'
        '<label><input type="checkbox" id="f-biz" checked> business agents</label>'
        '<label><input type="checkbox" id="f-exfu"> ExFu agents</label>'
    )

    # The view registry: built-in views first, then any views scopes provide.
    scopes_panel = (
        render_view_bar("scopes", scope_filters)
        + f'<div data-pane="scopes-list">{substrate_map_html}</div>'
        + '<div data-pane="scopes-graph" style="display:none">'
        + '<div id="scope-graph" class="graph-mount"></div>'
        + '<div class="guidance">Click any node to see what lives there, and drag '
        + "nodes to rearrange the map. You sit in the middle; every scope radiates "
        + "out from you.</div></div>"
    )
    agents_panel = (
        render_view_bar("agents", agent_filters)
        + f'<div data-pane="agents-list">{librarian_html}</div>'
        + '<div data-pane="agents-graph" style="display:none">'
        + '<div id="agents-graph" class="graph-mount"></div>'
        + '<div class="guidance">Each agent hangs off the scope it works for. '
        + "Click one for its story.</div></div>"
    )

    views = [
        {"id": "tab-map", "label": "Your scopes", "html": scopes_panel},
        {"id": "tab-librarians", "label": "Agents", "html": agents_panel},
        {"id": "tab-todos", "label": "Todos", "html": render_item_cards(
            "todos", workspace_items["todos"], "Todos",
            "To track tasks in a scope, tell your AI -- stored as simple "
            "checklists here, or pointed at the tool you already use.")},
        {"id": "tab-reminders", "label": "Reminders", "html": render_item_cards(
            "reminders", workspace_items["reminders"], "Reminders",
            'To set up nudges, tell your AI things like "flag the VAT return '
            'from the 20th of the month" -- they collect here.')},
        {"id": "tab-inbox", "label": "Inbox", "html": render_item_cards(
            "inbox", workspace_items["inbox"], "Inbox",
            "Anything you or your AI drops into a scope's inbox waits here "
            "until it finds a home; the nightly sweep suggests where.")},
    ]
    views.extend(discover_scope_views(root, scopes_flat))

    tabs_html = "".join(
        f'<button class="tab{" active" if i == 0 else ""}" data-tab="{v["id"]}">{esc(v["label"])}</button>'
        for i, v in enumerate(views)
    )
    panels_html = "\n".join(
        f'<div id="{v["id"]}" class="tab-panel{" active" if i == 0 else ""}">\n{v["html"]}\n</div>'
        for i, v in enumerate(views)
    )

    user_name = ""
    for s in scopes_flat:
        if s.get("type") == "user":
            user_name = s.get("name", "")
            break
    title_h1 = f"{esc(user_name)}&rsquo;s substrate" if user_name else "Your substrate"
    page_title = f"ExFu -- {user_name} substrate" if user_name else "ExFu -- your substrate"

    # Assemble page
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(page_title)}</title>
  <style>{render_css()}</style>
</head>
<body>
  <div class="shell">
  <div class="main">
  <div class="container">
    <header>
      <div class="eyebrow">ExFu &middot; substrate snapshot</div>
      <h1>{title_h1}</h1>
      <div class="subtitle">Generated {esc(now)}{' -- index from ' + esc(index_ts) if index_ts else ''}</div>
    </header>

    <div class="tabs">
      {tabs_html}
    </div>

    {panels_html}

    <footer>
      Generated by the ExFu dashboard librarian &middot; open this file any time -- it works offline
    </footer>
  </div>
  </div>

  <aside id="side-panel">
    <div id="panel-grip"></div>
    <div class="panel-body"></div>
  </aside>
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
