#!/usr/bin/env python3
"""
Library index

Builds and maintains the per-machine search index over every docket in the
library, and answers the questions the dispatcher and the compaction
librarian ask of it. The canonical records are the JSONL files inside the
library; this index is a cache, rebuilt from them by content hash, and never
a source of truth.

The index is binary, so it lives outside the synced root at
~/.exfu/derived/<library-id>/library.sqlite. EXFU_DERIVED_DIR overrides the
parent directory; library-id is the first 12 hex characters of the sha256 of
the resolved root path. Nothing binary is ever written inside the library.
The one thing this tool writes there is the text cache exfu/derived/due.json,
which the dispatcher falls back to when the index cannot be opened, and which
is refused when the docket files it was computed from have since changed.

Subcommands (root is the substrate root in every case):

    rebuild <root> [--trust-hints]
        Incremental rebuild. Every docket file is hashed and only rows whose
        content changed are re-indexed. With --trust-hints a file whose
        mtime and size match the last run is skipped without hashing (the
        hourly run trusts hints; the nightly run validates everything).

    query <root> <terms...> [--scope S] [--kind K] [--status S] [--limit N] [--json]
        Full-text search over docket entries (FTS5, bm25 ranking).

    due <root> [--at ISO] [--actor HANDLE] [--json] [--trust-hints]
        The dry run: which armed triggers are due at --at (default now) for
        this actor, with each one's resolved channel and send mode. Writes
        exfu/derived/due.json when run for the real now.

    explain <root> <trigger id> [--at ISO] [--actor HANDLE]
        One trigger: its row, next occurrence, recent receipts, and why it
        is or is not due.

    fire <root> <trigger id> --now [--json]
        The due entry for an immediate occurrence. Writes nothing; the caller
        then records it with receipt.

    receipt <root> <occurrence> intent|result [--status S] [--signals a,b]
            [--key K] [--payload TEXT] [--actor H] [--machine M] [--json]
        Append an immutable fire receipt to the owning scope's fires.jsonl.
        A result receipt also appends the reported signals, disarms a once
        trigger, and pauses a trigger after three consecutive failures.

    compact <root> [--dry-run]
        Fold conflicted copies, archive closed entries after 30 days, emit
        entry-completed signals, sweep orphaned triggers, and drop signals
        older than 30 days and receipts older than 90.

Usage:
    python3 index.py due /path/to/substrate-root --json
    python3 index.py receipt /path/to/substrate-root <occurrence> intent
    python3 index.py compact /path/to/substrate-root

Exit codes:
    0 -- ok (including "nothing due")
    1 -- the tool failed (bad arguments, unknown trigger, unwritable docket)
    2 -- the index is unavailable and due.json is stale, so no due view
         could be served

Misfire handling: `due` lists the elapsed occurrences it will not fire under
`skipped_occurrences`; the `receipt ... intent` command records them as
skipped result receipts at the moment the trigger is actually acted on.
`due` itself never writes a receipt.

Stdlib only. Python 3.9 or newer.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1"
UTC = timezone.utc

ARCHIVE_AFTER_DAYS = 30
ORPHAN_AFTER_DAYS = 30
SIGNAL_RETENTION_DAYS = 30
RECEIPT_RETENTION_DAYS = 90
DAILY_SEND_CAP = 20
RUN_SEND_CAP = 10
LOOP_FIRES_PER_DAY = 5
CRON_LOOKBACK_DAYS = 400
MAX_SKIPPED = 100

RESULT_STATUSES = ("delivered", "drafted", "failed", "skipped", "suppressed")
ITEM_STATUSES = ("open", "done", "archived")

# Docket file -> (index table, item kind)
DOCKET_FILES = {
    "todo.jsonl": ("items", "todo"),
    "reminders.jsonl": ("items", "reminder"),
    "agent-backlog.jsonl": ("items", "agent-backlog"),
    "triggers.jsonl": ("triggers", None),
    "signals.jsonl": ("signals", None),
    "fires.jsonl": ("fires", None),
    "channels.jsonl": ("channels", None),
}
ITEM_FILES = {"todo.jsonl": "todo", "reminders.jsonl": "reminder", "agent-backlog.jsonl": "agent-backlog"}
MUTABLE_STEMS = {"todo", "reminders", "agent-backlog", "triggers", "channels"}
IMMUTABLE_STEMS = {"signals", "fires", "archive"}

SKIP_NAMES = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__",
    ".DS_Store", ".idea", ".vscode", ".claude", ".omc",
}

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

CONFLICT_RE = re.compile(r"^(?P<stem>.+?) \((?:.*'s )?conflicted copy[^)]*\)\.jsonl$")

_warnings = []


def warn(msg):
    """Collect a warning and print it to stderr."""
    _warnings.append(msg)
    print(f"warning: {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

ISO_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?)?"
    r"\s*(Z|z|[+-]\d{2}:?\d{2})?$"
)


def parse_iso(value, default_tz=None):
    """
    Parse an ISO-8601 timestamp tolerantly: date only, 'Z', offsets with or
    without a colon, a space instead of 'T'. A naive value is placed in
    default_tz (UTC when not given). Returns an aware datetime, or None.
    """
    if not isinstance(value, str):
        return None
    m = ISO_RE.match(value.strip())
    if not m:
        return None
    y, mo, d, hh, mm, ss, _frac, tz = m.groups()
    try:
        dt = datetime(int(y), int(mo), int(d), int(hh or 0), int(mm or 0), int(ss or 0))
    except ValueError:
        return None
    if tz and tz.upper() == "Z":
        tzinfo = UTC
    elif tz:
        sign = 1 if tz[0] == "+" else -1
        digits = tz[1:].replace(":", "")
        tzinfo = timezone(sign * timedelta(hours=int(digits[:2]), minutes=int(digits[2:])))
    else:
        tzinfo = default_tz or UTC
    return dt.replace(tzinfo=tzinfo)


def utc_now():
    return datetime.now(UTC).replace(microsecond=0)


def utc_iso(dt):
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def instant_str(dt):
    """
    The scheduled-instant form used inside occurrence ids: local wall time
    with its offset, e.g. 2026-09-04T09:00+01:00. Seconds only when non-zero.
    """
    base = dt.strftime("%Y-%m-%dT%H:%M")
    if dt.second:
        base += dt.strftime(":%S")
    off = dt.utcoffset() or timedelta(0)
    total = int(off.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    return f"{base}{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"


def load_zone(name):
    """Resolve an IANA zone name; fall back to UTC with a warning."""
    if not name:
        return UTC
    if ZoneInfo is None:
        warn(f"zoneinfo unavailable; treating '{name}' as UTC")
        return UTC
    try:
        return ZoneInfo(name)
    except Exception:  # ZoneInfoNotFoundError or a bad key
        warn(f"unknown time zone '{name}'; treating it as UTC")
        return UTC


def occurrence_suffix(occurrence):
    """The part of an occurrence id after the trigger id, or ''."""
    return occurrence.split("@", 1)[1] if "@" in occurrence else ""


# ---------------------------------------------------------------------------
# Ids and hashing
# ---------------------------------------------------------------------------

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def id_exists(conn, candidate):
    for table in ("items", "triggers", "signals", "fires", "channels"):
        if conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (candidate,)).fetchone():
            return True
    return False


def new_id(conn=None, now=None, taken=None):
    """
    A library-wide id: UTC timestamp to the second plus ten Crockford base32
    characters from the secrets module, regenerated on collision with the
    index (and with any ids handed in as `taken`, for ids minted in a batch).
    """
    stamp = (now or utc_now()).strftime("%Y%m%dT%H%M%SZ")
    while True:
        rand = "".join(secrets.choice(CROCKFORD) for _ in range(10))
        candidate = f"{stamp}-{rand}"
        if taken is not None and candidate in taken:
            continue
        if conn is not None and id_exists(conn, candidate):
            continue
        if taken is not None:
            taken.add(candidate)
        return candidate


# ---------------------------------------------------------------------------
# JSONL reading and atomic writing
# ---------------------------------------------------------------------------

def read_jsonl(path):
    """
    Read a JSONL file. Returns (rows, bad_lines): rows are dicts carrying an
    id; bad_lines are the raw text of lines that could not be used, kept so a
    rewrite can preserve them verbatim rather than silently dropping them.
    Blank lines are ignored; malformed lines are skipped with a warning.
    """
    rows, bad = [], []
    path = Path(path)
    if not path.is_file():
        return rows, bad
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        warn(f"{path}: unreadable ({e})")
        return rows, bad
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            warn(f"{path}:{n}: malformed JSON, skipped ({e.msg})")
            bad.append(line)
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get("id"), str) or not obj["id"]:
            warn(f"{path}:{n}: not an object with an id, skipped")
            bad.append(line)
            continue
        rows.append(obj)
    return rows, bad


def write_jsonl(path, rows, bad_lines=()):
    """
    Atomically rewrite a JSONL file: temp file in the same directory, then
    os.replace. Refuses to create the parent folder -- a docket folder is
    materialised by an agent, never by this tool.
    """
    path = Path(path)
    if not path.parent.is_dir():
        raise RuntimeError(f"refusing to write {path}: its folder does not exist")
    tmp = path.parent / f".{path.name}.{secrets.token_hex(4)}.tmp"
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    data += "".join(line + "\n" for line in bad_lines)
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def append_jsonl(path, rows):
    """
    Atomically append rows, preserving the existing file text verbatim
    (including any lines the parser could not read).
    """
    path = Path(path)
    if not path.parent.is_dir():
        raise RuntimeError(f"refusing to write {path}: its folder does not exist")
    existing = ""
    if path.is_file():
        existing = path.read_text(encoding="utf-8", errors="replace")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    tmp = path.parent / f".{path.name}.{secrets.token_hex(4)}.tmp"
    data = existing + "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def write_text_atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{secrets.token_hex(4)}.tmp"
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Library walk: scopes and their dockets
# ---------------------------------------------------------------------------

class Scope:
    __slots__ = ("name", "path", "rel", "parent")

    def __init__(self, name, path, rel, parent):
        self.name = name
        self.path = path
        self.rel = rel
        self.parent = parent

    @property
    def docket(self):
        return self.path / "docket"


def parse_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^(\w[\w-]*):\s*(.+)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fields


def scope_name_of(scope_dir):
    try:
        fields = parse_frontmatter((scope_dir / "scope.md").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        fields = {}
    return fields.get("name") or scope_dir.name


def walk_scopes(root):
    """
    Every scope in the library: user/ first, then scopes/** recursively.
    A directory is a scope iff it holds scope.md; children live only under
    a scope's scopes/ subdirectory; grouping folders are descended through.
    The structural parent (the enclosing scope) is what channel resolution
    walks. Returns a list of Scope in walk order.
    """
    root = Path(root)
    scopes = []
    seen = {}

    def add(name, path, parent):
        if name in seen:
            warn(f"duplicate scope name '{name}' at {path}; keeping {seen[name]}")
            return None
        rel = path.relative_to(root).as_posix()
        sc = Scope(name, path, rel, parent)
        seen[name] = rel
        scopes.append(sc)
        return sc

    user_dir = root / "user"
    if (user_dir / "scope.md").is_file():
        add(scope_name_of(user_dir), user_dir, None)

    def scan(directory, parent_name):
        if not directory.is_dir():
            return
        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return
        for entry in entries:
            if not entry.is_dir() or entry.name in SKIP_NAMES or entry.name.startswith("."):
                continue
            if (entry / "scope.md").is_file():
                sc = add(scope_name_of(entry), entry, parent_name)
                if sc is not None:
                    scan(entry / "scopes", sc.name)
            else:
                scan(entry, parent_name)

    scan(root / "scopes", None)
    return scopes


def user_scope_name(scopes):
    for sc in scopes:
        if sc.rel == "user":
            return sc.name
    return None


def scope_chain(scopes_by_name, scope_name):
    """Own scope, then each enclosing scope, then the user scope."""
    chain = []
    current = scope_name
    guard = 0
    while current and current in scopes_by_name and guard < 50:
        chain.append(current)
        current = scopes_by_name[current].parent
        guard += 1
    user = None
    for sc in scopes_by_name.values():
        if sc.rel == "user":
            user = sc.name
    if user and user not in chain:
        chain.append(user)
    return chain


def docket_source_files(scopes):
    """Every docket file that currently exists, as (rel path, absolute path)."""
    out = []
    for sc in scopes:
        for fname in DOCKET_FILES:
            p = sc.docket / fname
            if p.is_file():
                out.append((f"{sc.rel}/docket/{fname}", p))
    return out


def current_source_hashes(scopes):
    return {rel: sha256_bytes(p.read_bytes()) for rel, p in docket_source_files(scopes)}


# ---------------------------------------------------------------------------
# Index location and schema
# ---------------------------------------------------------------------------

def library_id(root):
    return sha256_text(str(Path(root).resolve()))[:12]


def index_dir(root):
    base = os.environ.get("EXFU_DERIVED_DIR") or os.path.join(os.path.expanduser("~"), ".exfu", "derived")
    return Path(base) / library_id(root)


def index_path(root):
    return index_dir(root) / "library.sqlite"


SCHEMA = [
    "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)",
    "CREATE TABLE IF NOT EXISTS scopes (name TEXT PRIMARY KEY, path TEXT, parent TEXT)",
    "CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, mtime REAL, size INTEGER, hash TEXT, scope TEXT, table_name TEXT)",
    """CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY, scope TEXT, kind TEXT, status TEXT, title TEXT, notes TEXT,
        agent_notes TEXT, keywords TEXT, created TEXT, updated TEXT, revision INTEGER,
        deleted INTEGER DEFAULT 0, content_hash TEXT, raw TEXT, prev_status TEXT, file TEXT,
        embedding BLOB, embedding_model TEXT)""",
    "CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(id UNINDEXED, title, notes, agent_notes, keywords)",
    """CREATE TABLE IF NOT EXISTS triggers (
        id TEXT PRIMARY KEY, scope TEXT, target_type TEXT, target_scope TEXT, target_id TEXT,
        assess TEXT, when_mode TEXT, when_spec TEXT, when_at TEXT, tz TEXT, on_signal TEXT,
        handler_kind TEXT, weight TEXT, ref TEXT, channel TEXT, owner TEXT, status TEXT,
        created TEXT, updated TEXT, revision INTEGER, raw TEXT, content_hash TEXT, file TEXT,
        orphan_since TEXT)""",
    """CREATE TABLE IF NOT EXISTS signals (
        id TEXT PRIMARY KEY, name TEXT, at TEXT, scope TEXT, source TEXT, payload TEXT,
        raw TEXT, content_hash TEXT, file TEXT)""",
    """CREATE TABLE IF NOT EXISTS fires (
        id TEXT PRIMARY KEY, occurrence TEXT, trigger TEXT, phase TEXT, status TEXT, actor TEXT,
        machine TEXT, at TEXT, signals TEXT, idempotency_key TEXT, raw TEXT, content_hash TEXT,
        file TEXT)""",
    """CREATE TABLE IF NOT EXISTS channels (
        id TEXT PRIMARY KEY, scope TEXT, name TEXT, kind TEXT, via TEXT, target TEXT, send TEXT,
        revision INTEGER, raw TEXT, content_hash TEXT, file TEXT)""",
    "CREATE INDEX IF NOT EXISTS items_scope ON items(scope)",
    "CREATE INDEX IF NOT EXISTS items_status ON items(status)",
    "CREATE INDEX IF NOT EXISTS items_file ON items(file)",
    "CREATE INDEX IF NOT EXISTS triggers_status ON triggers(status)",
    "CREATE INDEX IF NOT EXISTS triggers_on ON triggers(on_signal)",
    "CREATE INDEX IF NOT EXISTS triggers_file ON triggers(file)",
    "CREATE INDEX IF NOT EXISTS signals_name ON signals(name)",
    "CREATE INDEX IF NOT EXISTS signals_at ON signals(at)",
    "CREATE INDEX IF NOT EXISTS signals_file ON signals(file)",
    "CREATE INDEX IF NOT EXISTS fires_trigger ON fires(trigger)",
    "CREATE INDEX IF NOT EXISTS fires_occurrence ON fires(occurrence)",
    "CREATE INDEX IF NOT EXISTS fires_at ON fires(at)",
    "CREATE INDEX IF NOT EXISTS fires_file ON fires(file)",
    "CREATE INDEX IF NOT EXISTS channels_scope_name ON channels(scope, name)",
    "CREATE INDEX IF NOT EXISTS channels_file ON channels(file)",
]

ALL_TABLES = ("scopes", "files", "items", "items_fts", "triggers", "signals", "fires", "channels")


def ensure_schema(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    version = meta_get(conn, "schema_version")
    if version is not None and version != SCHEMA_VERSION:
        for table in ALL_TABLES:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute("DELETE FROM meta")
    for stmt in SCHEMA:
        conn.execute(stmt)
    meta_set(conn, "schema_version", SCHEMA_VERSION)
    if meta_get(conn, "generation") is None:
        meta_set(conn, "generation", "0")
    conn.commit()


def meta_get(conn, key):
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else None


def meta_set(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, str(value)))


def open_index(root):
    """
    Open (creating if needed) the per-machine index. Returns (conn, error):
    conn is None when the index cannot be opened, and error says why.
    """
    try:
        d = index_dir(root)
        d.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(d / "library.sqlite"))
        conn.row_factory = sqlite3.Row
        ensure_schema(conn)
        return conn, None
    except (OSError, sqlite3.Error) as e:
        return None, f"{e}"


# ---------------------------------------------------------------------------
# Rebuild: hash first, upsert only what changed
# ---------------------------------------------------------------------------

def normalise_keywords(value):
    if isinstance(value, list):
        return [str(k) for k in value if k is not None]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def item_content_hash(row):
    return sha256_text(canonical({
        "title": row.get("title"),
        "notes": row.get("notes"),
        "agent_notes": row.get("agent_notes"),
        "keywords": normalise_keywords(row.get("keywords")),
    }))


def row_content_hash(row):
    return sha256_text(canonical({k: v for k, v in row.items() if k not in ("updated", "revision")}))


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def sync_items(conn, scope, kind, rel, rows):
    existing = {
        r["id"]: r for r in conn.execute(
            "SELECT id, status, raw, content_hash, prev_status FROM items WHERE file = ?", (rel,))
    }
    upserted = deleted = 0
    seen = set()
    for row in rows:
        rid = row["id"]
        if rid in seen:
            warn(f"{rel}: duplicate id {rid}; later row wins")
        seen.add(rid)
        raw = canonical(row)
        old = existing.get(rid)
        if old is not None and old["raw"] == raw:
            continue
        status = row.get("status") if isinstance(row.get("status"), str) else None
        prev_status = old["prev_status"] if old is not None else None
        if old is not None and old["status"] != status:
            prev_status = old["status"]
        chash = item_content_hash(row)
        keywords = normalise_keywords(row.get("keywords"))
        is_deleted = 1 if row.get("deleted") is True else 0
        conn.execute(
            """INSERT OR REPLACE INTO items
               (id, scope, kind, status, title, notes, agent_notes, keywords, created, updated,
                revision, deleted, content_hash, raw, prev_status, file, embedding, embedding_model)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,NULL)""",
            (rid, scope, kind, status, _str(row.get("title")), _str(row.get("notes")),
             _str(row.get("agent_notes")), json.dumps(keywords, ensure_ascii=False),
             _str(row.get("created")), _str(row.get("updated")), _int(row.get("revision"), 1),
             is_deleted, chash, raw, prev_status, rel),
        )
        conn.execute("DELETE FROM items_fts WHERE id = ?", (rid,))
        if not is_deleted:
            conn.execute(
                "INSERT INTO items_fts(id, title, notes, agent_notes, keywords) VALUES (?,?,?,?,?)",
                (rid, _str(row.get("title")) or "", _str(row.get("notes")) or "",
                 _str(row.get("agent_notes")) or "", " ".join(keywords)),
            )
        upserted += 1
    for rid in set(existing) - seen:
        conn.execute("DELETE FROM items WHERE id = ?", (rid,))
        conn.execute("DELETE FROM items_fts WHERE id = ?", (rid,))
        deleted += 1
    return upserted, deleted


def trigger_mode(row):
    when = row.get("when") if isinstance(row.get("when"), dict) else {}
    if row.get("on"):
        return "on-signal"
    return when.get("mode")


def sync_triggers(conn, scope, rel, rows):
    existing = {r["id"]: r for r in conn.execute("SELECT id, content_hash FROM triggers WHERE file = ?", (rel,))}
    upserted = deleted = 0
    seen = set()
    for row in rows:
        rid = row["id"]
        seen.add(rid)
        chash = row_content_hash(row)
        old = existing.get(rid)
        if old is not None and old["content_hash"] == chash:
            continue
        target = row.get("target") if isinstance(row.get("target"), dict) else {}
        when = row.get("when") if isinstance(row.get("when"), dict) else {}
        handler = row.get("handler") if isinstance(row.get("handler"), dict) else {}
        conn.execute(
            """INSERT OR REPLACE INTO triggers
               (id, scope, target_type, target_scope, target_id, assess, when_mode, when_spec, when_at,
                tz, on_signal, handler_kind, weight, ref, channel, owner, status, created, updated,
                revision, raw, content_hash, file, orphan_since)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                       (SELECT orphan_since FROM triggers WHERE id = ?))""",
            (rid, scope, _str(target.get("type")), _str(target.get("scope")), _str(target.get("id")),
             _str(row.get("assess")), trigger_mode(row), _str(when.get("spec")), _str(when.get("at")),
             _str(when.get("tz")), _str(row.get("on")), _str(handler.get("kind")), _str(handler.get("weight")),
             _str(handler.get("ref")), _str(row.get("channel")), _str(row.get("owner")),
             _str(row.get("status")), _str(row.get("created")), _str(row.get("updated")),
             _int(row.get("revision"), 1), canonical(row), chash, rel, rid),
        )
        upserted += 1
    for rid in set(existing) - seen:
        conn.execute("DELETE FROM triggers WHERE id = ?", (rid,))
        deleted += 1
    return upserted, deleted


def sync_signals(conn, scope, rel, rows):
    existing = {r["id"]: r for r in conn.execute("SELECT id, content_hash FROM signals WHERE file = ?", (rel,))}
    upserted = deleted = 0
    seen = set()
    for row in rows:
        rid = row["id"]
        seen.add(rid)
        chash = row_content_hash(row)
        old = existing.get(rid)
        if old is not None and old["content_hash"] == chash:
            continue
        conn.execute(
            """INSERT OR REPLACE INTO signals (id, name, at, scope, source, payload, raw, content_hash, file)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (rid, _str(row.get("name")), _str(row.get("at")), _str(row.get("scope")) or scope,
             _str(row.get("source")), _str(row.get("payload")), canonical(row), chash, rel),
        )
        upserted += 1
    for rid in set(existing) - seen:
        conn.execute("DELETE FROM signals WHERE id = ?", (rid,))
        deleted += 1
    return upserted, deleted


def sync_fires(conn, scope, rel, rows):
    existing = {r["id"]: r for r in conn.execute("SELECT id, content_hash FROM fires WHERE file = ?", (rel,))}
    upserted = deleted = 0
    seen = set()
    for row in rows:
        rid = row["id"]
        seen.add(rid)
        chash = row_content_hash(row)
        old = existing.get(rid)
        if old is not None and old["content_hash"] == chash:
            continue
        sigs = row.get("signals")
        conn.execute(
            """INSERT OR REPLACE INTO fires
               (id, occurrence, trigger, phase, status, actor, machine, at, signals, idempotency_key,
                raw, content_hash, file)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rid, _str(row.get("occurrence")), _str(row.get("trigger")), _str(row.get("phase")),
             _str(row.get("status")), _str(row.get("actor")), _str(row.get("machine")), _str(row.get("at")),
             json.dumps(sigs if isinstance(sigs, list) else [], ensure_ascii=False),
             _str(row.get("idempotency_key")), canonical(row), chash, rel),
        )
        upserted += 1
    for rid in set(existing) - seen:
        conn.execute("DELETE FROM fires WHERE id = ?", (rid,))
        deleted += 1
    return upserted, deleted


def sync_channels(conn, scope, rel, rows):
    existing = {r["id"]: r for r in conn.execute("SELECT id, content_hash FROM channels WHERE file = ?", (rel,))}
    upserted = deleted = 0
    seen = set()
    for row in rows:
        rid = row["id"]
        seen.add(rid)
        chash = row_content_hash(row)
        old = existing.get(rid)
        if old is not None and old["content_hash"] == chash:
            continue
        conn.execute(
            """INSERT OR REPLACE INTO channels
               (id, scope, name, kind, via, target, send, revision, raw, content_hash, file)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (rid, scope, _str(row.get("name")), _str(row.get("kind")), _str(row.get("via")),
             _str(row.get("target")), _str(row.get("send")) or "draft", _int(row.get("revision"), 1),
             canonical(row), chash, rel),
        )
        upserted += 1
    for rid in set(existing) - seen:
        conn.execute("DELETE FROM channels WHERE id = ?", (rid,))
        deleted += 1
    return upserted, deleted


def delete_file_rows(conn, table, rel):
    if table == "items":
        ids = [r[0] for r in conn.execute("SELECT id FROM items WHERE file = ?", (rel,))]
        for rid in ids:
            conn.execute("DELETE FROM items_fts WHERE id = ?", (rid,))
    n = conn.execute(f"DELETE FROM {table} WHERE file = ?", (rel,)).rowcount
    return max(n, 0)


def rebuild(conn, root, scopes, trust_hints=False):
    """
    Incremental rebuild. Returns a stats dict. mtime and size are hints that
    a file may be unchanged; only with --trust-hints are they believed
    without hashing. A file whose hash matches the last run is skipped; a
    changed file is parsed and only rows whose content changed are written.
    """
    stats = {"files_scanned": 0, "files_skipped": 0, "files_changed": 0,
             "rows_upserted": 0, "rows_deleted": 0}
    conn.execute("DELETE FROM scopes")
    for sc in scopes:
        conn.execute("INSERT INTO scopes(name, path, parent) VALUES (?,?,?)", (sc.name, sc.rel, sc.parent))

    known = {r["path"]: r for r in conn.execute("SELECT path, mtime, size, hash, table_name FROM files")}
    seen = set()
    changed = False
    for sc in scopes:
        for fname, (table, kind) in DOCKET_FILES.items():
            rel = f"{sc.rel}/docket/{fname}"
            path = sc.docket / fname
            seen.add(rel)
            existing = known.get(rel)
            if not path.is_file():
                if existing is not None:
                    stats["rows_deleted"] += delete_file_rows(conn, table, rel)
                    conn.execute("DELETE FROM files WHERE path = ?", (rel,))
                    stats["files_changed"] += 1
                    changed = True
                continue
            stats["files_scanned"] += 1
            try:
                st = path.stat()
            except OSError as e:
                warn(f"{rel}: cannot stat ({e})")
                continue
            if (trust_hints and existing is not None
                    and existing["mtime"] == st.st_mtime and existing["size"] == st.st_size):
                stats["files_skipped"] += 1
                continue
            try:
                data = path.read_bytes()
            except OSError as e:
                warn(f"{rel}: unreadable ({e})")
                continue
            digest = sha256_bytes(data)
            if existing is not None and existing["hash"] == digest:
                conn.execute("UPDATE files SET mtime = ?, size = ? WHERE path = ?", (st.st_mtime, st.st_size, rel))
                stats["files_skipped"] += 1
                continue
            stats["files_changed"] += 1
            changed = True
            rows, _bad = read_jsonl(path)
            if table == "items":
                up, de = sync_items(conn, sc.name, kind, rel, rows)
            elif table == "triggers":
                up, de = sync_triggers(conn, sc.name, rel, rows)
            elif table == "signals":
                up, de = sync_signals(conn, sc.name, rel, rows)
            elif table == "fires":
                up, de = sync_fires(conn, sc.name, rel, rows)
            else:
                up, de = sync_channels(conn, sc.name, rel, rows)
            stats["rows_upserted"] += up
            stats["rows_deleted"] += de
            conn.execute(
                "INSERT OR REPLACE INTO files(path, mtime, size, hash, scope, table_name) VALUES (?,?,?,?,?,?)",
                (rel, st.st_mtime, st.st_size, digest, sc.name, table),
            )
    for rel, row in known.items():
        if rel not in seen:
            stats["rows_deleted"] += delete_file_rows(conn, row["table_name"], rel)
            conn.execute("DELETE FROM files WHERE path = ?", (rel,))
            stats["files_changed"] += 1
            changed = True
    if changed:
        meta_set(conn, "generation", _int(meta_get(conn, "generation")) + 1)
    meta_set(conn, "last_run", utc_iso(utc_now()))
    meta_set(conn, "root", str(Path(root).resolve()))
    conn.commit()
    stats["generation"] = _int(meta_get(conn, "generation"))
    return stats


def rebuild_summary(stats):
    return (f"Index: {stats['files_scanned']} files scanned, {stats['files_skipped']} unchanged, "
            f"{stats['files_changed']} changed; {stats['rows_upserted']} rows upserted, "
            f"{stats['rows_deleted']} deleted; generation {stats['generation']}.")


# ---------------------------------------------------------------------------
# Cron: five fields, evaluated in the trigger's zone
# ---------------------------------------------------------------------------

MONTH_NAMES = {n: i for i, n in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DOW_NAMES = {n: i for i, n in enumerate(["sun", "mon", "tue", "wed", "thu", "fri", "sat"])}


class Cron:
    __slots__ = ("minutes", "hours", "doms", "months", "dows", "dom_star", "dow_star", "spec")

    def __init__(self, spec):
        fields = spec.split()
        if len(fields) != 5:
            raise ValueError(f"cron spec needs 5 fields, got {len(fields)}: '{spec}'")
        self.spec = spec
        self.minutes = _cron_field(fields[0], 0, 59, {})
        self.hours = _cron_field(fields[1], 0, 23, {})
        self.doms = _cron_field(fields[2], 1, 31, {})
        self.months = _cron_field(fields[3], 1, 12, MONTH_NAMES)
        dows = _cron_field(fields[4], 0, 7, DOW_NAMES)
        self.dows = {0 if d == 7 else d for d in dows}
        self.dom_star = fields[2].strip() == "*"
        self.dow_star = fields[4].strip() == "*"

    def matches_day(self, d):
        if d.month not in self.months:
            return False
        dow = (d.weekday() + 1) % 7  # Python: Monday=0; cron: Sunday=0
        dom_ok = d.day in self.doms
        dow_ok = dow in self.dows
        if self.dom_star and self.dow_star:
            return True
        if self.dom_star:
            return dow_ok
        if self.dow_star:
            return dom_ok
        return dom_ok or dow_ok  # the Vixie rule when both are restricted

    def matches_hour(self, local_dt):
        return self.matches_day(local_dt.date()) and local_dt.hour in self.hours


def _cron_field(field, lo, hi, names):
    field = field.strip().lower()
    if not field:
        raise ValueError("empty cron field")

    def conv(token):
        if token in names:
            return names[token]
        if not token.isdigit():
            raise ValueError(f"bad cron value '{token}'")
        return int(token)

    values = set()
    for part in field.split(","):
        step = 1
        had_step = False
        if "/" in part:
            part, step_s = part.split("/", 1)
            step = conv(step_s)
            had_step = True
            if step < 1:
                raise ValueError("cron step must be positive")
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            a_s, b_s = part.split("-", 1)
            a, b = conv(a_s), conv(b_s)
        else:
            a = conv(part)
            b = hi if had_step else a
        if a < lo or b > hi or a > b:
            raise ValueError(f"cron value out of range: '{part}' (allowed {lo}-{hi})")
        values.update(range(a, b + 1, step))
    return values


def cron_instants_before(cron, tz, until, lookback_days=CRON_LOOKBACK_DAYS):
    """
    Yield the scheduled instants of a cron spec at or before `until`, most
    recent first, as UTC datetimes. An instant that does not exist on a
    spring-forward day is skipped; one that exists twice on a fall-back day
    is yielded once (its first occurrence).
    """
    local = until.astimezone(tz)
    hours = sorted(cron.hours, reverse=True)
    minutes = sorted(cron.minutes, reverse=True)
    for offset in range(lookback_days):
        d = local.date() - timedelta(days=offset)
        if not cron.matches_day(d):
            continue
        for h in hours:
            for m in minutes:
                naive = datetime(d.year, d.month, d.day, h, m)
                aware = naive.replace(tzinfo=tz)
                utc = aware.astimezone(UTC)
                if utc.astimezone(tz).replace(tzinfo=None) != naive:
                    continue
                if utc <= until:
                    yield utc


def cron_next_after(cron, tz, after, lookahead_days=CRON_LOOKBACK_DAYS):
    """The first scheduled instant strictly after `after`, as UTC, or None."""
    local = after.astimezone(tz)
    hours = sorted(cron.hours)
    minutes = sorted(cron.minutes)
    for offset in range(lookahead_days):
        d = local.date() + timedelta(days=offset)
        if not cron.matches_day(d):
            continue
        for h in hours:
            for m in minutes:
                naive = datetime(d.year, d.month, d.day, h, m)
                aware = naive.replace(tzinfo=tz)
                utc = aware.astimezone(UTC)
                if utc.astimezone(tz).replace(tzinfo=None) != naive:
                    continue
                if utc > after:
                    return utc
    return None


# ---------------------------------------------------------------------------
# Actors, grants, channels
# ---------------------------------------------------------------------------

def _unfenced_lines(text):
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield line


ACTOR_NON_IDENTITY_KEYS = {"recorded", "notes", "role"}


def read_actors(root):
    """
    The actor records in durable/ledger/actors.md, in file order. Each `## <handle>`
    heading opens one record; every `- key: value` line beneath it except the
    bookkeeping keys is a name that resolves to the handle (`aliases` is a comma
    list; `display`, `slack`, `email` and any other medium are taken whole).
    Returns a list of {"handle", "names": [...]}.
    """
    path = Path(root) / "durable" / "ledger" / "actors.md"
    actors = []
    if not path.is_file():
        return actors
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return actors
    current = None
    for line in _unfenced_lines(text):
        m = re.match(r"^##\s+(\S+)", line)
        if m:
            handle = m.group(1).strip()
            if handle.startswith("<"):
                current = None
                continue
            current = {"handle": handle, "names": []}
            actors.append(current)
            continue
        if current is None:
            continue
        m = re.match(r"^\s*-\s*([A-Za-z][\w -]*?):\s*(.+?)\s*$", line)
        if not m:
            continue
        key, value = m.group(1).strip().lower(), m.group(2).strip()
        if key in ACTOR_NON_IDENTITY_KEYS or not value or value.startswith("<"):
            continue
        parts = [v.strip() for v in value.split(",")] if key == "aliases" else [value]
        current["names"].extend(v for v in parts if v)
    return actors


def alias_map(actors):
    """Lower-cased name (handle, display, alias, or medium id) -> canonical handle."""
    table = {}
    for a in actors:
        for name in [a["handle"], *a["names"]]:
            key = str(name).strip().lower().lstrip("@")
            if key and key not in table:
                table[key] = a["handle"]
    return table


def resolve_actor(name, actors):
    """
    The canonical handle for a name: through the actor records when one knows it,
    else the name as written. 'any' and empty names pass through unchanged.
    """
    if name is None:
        return None
    text = str(name).strip()
    if not text or text == "any":
        return text
    return alias_map(actors).get(text.lower().lstrip("@"), text)


def known_actor(name, actors):
    """True when a name resolves to a registered actor (always True with no records)."""
    if not actors:
        return True
    return str(name).strip().lower().lstrip("@") in alias_map(actors)


def default_actor(root, actors=None):
    """
    The library's actor: the first record in durable/ledger/actors.md; else the
    `actor handle:` line of durable/ledger/install.md; else its `installed by:`
    line resolved through the records; else 'any'.
    """
    if actors is None:
        actors = read_actors(root)
    if actors:
        return actors[0]["handle"]
    path = Path(root) / "durable" / "ledger" / "install.md"
    handle = installed_by = None
    if path.is_file():
        try:
            for line in _unfenced_lines(path.read_text(encoding="utf-8", errors="replace")):
                m = re.match(r"^\s*-\s*actor handle:\s*([^\s(]+)", line)
                if m and handle is None and not m.group(1).startswith("<"):
                    handle = m.group(1)
                m = re.match(r"^\s*-\s*installed by:\s*(.+?)\s*$", line)
                if m and installed_by is None and not m.group(1).startswith("<"):
                    installed_by = m.group(1)
        except OSError:
            pass
    if handle:
        return handle
    if installed_by:
        return resolve_actor(installed_by, actors)
    return "any"


def trigger_owner(trig, actor, actors):
    """
    The trigger's owner as a canonical handle. A missing or blank owner means the
    library's own actor (`any` must be written explicitly); a name the actor
    records know resolves to its handle; anything else stands as written.
    """
    raw = trig.get("owner")
    if raw is None or not str(raw).strip():
        return actor
    return resolve_actor(raw, actors)


def machine_name():
    try:
        return os.uname().nodename or "unknown"
    except (AttributeError, OSError):
        return os.environ.get("COMPUTERNAME") or "unknown"


def read_grants(root):
    """
    Channel id -> True when the latest entry in durable/ledger/grants.md is a
    grant rather than a revocation. Entries are `## <channel id> (...)`
    headings followed by `- granted:` or `- revoked:` lines.
    """
    path = Path(root) / "durable" / "ledger" / "grants.md"
    latest = {}
    if not path.is_file():
        return latest
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return latest
    current = None
    for line in _unfenced_lines(text):
        m = re.match(r"^##\s+(\S+)", line)
        if m:
            current = m.group(1)
            latest[current] = {"granted": False, "revoked": False}
            continue
        if current is None:
            continue
        if re.match(r"^\s*-\s*granted:", line):
            latest[current]["granted"] = True
        elif re.match(r"^\s*-\s*revoked:", line):
            latest[current]["revoked"] = True
    return {cid: (v["granted"] and not v["revoked"]) for cid, v in latest.items()}


def resolve_channel(conn, scopes_by_name, scope_name, channel_name):
    """Walk own scope, parents, then user for a channel by name."""
    if not channel_name:
        return None
    for name in scope_chain(scopes_by_name, scope_name):
        row = conn.execute(
            "SELECT * FROM channels WHERE scope = ? AND name = ? ORDER BY revision DESC LIMIT 1",
            (name, channel_name)).fetchone()
        if row is not None:
            return dict(row)
    return None


def target_is_owner(target, owner, actors=()):
    """The channel target names the owner: literally, with an @, or via the owner's actor record."""
    if not target or not owner or owner == "any":
        return False
    t = str(target).strip().lower().lstrip("@")
    o = str(owner).strip().lower()
    return t == o or resolve_actor(t, actors) == resolve_actor(o, actors)


def resolve_send(channel, owner, grants, delivered_today, run_counts, actors=()):
    """
    The resolved send mode for one due entry: 'pull' when there is no channel,
    'auto' only when every condition holds (channel says auto, it is a dm to
    the owner, the grant is active, and neither cap is tripped), else 'draft'.
    Returns (mode, reason).
    """
    if channel is None:
        return "pull", "no channel"
    if (channel.get("send") or "draft") != "auto":
        return "draft", "channel is draft"
    if channel.get("kind") != "dm":
        return "draft", "auto is honoured only on a dm in this release"
    if not target_is_owner(channel.get("target"), owner, actors):
        return "draft", "channel target is not the trigger's owner"
    if not grants.get(channel["id"], False):
        return "draft", "no active grant in durable/ledger/grants.md"
    if delivered_today.get(channel["id"], 0) >= DAILY_SEND_CAP:
        return "draft", f"daily cap of {DAILY_SEND_CAP} reached"
    if run_counts.get(channel["id"], 0) >= RUN_SEND_CAP:
        return "draft", f"per-run cap of {RUN_SEND_CAP} reached"
    run_counts[channel["id"]] = run_counts.get(channel["id"], 0) + 1
    return "auto", "grant active"


# ---------------------------------------------------------------------------
# Due computation
# ---------------------------------------------------------------------------

def receipts_for(conn, trigger_id):
    rows = [dict(r) for r in conn.execute("SELECT * FROM fires WHERE trigger = ? ORDER BY at", (trigger_id,))]
    for r in rows:
        try:
            r["signals"] = json.loads(r.get("signals") or "[]")
        except ValueError:
            r["signals"] = []
    return rows


def signals_named(conn, name):
    return [dict(r) for r in conn.execute("SELECT * FROM signals WHERE name = ? ORDER BY at", (name,))]


def signal_by_id(conn, sid):
    row = conn.execute("SELECT * FROM signals WHERE id = ?", (sid,)).fetchone()
    return dict(row) if row else None


def is_blocked(occurrence, receipts, actor):
    """
    An occurrence is spent when anyone has written a result for it, or this
    actor has written any receipt for it (an own half-receipt means
    'attempted, outcome unknown' and is never blindly repeated).
    """
    for r in receipts:
        if r.get("occurrence") != occurrence:
            continue
        if r.get("phase") == "result":
            return True
        if r.get("actor") == actor:
            return True
    return False


def receipt_watermark(conn, trig, receipts):
    """The latest scheduled instant any receipt for this trigger refers to."""
    best = None
    for r in receipts:
        suffix = occurrence_suffix(r.get("occurrence") or "")
        if not suffix:
            continue
        if trig["when_mode"] == "on-signal":
            sig = signal_by_id(conn, suffix)
            inst = parse_iso(sig["at"]) if sig else parse_iso(suffix.split("-", 1)[0])
        else:
            inst = parse_iso(suffix)
        if inst is not None and (best is None or inst > best):
            best = inst
    return best


def window_open(trig, now):
    """
    An on-signal trigger's optional `when` window: a cron window is open when
    now matches the spec's day fields and hour; a once window opens at its
    instant. No window means always open. Returns (open, reason).
    """
    raw = json.loads(trig["raw"]) if trig.get("raw") else {}
    when = raw.get("when") if isinstance(raw.get("when"), dict) else {}
    mode = when.get("mode")
    if not when or mode in (None, "on-signal"):
        return True, None
    tz = load_zone(trig.get("tz"))
    if mode == "cron":
        try:
            cron = Cron(trig.get("when_spec") or "")
        except ValueError as e:
            return False, f"window spec unusable: {e}"
        if cron.matches_hour(now.astimezone(tz)):
            return True, None
        return False, f"outside the cron window '{cron.spec}' ({trig.get('tz') or 'UTC'})"
    if mode == "once":
        at = parse_iso(trig.get("when_at"), tz)
        if at is None:
            return False, "window instant unparseable"
        if now >= at:
            return True, None
        return False, f"window opens at {utc_iso(at)}"
    return False, f"unknown window mode '{mode}'"


def evaluate_trigger(conn, trig, now, actor, receipts=None):
    """
    Decide whether one trigger is due at `now`. Returns a dict:
      due:      the occurrence dict {occurrence, instant, signal} or None
      skipped:  elapsed occurrences (same shape) the misfire rule will not fire
      reason:   why it is or is not due, in words
      next_at:  the next scheduled instant (UTC), when knowable
    """
    if receipts is None:
        receipts = receipts_for(conn, trig["id"])
    result = {"due": None, "skipped": [], "reason": "", "next_at": None}
    tid = trig["id"]
    mode = trig.get("when_mode")
    tz = load_zone(trig.get("tz"))
    created = parse_iso(trig.get("created"))

    if trig.get("status") != "armed":
        result["reason"] = f"status is {trig.get('status') or 'unset'}, not armed"
        return result

    if mode == "once":
        at = parse_iso(trig.get("when_at"), tz)
        if at is None:
            result["reason"] = "when.at is missing or unparseable"
            return result
        occ = f"{tid}@{instant_str(at.astimezone(tz))}"
        result["next_at"] = at if at > now else None
        if at > now:
            result["reason"] = f"not yet: fires at {utc_iso(at)}"
        elif is_blocked(occ, receipts, actor):
            result["reason"] = "already receipted for its one occurrence"
        else:
            result["due"] = {"occurrence": occ, "instant": at, "signal": None}
            result["reason"] = f"once at {utc_iso(at)} has passed with no receipt"
        return result

    if mode == "cron":
        try:
            cron = Cron(trig.get("when_spec") or "")
        except ValueError as e:
            result["reason"] = f"cron spec unusable: {e}"
            return result
        result["next_at"] = cron_next_after(cron, tz, now)
        gen = cron_instants_before(cron, tz, now)
        latest = next(gen, None)
        if latest is None:
            result["reason"] = f"no scheduled instant in the last {CRON_LOOKBACK_DAYS} days"
            return result
        if created is not None and latest < created:
            result["reason"] = (f"most recent instant {utc_iso(latest)} predates the trigger "
                                f"(created {utc_iso(created)}); never backfilled")
            return result
        occ = f"{tid}@{instant_str(latest.astimezone(tz))}"
        if is_blocked(occ, receipts, actor):
            result["reason"] = f"most recent instant {utc_iso(latest)} is already receipted"
            return result
        result["due"] = {"occurrence": occ, "instant": latest, "signal": None}
        result["reason"] = f"scheduled instant {utc_iso(latest)} has passed with no receipt"
        watermark = receipt_watermark(conn, trig, receipts)
        floor = max([d for d in (watermark, created) if d is not None], default=None)
        for inst in gen:
            if floor is not None and inst <= floor:
                break
            if len(result["skipped"]) >= MAX_SKIPPED:
                break
            s_occ = f"{tid}@{instant_str(inst.astimezone(tz))}"
            if is_blocked(s_occ, receipts, actor):
                continue
            result["skipped"].append({"occurrence": s_occ, "instant": inst, "signal": None})
        return result

    if mode == "on-signal":
        name = trig.get("on_signal")
        if not name:
            result["reason"] = "on-signal trigger names no signal"
            return result
        opened, why = window_open(trig, now)
        if not opened:
            result["reason"] = why
            return result
        watermark = receipt_watermark(conn, trig, receipts)
        candidates = []
        for sig in signals_named(conn, name):
            at = parse_iso(sig.get("at"))
            if at is None or at > now:
                continue
            if created is not None and at < created:
                continue
            if watermark is not None and at <= watermark:
                continue
            occ = f"{tid}@{sig['id']}"
            if is_blocked(occ, receipts, actor):
                continue
            candidates.append({"occurrence": occ, "instant": at, "signal": sig})
        if not candidates:
            result["reason"] = f"no unreceipted signal named '{name}' since the last receipt"
            return result
        candidates.sort(key=lambda c: c["instant"])
        result["due"] = candidates[-1]
        result["skipped"] = list(reversed(candidates[:-1]))[:MAX_SKIPPED]
        result["reason"] = f"signal '{name}' ({candidates[-1]['signal']['id']}) has no receipt"
        return result

    result["reason"] = f"unknown schedule mode '{mode}'"
    return result


def loop_counts(conn, now):
    """Signal name -> result receipts in the last 24h for triggers armed on it."""
    since = utc_iso(now - timedelta(hours=24))
    until = utc_iso(now)
    counts = {}
    for r in conn.execute(
            """SELECT t.on_signal AS name, COUNT(*) AS n FROM fires f JOIN triggers t ON t.id = f.trigger
               WHERE f.phase = 'result' AND t.on_signal IS NOT NULL AND f.at >= ? AND f.at <= ?
               GROUP BY t.on_signal""", (since, until)):
        counts[r["name"]] = r["n"]
    return counts


def delivered_today(conn, scopes_by_name, now):
    """Channel id -> delivered result receipts on now's UTC date."""
    day = now.astimezone(UTC).strftime("%Y-%m-%d")
    counts = {}
    for r in conn.execute(
            """SELECT f.trigger AS trigger FROM fires f
               WHERE f.phase = 'result' AND f.status = 'delivered' AND substr(f.at, 1, 10) = ?""", (day,)):
        trig = conn.execute("SELECT scope, channel FROM triggers WHERE id = ?", (r["trigger"],)).fetchone()
        if trig is None or not trig["channel"]:
            continue
        ch = resolve_channel(conn, scopes_by_name, trig["scope"], trig["channel"])
        if ch is not None:
            counts[ch["id"]] = counts.get(ch["id"], 0) + 1
    return counts


def target_title(conn, trig):
    if trig.get("target_type") == "docket-entry" and trig.get("target_id"):
        row = conn.execute("SELECT title FROM items WHERE id = ?", (trig["target_id"],)).fetchone()
        return row["title"] if row else None
    return None


def build_entry(conn, scopes_by_name, trig, occ, grants, delivered, run_counts, receipts, loops,
                actor="any", actors=()):
    """One due-view entry, as the dispatcher consumes it."""
    channel = resolve_channel(conn, scopes_by_name, trig["scope"], trig.get("channel"))
    if trig.get("channel") and channel is None:
        warn(f"trigger {trig['id']}: channel '{trig['channel']}' not found in scope chain; degrading to pull")
    owner = trigger_owner(trig, actor, actors)
    mode, why = resolve_send(channel, owner, grants, delivered, run_counts, actors)
    others = [
        {"actor": r.get("actor"), "machine": r.get("machine"), "at": r.get("at")}
        for r in receipts
        if r.get("occurrence") == occ["occurrence"] and r.get("phase") == "intent"
    ]
    target = None
    if trig.get("target_type") or trig.get("target_id"):
        target = {"type": trig.get("target_type"), "scope": trig.get("target_scope"),
                  "id": trig.get("target_id"), "title": target_title(conn, trig)}
    suppressed = False
    suppressed_reason = None
    name = trig.get("on_signal")
    if name and loops.get(name, 0) >= LOOP_FIRES_PER_DAY:
        suppressed = True
        suppressed_reason = f"signal '{name}' fired {loops[name]} times in 24h; check for a loop"
    sig = occ.get("signal")
    return {
        "occurrence": occ["occurrence"],
        "trigger": trig["id"],
        "scope": trig["scope"],
        "mode": trig.get("when_mode"),
        "scheduled_at": utc_iso(occ["instant"]) if occ.get("instant") else None,
        "target": target,
        "assess": trig.get("assess"),
        "handler": {"kind": trig.get("handler_kind"), "weight": trig.get("weight"), "ref": trig.get("ref")},
        "handler_kind": trig.get("handler_kind"),
        "weight": trig.get("weight"),
        "ref": trig.get("ref"),
        "channel": channel["name"] if channel else trig.get("channel"),
        "channel_id": channel["id"] if channel else None,
        "channel_kind": channel["kind"] if channel else None,
        "channel_via": channel["via"] if channel else None,
        "channel_target": channel["target"] if channel else None,
        "resolved_send": mode,
        "send_reason": why,
        "owner": owner,
        "signal": ({"id": sig["id"], "name": sig["name"], "at": sig["at"], "payload": sig.get("payload")}
                   if sig else None),
        "other_intents": others,
        "suppressed": suppressed,
        "suppressed_reason": suppressed_reason,
        "skipped_occurrences": [],
    }


def compute_due(conn, root, scopes, now, actor, actors=None):
    """
    The due view: every armed trigger this actor may fire that is due at now.
    Returns (entries, excluded, flags): `excluded` lists the triggers that are due
    but belong to another actor, so a mismatch is never silent; `flags` names
    armed triggers whose owner no actor record knows.
    """
    if actors is None:
        actors = read_actors(root)
    scopes_by_name = {sc.name: sc for sc in scopes}
    grants = read_grants(root)
    delivered = delivered_today(conn, scopes_by_name, now)
    loops = loop_counts(conn, now)
    run_counts = {}
    entries, excluded, flags = [], [], []
    for row in conn.execute("SELECT * FROM triggers WHERE status = 'armed' ORDER BY created, id"):
        trig = dict(row)
        owner = trigger_owner(trig, actor, actors)
        if owner != "any" and not known_actor(owner, actors):
            flags.append(f"trigger {trig['id']} is owned by '{trig.get('owner')}', which is not a registered actor "
                         f"in durable/ledger/actors.md; nothing will fire it")
        receipts = receipts_for(conn, trig["id"])
        ev = evaluate_trigger(conn, trig, now, actor, receipts)
        if ev["due"] is None:
            continue
        if owner != "any" and owner != actor:
            excluded.append({"trigger": trig["id"], "scope": trig["scope"], "occurrence": ev["due"]["occurrence"],
                             "owner": owner, "owner_as_written": trig.get("owner"), "actor": actor})
            continue
        entry = build_entry(conn, scopes_by_name, trig, ev["due"], grants, delivered, run_counts, receipts, loops,
                            actor, actors)
        entry["skipped_occurrences"] = [s["occurrence"] for s in ev["skipped"]]
        entry["reason"] = ev["reason"]
        entries.append(entry)
    entries.sort(key=lambda e: (e.get("scheduled_at") or "", e["trigger"]))
    return entries, excluded, flags


def index_health(conn):
    """Flags the index raises: triggers armed on never-emitted names, orphaned targets."""
    notes = []
    for r in conn.execute("SELECT id, on_signal FROM triggers WHERE status = 'armed' AND on_signal IS NOT NULL"):
        if not conn.execute("SELECT 1 FROM signals WHERE name = ? LIMIT 1", (r["on_signal"],)).fetchone():
            notes.append(f"trigger {r['id']} is armed on '{r['on_signal']}', which nothing has ever emitted")
    for r in conn.execute(
            "SELECT id, target_id FROM triggers WHERE status = 'armed' AND target_type = 'docket-entry'"):
        if r["target_id"] and not conn.execute("SELECT 1 FROM items WHERE id = ?", (r["target_id"],)).fetchone():
            notes.append(f"trigger {r['id']} targets entry {r['target_id']}, which is not in any active docket file")
    return notes


# ---------------------------------------------------------------------------
# due.json: the text cache inside the library
# ---------------------------------------------------------------------------

def due_json_path(root):
    return Path(root) / "exfu" / "derived" / "due.json"


def write_due_json(root, scopes, conn, now, actor, entries):
    payload = {
        "generated_at": utc_iso(now),
        "generation": _int(meta_get(conn, "generation")),
        "actor": actor,
        "at": utc_iso(now),
        "source_hashes": current_source_hashes(scopes),
        "due": entries,
    }
    write_text_atomic(due_json_path(root), json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_due_json_or_refuse(root, scopes, actor):
    """
    The fallback when the index cannot be opened. Returns (entries, error).
    Refuses when the docket files no longer match the hashes the cache was
    computed from, or when the cache was computed for another actor.
    """
    path = due_json_path(root)
    if not path.is_file():
        return None, f"no {path.relative_to(root)} to fall back to"
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"due.json unreadable: {e}"
    cached = cache.get("source_hashes") or {}
    current = current_source_hashes(scopes)
    if cached != current:
        changed = sorted(set(cached) ^ set(current) | {k for k in cached if k in current and cached[k] != current[k]})
        return None, ("due.json is stale: docket files changed since it was generated "
                      f"({len(changed)}: {', '.join(changed[:5])}{' ...' if len(changed) > 5 else ''})")
    if actor and cache.get("actor") and cache["actor"] != actor:
        return None, f"due.json was computed for actor '{cache['actor']}', not '{actor}'"
    return cache.get("due") or [], None


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

def print_excluded(excluded, actor):
    if not excluded:
        return
    print()
    print(f"{len(excluded)} due but excluded (owned by another actor; actor is '{actor}'):")
    for x in excluded:
        as_written = x.get("owner_as_written")
        shown = f"'{x['owner']}'" if as_written in (None, x["owner"]) else f"'{as_written}' -> '{x['owner']}'"
        print(f"   {x['occurrence']}  scope: {x['scope']}  owned by {shown}")


def print_due_entries(entries, now, actor, header=True):
    if header:
        print(f"{len(entries)} due for actor '{actor}' at {utc_iso(now)}" + (":" if entries else "."))
    for i, e in enumerate(entries, 1):
        print()
        print(f"{i}. {e['occurrence']}")
        print(f"   scope: {e['scope']}  mode: {e['mode']}  owner: {e['owner']}  scheduled: {e.get('scheduled_at')}")
        t = e.get("target")
        if t:
            title = f' "{t.get("title")}"' if t.get("title") else ""
            print(f"   target: {t.get('type')} {t.get('id') or ''}{title}".rstrip())
        if e.get("signal"):
            print(f"   signal: {e['signal']['name']} ({e['signal']['id']}) at {e['signal']['at']}")
        if e.get("assess"):
            print(f"   assess: {e['assess']}")
        h = e.get("handler") or {}
        hbits = h.get("kind") or "?"
        if h.get("weight"):
            hbits += f" ({h['weight']})"
        if h.get("ref"):
            hbits += f" ref {h['ref']}"
        print(f"   handler: {hbits}   channel: {e.get('channel') or '(none)'} -> {e['resolved_send']} ({e.get('send_reason')})")
        if e.get("skipped_occurrences"):
            sk = e["skipped_occurrences"]
            print(f"   skipped occurrences ({len(sk)}, recorded at intent): {', '.join(sk[:3])}{' ...' if len(sk) > 3 else ''}")
        if e.get("other_intents"):
            names = ", ".join(str(o.get("actor")) for o in e["other_intents"])
            print(f"   claim: intent receipts also exist from: {names} (the lexically lower handle proceeds)")
        if e.get("suppressed"):
            print(f"   SUPPRESSED: {e.get('suppressed_reason')}")


def emit_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def prepare(root, trust_hints=False, quiet=True):
    """Open the index and refresh it. Returns (conn, scopes, stats, error)."""
    scopes = walk_scopes(root)
    conn, err = open_index(root)
    if conn is None:
        return None, scopes, None, err
    stats = rebuild(conn, root, scopes, trust_hints=trust_hints)
    if quiet:
        print(rebuild_summary(stats), file=sys.stderr)
    else:
        print(rebuild_summary(stats))
    return conn, scopes, stats, None


def cmd_rebuild(args):
    root = args.root
    conn, scopes, stats, err = prepare(root, trust_hints=args.trust_hints, quiet=False)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    print(f"Index at {index_path(root)}; {len(scopes)} scope(s) walked.")
    for note in index_health(conn):
        print(f"  flag: {note}")
    return 0


def fts_match_expression(conn, terms):
    """Use the terms as written if FTS5 accepts them, else quote each token."""
    raw = " ".join(terms).strip()
    try:
        conn.execute("SELECT 1 FROM items_fts WHERE items_fts MATCH ? LIMIT 0", (raw,)).fetchall()
        return raw
    except sqlite3.OperationalError:
        return " ".join('"' + t.replace('"', '""') + '"' for t in re.findall(r"\S+", raw))


def cmd_query(args):
    root = args.root
    conn, scopes, stats, err = prepare(root, trust_hints=args.trust_hints)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    expr = fts_match_expression(conn, args.terms)
    sql = """SELECT i.id, i.scope, i.kind, i.status, i.title, bm25(items_fts) AS rank,
                    snippet(items_fts, -1, '[', ']', ' ... ', 12) AS snip
             FROM items_fts JOIN items i ON i.id = items_fts.id
             WHERE items_fts MATCH ? AND i.deleted = 0"""
    params = [expr]
    if args.scope:
        sql += " AND i.scope = ?"
        params.append(args.scope)
    if args.kind:
        sql += " AND i.kind = ?"
        params.append(args.kind)
    if args.status:
        sql += " AND i.status = ?"
        params.append(args.status)
    sql += " ORDER BY rank LIMIT ?"
    params.append(args.limit)
    try:
        rows = [dict(r) for r in conn.execute(sql, params)]
    except sqlite3.OperationalError as e:
        print(f"Error: query failed: {e}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(rows)
        return 0
    if not rows:
        print(f"No entries match '{expr}'.")
        return 0
    print(f"{len(rows)} match(es) for '{expr}':")
    for r in rows:
        print(f"  {r['id']}  {r['scope']}  {r['kind']}  {r['status']}  {r['title'] or ''}")
        if r.get("snip"):
            print(f"      {r['snip']}")
    return 0


def resolve_now(at_text):
    if not at_text:
        return utc_now(), False
    dt = parse_iso(at_text)
    if dt is None:
        raise ValueError(f"cannot parse --at '{at_text}' (use ISO-8601, e.g. 2026-09-04T09:00:00Z)")
    return dt.astimezone(UTC), True


def cmd_due(args):
    root = args.root
    try:
        now, explicit_at = resolve_now(args.at)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    actors = read_actors(root)
    actor = resolve_actor(args.actor, actors) if args.actor else default_actor(root, actors)
    conn, scopes, stats, err = prepare(root, trust_hints=args.trust_hints)
    if conn is None:
        print(f"Index unavailable ({err}); falling back to exfu/derived/due.json.", file=sys.stderr)
        entries, cache_err = read_due_json_or_refuse(root, scopes, args.actor)
        if cache_err:
            print(f"Refusing: {cache_err}. Rebuild the index or run `due` where it is available.", file=sys.stderr)
            return 2
        if explicit_at:
            print("Note: due.json holds the view computed at its generated_at; --at cannot be honoured from the cache.",
                  file=sys.stderr)
        if args.json:
            emit_json(entries)
        else:
            print("(served from exfu/derived/due.json)")
            print_due_entries(entries, now, actor)
        return 0
    if actor == "any":
        print("Note: no actor in durable/ledger/actors.md or install.md; only triggers owned by 'any' are considered.",
              file=sys.stderr)
    entries, excluded, owner_flags = compute_due(conn, root, scopes, now, actor, actors)
    if not explicit_at:
        try:
            write_due_json(root, scopes, conn, now, actor, entries)
        except OSError as e:
            warn(f"could not write due.json: {e}")
    for note in index_health(conn) + owner_flags:
        print(f"flag: {note}", file=sys.stderr)
    for x in excluded:
        print(f"flag: excluded due trigger {x['trigger']} ({x['occurrence']}): owned by '{x['owner']}', "
              f"actor is '{actor}'", file=sys.stderr)
    if args.json:
        emit_json(entries)
    else:
        print_due_entries(entries, now, actor)
        print_excluded(excluded, actor)
    return 0


def cmd_explain(args):
    root = args.root
    try:
        now, _ = resolve_now(args.at)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    actors = read_actors(root)
    actor = resolve_actor(args.actor, actors) if args.actor else default_actor(root, actors)
    conn, scopes, stats, err = prepare(root)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    row = conn.execute("SELECT * FROM triggers WHERE id = ?", (args.trigger_id,)).fetchone()
    if row is None:
        print(f"Error: no trigger with id {args.trigger_id} in the index.", file=sys.stderr)
        return 1
    trig = dict(row)
    scopes_by_name = {sc.name: sc for sc in scopes}
    owner = trigger_owner(trig, actor, actors)
    raw_owner = trig.get("owner")
    if raw_owner is None or not str(raw_owner).strip():
        owner_shown = f"(none) -> {owner} (the library's actor)"
    elif str(raw_owner).strip() != owner:
        owner_shown = f"{str(raw_owner).strip()} -> {owner}"
    else:
        owner_shown = owner
    print(f"Trigger {trig['id']} in scope '{trig['scope']}'")
    print(f"  status: {trig.get('status')}  owner: {owner_shown}  mode: {trig.get('when_mode')}")
    if trig.get("when_mode") == "cron":
        print(f"  spec: {trig.get('when_spec')}  tz: {trig.get('tz') or 'UTC'}")
    elif trig.get("when_mode") == "once":
        print(f"  at: {trig.get('when_at')}  tz: {trig.get('tz') or 'UTC'}")
    if trig.get("on_signal"):
        print(f"  on: {trig['on_signal']}")
        if trig.get("when_spec") or trig.get("when_at"):
            print(f"  window: {trig.get('when_spec') or trig.get('when_at')} ({trig.get('tz') or 'UTC'})")
    if trig.get("target_type"):
        title = target_title(conn, trig)
        print(f"  target: {trig['target_type']} {trig.get('target_id') or ''}" + (f' "{title}"' if title else ""))
    print(f"  handler: {trig.get('handler_kind')} weight={trig.get('weight')} ref={trig.get('ref')}")
    channel = resolve_channel(conn, scopes_by_name, trig["scope"], trig.get("channel"))
    if trig.get("channel"):
        if channel:
            print(f"  channel: {trig['channel']} -> {channel['kind']} via {channel['via']} to {channel['target']} "
                  f"(send: {channel.get('send')}, declared in '{channel['scope']}', "
                  f"grant {'active' if read_grants(root).get(channel['id']) else 'absent'})")
        else:
            print(f"  channel: {trig['channel']} (not found in scope chain; degrades to pull)")
    else:
        print("  channel: (none; pull)")
    print(f"  assess: {trig.get('assess')}")
    print(f"  created: {trig.get('created')}  updated: {trig.get('updated')}  revision: {trig.get('revision')}")

    receipts = receipts_for(conn, trig["id"])
    ev = evaluate_trigger(conn, trig, now, actor, receipts)
    print()
    if ev["next_at"]:
        print(f"Next occurrence: {utc_iso(ev['next_at'])}")
    elif trig.get("when_mode") == "on-signal":
        recent = signals_named(conn, trig["on_signal"])
        print(f"Next occurrence: whenever '{trig['on_signal']}' is emitted ({len(recent)} in the index so far)")
    else:
        print("Next occurrence: none")
    print(f"Receipts ({len(receipts)}, most recent last):")
    for r in receipts[-10:]:
        extra = f" {r.get('status')}" if r.get("phase") == "result" else ""
        sigs = f" signals={','.join(r.get('signals') or [])}" if r.get("signals") else ""
        print(f"  {r.get('at')}  {r.get('phase')}{extra}  by {r.get('actor')}@{r.get('machine')}  {r.get('occurrence')}{sigs}")
    if not receipts:
        print("  (none)")
    print()
    if owner != "any" and not known_actor(owner, actors):
        print(f"Owner check: '{raw_owner}' is not a registered actor in durable/ledger/actors.md; nothing will fire it.")
    elif owner != "any" and owner != actor:
        print(f"Owner check: owned by '{owner}', so actor '{actor}' will not fire it.")
    if ev["due"]:
        print(f"Due at {utc_iso(now)}: yes -- {ev['reason']}")
        print(f"  occurrence: {ev['due']['occurrence']}")
        if ev["skipped"]:
            print(f"  would record {len(ev['skipped'])} elapsed occurrence(s) as skipped")
    else:
        print(f"Due at {utc_iso(now)}: no -- {ev['reason']}")
    for note in index_health(conn):
        if trig["id"] in note:
            print(f"flag: {note}")
    return 0


def cmd_fire(args):
    root = args.root
    conn, scopes, stats, err = prepare(root)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    row = conn.execute("SELECT * FROM triggers WHERE id = ?", (args.trigger_id,)).fetchone()
    if row is None:
        print(f"Error: no trigger with id {args.trigger_id} in the index.", file=sys.stderr)
        return 1
    trig = dict(row)
    now = utc_now()
    actors = read_actors(root)
    actor = resolve_actor(args.actor, actors) if args.actor else default_actor(root, actors)
    tz = load_zone(trig.get("tz"))
    occ = {"occurrence": f"{trig['id']}@{instant_str(now.astimezone(tz))}", "instant": now, "signal": None}
    scopes_by_name = {sc.name: sc for sc in scopes}
    receipts = receipts_for(conn, trig["id"])
    entry = build_entry(conn, scopes_by_name, trig, occ, read_grants(root),
                        delivered_today(conn, scopes_by_name, now), {}, receipts, loop_counts(conn, now),
                        actor, actors)
    entry["reason"] = "fired by hand with --now"
    if args.json:
        emit_json([entry])
    else:
        print("Immediate occurrence (nothing written; record it with `receipt`):")
        print_due_entries([entry], now, actor, header=False)
    return 0


def cmd_receipt(args):
    root = args.root
    conn, scopes, stats, err = prepare(root)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    occurrence = args.occurrence
    trig_id = occurrence.split("@", 1)[0]
    row = conn.execute("SELECT * FROM triggers WHERE id = ?", (trig_id,)).fetchone()
    if row is None:
        print(f"Error: occurrence '{occurrence}' names no trigger in the index.", file=sys.stderr)
        return 1
    trig = dict(row)
    scopes_by_name = {sc.name: sc for sc in scopes}
    scope = scopes_by_name.get(trig["scope"])
    if scope is None or not scope.docket.is_dir():
        print(f"Error: the docket folder for scope '{trig['scope']}' does not exist; nothing written.", file=sys.stderr)
        return 1
    if args.phase == "result" and not args.status:
        print("Error: a result receipt needs --status.", file=sys.stderr)
        return 1

    now = utc_now()
    actors = read_actors(root)
    actor = resolve_actor(args.actor, actors) if args.actor else default_actor(root, actors)
    machine = args.machine or machine_name()
    taken = set()
    written = []

    if args.phase == "intent":
        # Record the misfire rule at the moment of acting: elapsed occurrences
        # between the watermark and this one become skipped results.
        ev_now = None
        if trig.get("when_mode") == "on-signal":
            sig = signal_by_id(conn, occurrence_suffix(occurrence))
            ev_now = parse_iso(sig["at"]) if sig else None
        else:
            ev_now = parse_iso(occurrence_suffix(occurrence))
        if ev_now is not None:
            receipts = receipts_for(conn, trig["id"])
            ev = evaluate_trigger(conn, trig, ev_now, actor, receipts)
            if ev["due"] and ev["due"]["occurrence"] == occurrence:
                for s in ev["skipped"]:
                    written.append({
                        "id": new_id(conn, now, taken), "occurrence": s["occurrence"], "trigger": trig["id"],
                        "phase": "result", "status": "skipped", "actor": actor, "machine": machine,
                        "at": utc_iso(now), "signals": [], "idempotency_key": "", "reason": "misfire",
                    })
        written.append({
            "id": new_id(conn, now, taken), "occurrence": occurrence, "trigger": trig["id"],
            "phase": "intent", "actor": actor, "machine": machine, "at": utc_iso(now),
        })
    else:
        signals = [s.strip() for s in (args.signals or "").split(",") if s.strip()]
        written.append({
            "id": new_id(conn, now, taken), "occurrence": occurrence, "trigger": trig["id"],
            "phase": "result", "status": args.status, "actor": actor, "machine": machine,
            "at": utc_iso(now), "signals": signals, "idempotency_key": args.key or "",
        })

    fires_path = scope.docket / "fires.jsonl"
    try:
        append_jsonl(fires_path, written)
    except (OSError, RuntimeError) as e:
        print(f"Error: could not write {fires_path}: {e}", file=sys.stderr)
        return 1
    notes = [f"Wrote {len(written)} receipt(s) to {fires_path.relative_to(root)}."]

    emitted = []
    trigger_change = None
    if args.phase == "result":
        signals = written[-1]["signals"]
        if signals:
            sig_rows = [{
                "id": new_id(conn, now, taken), "name": name, "at": utc_iso(now), "scope": scope.name,
                "source": trig["id"], "payload": args.payload or "",
            } for name in signals]
            try:
                append_jsonl(scope.docket / "signals.jsonl", sig_rows)
            except (OSError, RuntimeError) as e:
                print(f"Error: could not write signals.jsonl: {e}", file=sys.stderr)
                return 1
            emitted = sig_rows
            notes.append(f"Emitted {len(sig_rows)} signal(s): {', '.join(signals)}.")

        # Trigger row maintenance: the only two writes the dispatcher makes.
        new_status = None
        if trig.get("when_mode") == "once" and args.status in ("delivered", "drafted"):
            new_status = "disarmed"
        else:
            results = [r for r in read_jsonl(fires_path)[0]
                       if r.get("trigger") == trig["id"] and r.get("phase") == "result"]
            results.sort(key=lambda r: r.get("at") or "")
            if len(results) >= 3 and all(r.get("status") == "failed" for r in results[-3:]):
                new_status = "paused"
        if new_status and trig.get("status") != new_status:
            trig_path = scope.docket / "triggers.jsonl"
            rows, bad = read_jsonl(trig_path)
            for r in rows:
                if r.get("id") == trig["id"]:
                    r["status"] = new_status
                    r["revision"] = _int(r.get("revision"), 1) + 1
                    r["updated"] = utc_iso(now)
                    trigger_change = new_status
            if trigger_change:
                try:
                    write_jsonl(trig_path, rows, bad)
                except (OSError, RuntimeError) as e:
                    print(f"Error: could not rewrite triggers.jsonl: {e}", file=sys.stderr)
                    return 1
                notes.append(f"Trigger {trig['id']} is now {trigger_change}.")

    # Refresh the index so the receipts are visible, then re-read the file
    # from disk for the claim rule.
    rebuild(conn, root, scopes)
    fresh, _ = read_jsonl(fires_path)
    others = [r for r in fresh
              if r.get("occurrence") == occurrence and r.get("phase") == "intent" and r.get("actor") != actor]

    if args.json:
        emit_json({"written": written, "signals": emitted, "trigger_status": trigger_change,
                   "other_intents": others})
        return 0
    for n in notes:
        print(n)
    if others:
        handles = sorted(str(o.get("actor")) for o in others)
        print(f"Claim: other actors also wrote intent for this occurrence: {', '.join(handles)}. "
              f"The lexically lowest handle proceeds"
              + (f"; that is you ('{actor}')." if actor < handles[0] else f"; that is '{handles[0]}', so record skipped."))
        for o in others:
            print(f"  {o.get('at')}  intent by {o.get('actor')}@{o.get('machine')}")
    else:
        print("Claim: no other actor has written intent for this occurrence.")
    return 0


# ---------------------------------------------------------------------------
# Compaction
# ---------------------------------------------------------------------------

def _rev(row):
    return _int(row.get("revision"), 0)


def _upd(row):
    return parse_iso(row.get("updated")) or datetime(1970, 1, 1, tzinfo=UTC)


def pick_winner(a, b):
    """Highest revision, then latest updated, then lexically lowest writer."""
    if _rev(a) != _rev(b):
        return a if _rev(a) > _rev(b) else b
    if _upd(a) != _upd(b):
        return a if _upd(a) > _upd(b) else b
    wa = str(a.get("writer") or "\uffff")  # a row without a writer never wins on the tiebreak
    wb = str(b.get("writer") or "\uffff")
    if wa != wb:
        return a if wa < wb else b
    return a


def fold_rows(main_rows, sibling_rows, mutable):
    by_id = {}
    order = []
    for r in list(main_rows) + list(sibling_rows):
        rid = r["id"]
        if rid not in by_id:
            by_id[rid] = r
            order.append(rid)
        elif mutable:
            by_id[rid] = pick_winner(by_id[rid], r)
    return [by_id[i] for i in order]


def compact_docket(conn, root, scope, now, dry_run):
    """Compact one docket in the documented order. Returns a counts dict."""
    docket = scope.docket
    counts = {"folded": 0, "archived": 0, "signalled": 0, "triggers_swept": 0,
              "signals_dropped": 0, "receipts_dropped": 0}
    archive_path = docket / "archive.jsonl"

    # 1. Fold conflicted copies.
    for sibling in sorted(docket.glob("*.jsonl")):
        m = CONFLICT_RE.match(sibling.name)
        if not m:
            continue
        stem = m.group("stem")
        if stem not in MUTABLE_STEMS and stem not in IMMUTABLE_STEMS:
            warn(f"{sibling}: conflicted copy of an unknown docket file; left alone")
            continue
        main = docket / f"{stem}.jsonl"
        main_rows, main_bad = read_jsonl(main)
        sib_rows, sib_bad = read_jsonl(sibling)
        merged = fold_rows(main_rows, sib_rows, mutable=stem in MUTABLE_STEMS)
        if not dry_run:
            write_jsonl(main, merged, main_bad + sib_bad)
            sibling.unlink()
        counts["folded"] += 1

    # 2. Archive closed entries older than the window.
    cutoff = now - timedelta(days=ARCHIVE_AFTER_DAYS)
    for fname, kind in ITEM_FILES.items():
        path = docket / fname
        if not path.is_file():
            continue
        rows, bad = read_jsonl(path)
        keep, move = [], []
        for r in rows:
            upd = parse_iso(r.get("updated"))
            if r.get("status") in ("done", "archived") and upd is not None and upd < cutoff:
                archived = dict(r)
                archived["kind"] = kind
                move.append(archived)
            else:
                keep.append(r)
        if move:
            if not dry_run:
                append_jsonl(archive_path, move)
                write_jsonl(path, keep, bad)
            counts["archived"] += len(move)

    # 3. Emit entry-completed signals for transitions the index saw.
    transitions = [dict(r) for r in conn.execute(
        "SELECT id FROM items WHERE scope = ? AND prev_status = 'open' AND status IN ('done','archived')",
        (scope.name,))]
    if transitions:
        existing_names = {r[0] for r in conn.execute("SELECT name FROM signals WHERE name LIKE 'entry-completed:%'")}
        for r in read_jsonl(docket / "signals.jsonl")[0]:
            existing_names.add(r.get("name"))
        taken = set()
        new_signals = []
        for t in transitions:
            name = f"entry-completed:{t['id']}"
            if name in existing_names:
                continue
            new_signals.append({"id": new_id(conn, now, taken), "name": name, "at": utc_iso(now),
                                "scope": scope.name, "source": "docket-compact", "payload": ""})
            existing_names.add(name)
        if new_signals and not dry_run:
            append_jsonl(docket / "signals.jsonl", new_signals)
        if not dry_run:
            for t in transitions:
                conn.execute("UPDATE items SET prev_status = NULL WHERE id = ?", (t["id"],))
            conn.commit()
        counts["signalled"] += len(new_signals)

    # 4. Sweep triggers whose target has been closed or missing for the window.
    trig_path = docket / "triggers.jsonl"
    if trig_path.is_file():
        rows, bad = read_jsonl(trig_path)
        archive_cache = {}

        def archived_entry(target_scope, target_id):
            sc_row = conn.execute("SELECT path FROM scopes WHERE name = ?", (target_scope,)).fetchone()
            if sc_row is None:
                return None
            key = sc_row["path"]
            if key not in archive_cache:
                p = Path(root) / key / "docket" / "archive.jsonl"
                archive_cache[key] = {r["id"]: r for r in read_jsonl(p)[0]}
            return archive_cache[key].get(target_id)

        keep, swept = [], []
        for r in rows:
            target = r.get("target") if isinstance(r.get("target"), dict) else {}
            if target.get("type") != "docket-entry" or not target.get("id"):
                keep.append(r)
                continue
            tid = target["id"]
            item = conn.execute("SELECT status, updated FROM items WHERE id = ?", (tid,)).fetchone()
            closed_since = None
            missing = False
            if item is not None:
                if item["status"] in ("done", "archived"):
                    closed_since = parse_iso(item["updated"])
            else:
                arch = archived_entry(target.get("scope") or scope.name, tid)
                if arch is not None:
                    closed_since = parse_iso(arch.get("updated"))
                else:
                    missing = True
            sweep = False
            if closed_since is not None and closed_since < now - timedelta(days=ORPHAN_AFTER_DAYS):
                sweep = True
            if missing:
                orphan_row = conn.execute("SELECT orphan_since FROM triggers WHERE id = ?", (r["id"],)).fetchone()
                since = parse_iso(orphan_row["orphan_since"]) if orphan_row and orphan_row["orphan_since"] else None
                if since is None:
                    if not dry_run:
                        conn.execute("UPDATE triggers SET orphan_since = ? WHERE id = ?", (utc_iso(now), r["id"]))
                elif since < now - timedelta(days=ORPHAN_AFTER_DAYS):
                    sweep = True
            elif not dry_run:
                conn.execute("UPDATE triggers SET orphan_since = NULL WHERE id = ?", (r["id"],))
            if sweep:
                s = dict(r)
                s["status"] = "disarmed"
                s["revision"] = _rev(r) + 1
                s["updated"] = utc_iso(now)
                s["kind"] = "trigger"
                swept.append(s)
            else:
                keep.append(r)
        if swept and not dry_run:
            append_jsonl(archive_path, swept)
            write_jsonl(trig_path, keep, bad)
        if not dry_run:
            conn.commit()
        counts["triggers_swept"] += len(swept)

    # 5. Retention: signals and receipts.
    for fname, days, key in (("signals.jsonl", SIGNAL_RETENTION_DAYS, "signals_dropped"),
                             ("fires.jsonl", RECEIPT_RETENTION_DAYS, "receipts_dropped")):
        path = docket / fname
        if not path.is_file():
            continue
        rows, bad = read_jsonl(path)
        limit = now - timedelta(days=days)
        keep = []
        dropped = 0
        for r in rows:
            at = parse_iso(r.get("at"))
            if at is not None and at < limit:
                dropped += 1
            else:
                keep.append(r)
        if dropped:
            if not dry_run:
                write_jsonl(path, keep, bad)
            counts[key] += dropped
    return counts


def cmd_compact(args):
    root = args.root
    conn, scopes, stats, err = prepare(root, trust_hints=args.trust_hints)
    if conn is None:
        print(f"Error: cannot open the index at {index_path(root)}: {err}", file=sys.stderr)
        return 1
    now = utc_now()
    totals = {}
    dockets = 0
    for sc in scopes:
        if not sc.docket.is_dir():
            continue
        dockets += 1
        try:
            counts = compact_docket(conn, root, sc, now, args.dry_run)
        except (OSError, RuntimeError) as e:
            print(f"Error: compaction of '{sc.name}' failed: {e}", file=sys.stderr)
            return 1
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
        print(f"{sc.name}: folded {counts['folded']}, archived {counts['archived']}, "
              f"signalled {counts['signalled']}, triggers swept {counts['triggers_swept']}, "
              f"signals dropped {counts['signals_dropped']}, receipts dropped {counts['receipts_dropped']}")
    if not args.dry_run:
        rebuild(conn, root, scopes)
    label = "would be " if args.dry_run else ""
    print(f"{dockets} docket(s) compacted{' (dry run)' if args.dry_run else ''}: "
          f"{totals.get('folded', 0)} {label}folded, {totals.get('archived', 0)} {label}archived, "
          f"{totals.get('signalled', 0)} {label}signalled, {totals.get('triggers_swept', 0)} triggers {label}swept, "
          f"{totals.get('signals_dropped', 0)} signals and {totals.get('receipts_dropped', 0)} receipts {label}dropped.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Per-machine index over the library's dockets: search, the due view, receipts, compaction")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("rebuild", help="Incrementally rebuild the index")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("--trust-hints", action="store_true",
                   help="Skip files whose mtime and size are unchanged without hashing them")

    p = sub.add_parser("query", help="Full-text search over docket entries")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("terms", nargs="+", help="Search terms (FTS5 syntax accepted)")
    p.add_argument("--scope")
    p.add_argument("--kind", choices=("todo", "reminder", "agent-backlog"))
    p.add_argument("--status", choices=ITEM_STATUSES)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.add_argument("--trust-hints", action="store_true")

    p = sub.add_parser("due", help="Which armed triggers are due (the dry run)")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("--at", help="Evaluate as of this ISO-8601 instant (default: now)")
    p.add_argument("--actor", help="Actor handle (default: durable/ledger/install.md, else 'any')")
    p.add_argument("--json", action="store_true")
    p.add_argument("--trust-hints", action="store_true")

    p = sub.add_parser("explain", help="Why one trigger is or is not due")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("trigger_id")
    p.add_argument("--at")
    p.add_argument("--actor")

    p = sub.add_parser("fire", help="The due entry for an immediate occurrence (writes nothing)")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("trigger_id")
    p.add_argument("--now", action="store_true", required=True, help="Fire as of now")
    p.add_argument("--actor")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("receipt", help="Append an intent or result receipt")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("occurrence", help="<trigger id>@<instant or signal id>")
    p.add_argument("phase", choices=("intent", "result"))
    p.add_argument("--status", choices=RESULT_STATUSES)
    p.add_argument("--signals", help="Comma-separated signal names the handler reported")
    p.add_argument("--key", help="Idempotency key from the connector, if any")
    p.add_argument("--payload", help="Payload written on each emitted signal")
    p.add_argument("--actor")
    p.add_argument("--machine")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("compact", help="Fold, archive, signal, sweep every docket")
    p.add_argument("root", help="Path to the substrate root folder")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--trust-hints", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    args.root = root
    handlers = {
        "rebuild": cmd_rebuild,
        "query": cmd_query,
        "due": cmd_due,
        "explain": cmd_explain,
        "fire": cmd_fire,
        "receipt": cmd_receipt,
        "compact": cmd_compact,
    }
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
