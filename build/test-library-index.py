#!/usr/bin/env python3
"""
Self-test for scheduled-tasks/library-index/index.py

Builds a scratch library under $TMPDIR (a user scope with install.md and a
granted dm channel, one client scope with entries, a cron trigger in
Europe/London, a once trigger, an on-signal trigger, a broadcast channel),
then drives the tool through its subcommands and asserts what each one
should have done. The index is kept outside the scratch root; the test
checks that nothing binary ever appears inside it.

Usage:
    python3 build/test-library-index.py

Exit code 0 when every assertion passes. Not shipped; build/ is tooling.
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "src" / "shared" / "scheduled-tasks" / "library-index" / "index.py"

CRON_ID = "20260903T120000Z-TRGCRON001"
ONCE_ID = "20260903T120100Z-TRGONCE001"
SIG_ID = "20260901T120200Z-TRGSIGN001"
ALIAS_ID = "20260905T190000Z-TRGALIAS01"
NOOWNER_ID = "20260905T190100Z-TRGNOOWN01"
STRANGER_ID = "20260905T190200Z-TRGSTRNG01"
T1, T2, T3, T4, T5 = (f"20260901T10000{i}Z-ITEM00000{i}" for i in range(1, 6))
R1 = "20260901T100100Z-REMIND0001"
CH_DM = "20260901T110000Z-CHANNEL0DM"
CH_TEAM = "20260901T110100Z-CHANNEL0TM"

checks = 0


def ok(condition, what):
    global checks
    checks += 1
    if not condition:
        print(f"FAIL: {what}")
        sys.exit(1)
    print(f"  ok: {what}")


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def read_rows(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def scope_md(path, name, parent):
    path.mkdir(parents=True, exist_ok=True)
    (path / "scope.md").write_text(
        f"---\nname: {name}\npurpose: test scope\nparent: {parent}\nexfu: 20260903-1743\n---\n", encoding="utf-8")


def build_library(lib):
    scope_md(lib / "user", "al", "none")
    scope_md(lib / "scopes" / "acme", "acme", "root")
    ledger = lib / "durable" / "ledger"
    ledger.mkdir(parents=True)
    (ledger / "install.md").write_text(
        "# Install\n\n- created: 2026-09-01\n- plugin: exfu-agent-library-solo 0.11.0\n"
        "- surface: Claude Code\n- storage: local\n- conventions at install: 20260903-1743\n"
        "- installed by: al\n", encoding="utf-8")
    (ledger / "grants.md").write_text(
        "# Grants\n\n```markdown\n## <channel id> (<channel name>, <scope>)\n- granted: <ISO date>\n```\n\n"
        f"## {CH_DM} (slack-dm, al)\n- granted: 2026-09-01\n- by: al (Claude Code), plugin 0.11.0\n"
        "- send: auto\n- notes: yes, message me directly\n", encoding="utf-8")

    env = {"created": "2026-09-01T10:00:00Z", "updated": "2026-09-01T10:00:00Z", "revision": 1}
    jsonl(lib / "user" / "docket" / "channels.jsonl", [
        {"id": CH_DM, "name": "slack-dm", "kind": "dm", "via": "slack", "target": "@al", "send": "auto", **env},
    ])
    jsonl(lib / "user" / "docket" / "todo.jsonl", [
        {"id": "20260901T100000Z-USERITEM01", "title": "Renew passport", "notes": "", "agent_notes": "",
         "status": "open", "keywords": ["passport"], **env},
    ])
    acme = lib / "scopes" / "acme" / "docket"
    jsonl(acme / "todo.jsonl", [
        {"id": T1, "title": "Chase the Acme security questionnaire", "notes": "Sent 20 Aug, Priya said end of month.",
         "agent_notes": "Only surface after the Acme call.", "status": "open",
         "keywords": ["acme", "security questionnaire", "priya"], **env},
        {"id": T2, "title": "Book the Acme kickoff room", "notes": "Second floor", "agent_notes": "",
         "status": "open", "keywords": ["acme", "kickoff"], **env},
        {"id": T3, "title": "Throwaway entry", "notes": "", "agent_notes": "", "status": "open",
         "keywords": [], **env},
        {"id": T4, "title": "Send the Acme invoice", "notes": "", "agent_notes": "", "status": "open",
         "keywords": ["invoice"], **env},
    ])
    jsonl(acme / "reminders.jsonl", [
        {"id": R1, "title": "Ping Priya", "notes": "", "agent_notes": "", "status": "open",
         "keywords": ["priya"], **env},
    ])
    jsonl(acme / "channels.jsonl", [
        {"id": CH_TEAM, "name": "acme-team", "kind": "broadcast", "via": "slack", "target": "#acme-project",
         "send": "draft", **env},
    ])
    jsonl(acme / "triggers.jsonl", [
        {"id": CRON_ID, "target": {"type": "docket-entry", "scope": "acme", "id": T1},
         "assess": "Surface the questionnaire chase on weekday mornings.",
         "when": {"mode": "cron", "spec": "0 9 * * 1-5", "tz": "Europe/London"}, "on": None,
         "handler": {"kind": "agent", "weight": "light", "ref": None}, "channel": "slack-dm", "owner": "al",
         "status": "armed", "created": "2026-09-03T12:00:00Z", "updated": "2026-09-03T12:00:00Z", "revision": 1},
        {"id": ONCE_ID, "target": None,
         "assess": "Check email for the Acme reply and report acme-reply-seen if there is one.",
         "when": {"mode": "once", "at": "2026-09-05T10:00:00Z", "tz": "UTC"}, "on": None,
         "handler": {"kind": "agent", "weight": "light", "ref": None}, "channel": None, "owner": "al",
         "status": "armed", "created": "2026-09-03T12:01:00Z", "updated": "2026-09-03T12:01:00Z", "revision": 1},
        {"id": SIG_ID, "target": {"type": "docket-entry", "scope": "acme", "id": R1},
         "assess": "On the Acme reply, draft the follow-up for the team.",
         "when": None, "on": "acme-reply-seen",
         "handler": {"kind": "deliver", "weight": "light", "ref": None}, "channel": "acme-team", "owner": "any",
         "status": "armed", "created": "2026-09-01T12:02:00Z", "updated": "2026-09-01T12:02:00Z", "revision": 1},
    ])


class Runner:
    def __init__(self, lib, derived):
        self.lib = lib
        self.derived = derived

    def run(self, *args, derived=None, expect=0):
        env = dict(os.environ)
        env["EXFU_DERIVED_DIR"] = str(derived or self.derived)
        cmd = [sys.executable, str(TOOL), args[0], str(self.lib), *args[1:]]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if expect is not None and proc.returncode != expect:
            print(f"FAIL: {' '.join(args)} exited {proc.returncode} (expected {expect})")
            print("stdout:", proc.stdout)
            print("stderr:", proc.stderr)
            sys.exit(1)
        return proc

    def run_json(self, *args, **kw):
        proc = self.run(*args, "--json", **kw)
        try:
            return json.loads(proc.stdout), proc
        except json.JSONDecodeError:
            print(f"FAIL: {' '.join(args)} did not print JSON:\n{proc.stdout}\n{proc.stderr}")
            sys.exit(1)


def stats_of(stdout):
    import re
    m = re.search(r"(\d+) files scanned, (\d+) unchanged, (\d+) changed; (\d+) rows upserted, (\d+) deleted", stdout)
    if not m:
        print(f"FAIL: no rebuild summary in:\n{stdout}")
        sys.exit(1)
    return tuple(int(x) for x in m.groups())


def main():
    scratch = Path(tempfile.mkdtemp(prefix="exfu-library-index-test-"))
    lib = scratch / "library"
    derived = scratch / "derived"
    lib.mkdir()
    build_library(lib)
    r = Runner(lib, derived)
    acme = lib / "scopes" / "acme" / "docket"
    print(f"scratch library: {lib}")

    # -- rebuild ------------------------------------------------------------
    print("rebuild")
    scanned, unchanged, changed, upserted, deleted = stats_of(r.run("rebuild").stdout)
    ok(scanned == 6 and changed == 6, f"first rebuild scanned {scanned} files, {changed} changed")
    ok(upserted == 11, f"first rebuild upserted {upserted} rows")
    _, _, changed, upserted, deleted = stats_of(r.run("rebuild").stdout)
    ok(changed == 0 and upserted == 0 and deleted == 0, "second rebuild changes nothing")
    _, unchanged, changed, _, _ = stats_of(r.run("rebuild", "--trust-hints").stdout)
    ok(changed == 0 and unchanged == 6, "trusted hints skip every file")

    rows = read_rows(acme / "todo.jsonl")
    for row in rows:
        if row["id"] == T2:
            row["notes"] = "Second floor, the big one"
            row["updated"] = "2026-09-02T10:00:00Z"
            row["revision"] = 2
    jsonl(acme / "todo.jsonl", rows)
    _, _, changed, upserted, deleted = stats_of(r.run("rebuild").stdout)
    ok(changed == 1 and upserted == 1 and deleted == 0, "editing one entry's notes upserts exactly 1 row")

    jsonl(acme / "todo.jsonl", [row for row in rows if row["id"] != T3])
    _, _, changed, upserted, deleted = stats_of(r.run("rebuild").stdout)
    ok(deleted == 1 and upserted == 0, "deleting an entry deletes exactly 1 row")
    db_files = list(derived.glob("*/library.sqlite"))
    ok(len(db_files) == 1, "one library.sqlite in the derived dir")
    conn = sqlite3.connect(str(db_files[0]))
    ok(conn.execute("SELECT COUNT(*) FROM items WHERE id = ?", (T3,)).fetchone()[0] == 0, "deleted entry is gone from items")
    ok(conn.execute("SELECT COUNT(*) FROM items_fts WHERE id = ?", (T3,)).fetchone()[0] == 0, "deleted entry is gone from items_fts")
    conn.close()

    # -- query --------------------------------------------------------------
    print("query")
    hits, _ = r.run_json("query", "questionnaire")
    ok([h["id"] for h in hits] == [T1], "query finds the entry by keyword")
    hits, _ = r.run_json("query", "priya", "--kind", "reminder")
    ok([h["id"] for h in hits] == [R1], "query filters by kind")
    hits, _ = r.run_json("query", "acme", "--scope", "acme", "--status", "open")
    ok({h["id"] for h in hits} == {T1, T2, T4}, "query filters by scope and status")

    # -- due ----------------------------------------------------------------
    print("due")
    due, _ = r.run_json("due", "--at", "2026-09-04T07:00:00Z")
    ok([e["trigger"] for e in due] == [], "nothing due before 9am London on the first weekday")
    due, _ = r.run_json("due", "--at", "2026-09-04T08:30:00Z")
    ok([e["trigger"] for e in due] == [CRON_ID], "cron trigger due after 9am London")
    cron_occ = f"{CRON_ID}@2026-09-04T09:00+01:00"
    ok(due[0]["occurrence"] == cron_occ, "cron occurrence carries the London instant")
    ok(due[0]["resolved_send"] == "auto" and due[0]["channel"] == "slack-dm", "granted dm to owner resolves to auto")
    ok(due[0]["target"]["title"].startswith("Chase the Acme"), "target title resolved from the index")
    ok(due[0]["skipped_occurrences"] == [], "no skipped occurrences on the first fire after creation")
    due, _ = r.run_json("due", "--at", "2026-09-05T09:59:00Z")
    ok(ONCE_ID not in [e["trigger"] for e in due], "once trigger not due one minute early")
    due, _ = r.run_json("due", "--at", "2026-09-05T10:00:00Z")
    once = [e for e in due if e["trigger"] == ONCE_ID]
    once_occ = f"{ONCE_ID}@2026-09-05T10:00+00:00"
    ok(len(once) == 1 and once[0]["occurrence"] == once_occ, "once trigger due at its instant")
    ok(once[0]["resolved_send"] == "pull", "no channel resolves to pull")
    due, _ = r.run_json("due", "--at", "2026-09-05T10:00:00Z", "--actor", "sam")
    ok([e["trigger"] for e in due] == [], "another actor sees none of al's triggers")

    # -- receipts on the cron trigger ---------------------------------------
    print("receipt (cron)")
    r.run("receipt", cron_occ, "intent", "--actor", "al", "--machine", "test-box")
    r.run("receipt", cron_occ, "result", "--status", "delivered", "--actor", "al", "--machine", "test-box")
    due, _ = r.run_json("due", "--at", "2026-09-04T08:30:00Z")
    ok(CRON_ID not in [e["trigger"] for e in due], "receipted cron occurrence is no longer due")
    due, _ = r.run_json("due", "--at", "2026-09-08T09:00:00Z")
    cron = [e for e in due if e["trigger"] == CRON_ID]
    # 2026-09-04 is a Friday; the 5th and 6th are the weekend; the 7th is Monday.
    ok(len(cron) == 1 and cron[0]["occurrence"] == f"{CRON_ID}@2026-09-08T09:00+01:00",
       "Tuesday's occurrence is the one that fires")
    ok(cron[0]["skipped_occurrences"] == [f"{CRON_ID}@2026-09-07T09:00+01:00"],
       "Monday's elapsed occurrence is listed as skipped, the weekend is not")
    r.run("receipt", cron[0]["occurrence"], "intent", "--actor", "al", "--machine", "test-box")
    fires = read_rows(acme / "fires.jsonl")
    skipped = [f for f in fires if f.get("status") == "skipped"]
    ok(len(skipped) == 1 and skipped[0]["occurrence"] == f"{CRON_ID}@2026-09-07T09:00+01:00",
       "intent receipt records the skipped occurrence")
    r.run("receipt", cron[0]["occurrence"], "result", "--status", "delivered", "--actor", "al", "--machine", "test-box")
    ok(read_rows(acme / "triggers.jsonl")[0]["status"] == "armed", "cron trigger stays armed after firing")

    # -- receipts on the once trigger, and the signal it emits --------------
    print("receipt (once)")
    proc = r.run("receipt", once_occ, "intent", "--actor", "al", "--machine", "test-box")
    ok("no other actor" in proc.stdout, "intent receipt reports no competing claim")
    r.run("receipt", once_occ, "result", "--status", "delivered", "--signals", "acme-reply-seen",
          "--actor", "al", "--machine", "test-box")
    trig_rows = {t["id"]: t for t in read_rows(acme / "triggers.jsonl")}
    ok(trig_rows[ONCE_ID]["status"] == "disarmed" and trig_rows[ONCE_ID]["revision"] == 2,
       "once trigger disarmed with revision bumped")
    ok(trig_rows[CRON_ID]["revision"] == 1, "other trigger rows untouched")
    signals = read_rows(acme / "signals.jsonl")
    seen = [s for s in signals if s["name"] == "acme-reply-seen"]
    ok(len(seen) == 1 and seen[0]["source"] == ONCE_ID and seen[0]["scope"] == "acme", "signal emitted into signals.jsonl")
    due, _ = r.run_json("due", "--at", "2026-09-05T10:00:00Z")
    ok(ONCE_ID not in [e["trigger"] for e in due], "disarmed once trigger is not due")

    # -- the on-signal trigger fires once per signal --------------------------
    print("on-signal")
    due, _ = r.run_json("due")
    sig = [e for e in due if e["trigger"] == SIG_ID]
    ok(len(sig) == 1 and sig[0]["occurrence"] == f"{SIG_ID}@{seen[0]['id']}", "on-signal trigger due after the signal")
    ok(sig[0]["resolved_send"] == "draft" and sig[0]["channel"] == "acme-team", "broadcast channel resolves to draft")
    ok(sig[0]["signal"]["name"] == "acme-reply-seen", "due entry names the signal")
    r.run("receipt", sig[0]["occurrence"], "intent", "--actor", "al", "--machine", "test-box")
    r.run("receipt", sig[0]["occurrence"], "result", "--status", "drafted", "--actor", "al", "--machine", "test-box")
    due, _ = r.run_json("due")
    ok(SIG_ID not in [e["trigger"] for e in due], "on-signal trigger fires only once per signal")
    proc = r.run("receipt", sig[0]["occurrence"], "intent", "--actor", "sam", "--machine", "other-box")
    ok("al" in proc.stdout and "Claim" in proc.stdout, "a second actor's intent sees the first actor's claim")

    # -- explain and fire -----------------------------------------------------
    print("explain / fire")
    proc = r.run("explain", CRON_ID, "--at", "2026-09-04T08:30:00Z")
    ok("Due at 2026-09-04T08:30:00Z: no" in proc.stdout and "already receipted" in proc.stdout,
       "explain says why the cron trigger is not due")
    proc = r.run("explain", ONCE_ID)
    ok("status is disarmed" in proc.stdout, "explain says the once trigger is disarmed")
    before = (acme / "fires.jsonl").read_bytes()
    fired, _ = r.run_json("fire", CRON_ID, "--now")
    ok(len(fired) == 1 and fired[0]["occurrence"].startswith(CRON_ID + "@"), "fire --now prints an immediate occurrence")
    ok((acme / "fires.jsonl").read_bytes() == before, "fire --now wrote nothing")

    # -- due.json cache and the stale check -----------------------------------
    print("due.json")
    r.run("due")  # refresh the cache after the receipts written above
    due_json = lib / "exfu" / "derived" / "due.json"
    ok(due_json.is_file(), "due.json written inside the library")
    cache = json.loads(due_json.read_text(encoding="utf-8"))
    ok(set(cache) >= {"generated_at", "generation", "source_hashes", "due"}, "due.json carries generation and source hashes")
    blocker = scratch / "blocker"
    blocker.write_text("not a directory\n", encoding="utf-8")
    unusable = blocker / "derived"
    proc = r.run("due", "--json", derived=unusable, expect=0)
    ok("falling back" in proc.stderr and json.loads(proc.stdout) == cache["due"], "unopenable index serves due.json")
    jsonl(acme / "reminders.jsonl", read_rows(acme / "reminders.jsonl") + [
        {"id": "20260903T150000Z-REMIND0002", "title": "New since the cache", "notes": "", "agent_notes": "",
         "status": "open", "keywords": [], "created": "2026-09-03T15:00:00Z", "updated": "2026-09-03T15:00:00Z",
         "revision": 1}])
    proc = r.run("due", "--json", derived=unusable, expect=2)
    ok("stale" in proc.stderr, "stale due.json is refused once a docket file changes")

    # -- compact ----------------------------------------------------------------
    print("compact")
    rows = read_rows(acme / "todo.jsonl")
    for row in rows:
        if row["id"] == T4:
            row["status"] = "done"
            row["updated"] = "2026-07-01T09:00:00Z"
            row["revision"] = 2
    jsonl(acme / "todo.jsonl", rows)
    conflicted = [
        {**next(x for x in rows if x["id"] == T1), "title": "Chase the Acme security questionnaire (Sam's edit)",
         "revision": 2, "updated": "2026-09-03T11:00:00Z", "writer": "sam"},
        {"id": T5, "title": "Sam's new entry", "notes": "", "agent_notes": "", "status": "open", "keywords": [],
         "created": "2026-09-03T11:05:00Z", "updated": "2026-09-03T11:05:00Z", "revision": 1, "writer": "sam"},
    ]
    sibling = acme / "todo (Sam's conflicted copy 2026-09-03).jsonl"
    jsonl(sibling, conflicted)
    proc = r.run("compact", "--dry-run")
    ok(sibling.exists() and "acme: folded 1, archived 1, signalled 1" in proc.stdout, "dry run reports without writing")
    proc = r.run("compact")
    ok("acme: folded 1, archived 1, signalled 1" in proc.stdout, "compact reports fold, archive and signal counts")
    ok(not sibling.exists(), "conflicted copy removed after folding")
    todo = {t["id"]: t for t in read_rows(acme / "todo.jsonl")}
    ok(todo[T1]["revision"] == 2 and "Sam's edit" in todo[T1]["title"], "fold keeps the higher revision")
    ok(T5 in todo, "fold unions the sibling's new row")
    ok(T4 not in todo, "old done entry left the active file")
    archive = read_rows(acme / "archive.jsonl")
    ok(any(a["id"] == T4 and a["kind"] == "todo" for a in archive), "old done entry archived with its kind")
    names = [s["name"] for s in read_rows(acme / "signals.jsonl")]
    ok(names.count(f"entry-completed:{T4}") == 1, "entry-completed signal emitted for the closed entry")
    proc = r.run("compact")
    names = [s["name"] for s in read_rows(acme / "signals.jsonl")]
    ok(names.count(f"entry-completed:{T4}") == 1 and "signalled 0" in proc.stdout, "second compaction emits nothing new")

    # -- actors: aliases, the self default, and visible exclusions ------------------
    print("actors")
    ledger = lib / "durable" / "ledger"
    (ledger / "install.md").write_text(
        "# Install\n\n- created: 2026-09-01\n- plugin: exfu-agent-library-solo 0.11.2\n"
        "- installed by: Alastair Brayne\n", encoding="utf-8")
    (ledger / "actors.md").write_text(
        "# Actors\n\n```markdown\n## <handle>\n- aliases: <other names>\n```\n\n"
        "## al\n- display: Alastair Brayne\n- aliases: Alastair, Al\n- slack: U0B0C019474\n"
        "- recorded: 2026-09-05T20:00:00Z by al (Claude Code), plugin 0.11.2\n", encoding="utf-8")
    env2 = {"created": "2026-09-05T19:00:00Z", "updated": "2026-09-05T19:00:00Z", "revision": 1}
    jsonl(lib / "user" / "docket" / "channels.jsonl", [
        {"id": CH_DM, "name": "slack-dm", "kind": "dm", "via": "slack", "target": "U0B0C019474", "send": "auto", **env2},
    ])
    when = {"mode": "once", "at": "2026-09-06T09:00:00Z", "tz": "UTC"}
    handler = {"kind": "agent", "weight": "light", "ref": None}
    jsonl(lib / "user" / "docket" / "triggers.jsonl", [
        {"id": ALIAS_ID, "target": None, "assess": "Owned under a display name.", "when": when, "on": None,
         "handler": handler, "channel": "slack-dm", "owner": "Alastair", "status": "armed", **env2},
        {"id": NOOWNER_ID, "target": None, "assess": "No owner key at all.", "when": when, "on": None,
         "handler": handler, "channel": None, "status": "armed", **env2},
        {"id": STRANGER_ID, "target": None, "assess": "Owned by someone this library does not know.", "when": when,
         "on": None, "handler": handler, "channel": None, "owner": "sam", "status": "armed", **env2},
    ])
    due, proc = r.run_json("due", "--at", "2026-09-06T09:00:00Z")
    ids = [e["trigger"] for e in due]
    ok(ALIAS_ID in ids, "a trigger owned under an alias fires for the canonical actor")
    ok(NOOWNER_ID in ids, "a trigger with no owner fires for the library's own actor")
    ok(STRANGER_ID not in ids, "another actor's trigger is still excluded")
    alias = next(e for e in due if e["trigger"] == ALIAS_ID)
    ok(alias["owner"] == "al", "the due view reports the canonical handle as owner")
    ok(alias["resolved_send"] == "auto", "a dm whose target is the owner's slack id resolves to auto")
    ok("excluded" in proc.stderr and STRANGER_ID in proc.stderr and "'sam'" in proc.stderr,
       "--json reports the due trigger it excluded, naming its owner")
    ok("not a registered actor" in proc.stderr, "--json flags an owner that resolves to no known actor")
    proc = r.run("due", "--at", "2026-09-06T09:00:00Z")
    ok("1 due but excluded" in proc.stdout and "owned by 'sam'" in proc.stdout and "actor is 'al'" in proc.stdout,
       "the text due view says what it excluded and why")
    proc = r.run("explain", ALIAS_ID, "--at", "2026-09-06T09:00:00Z")
    ok("owner: Alastair -> al" in proc.stdout, "explain shows the alias resolving to the handle")
    ok("Owner check: owned by" not in proc.stdout, "explain raises no owner objection for an alias of the actor")
    proc = r.run("explain", STRANGER_ID, "--at", "2026-09-06T09:00:00Z")
    ok("not a registered actor" in proc.stdout, "explain flags an owner no actor record knows")
    alias_occ = f"{ALIAS_ID}@2026-09-06T09:00+00:00"
    r.run("receipt", alias_occ, "intent", "--actor", "Alastair", "--machine", "test-box")
    fires = read_rows(lib / "user" / "docket" / "fires.jsonl")
    ok(fires[-1]["actor"] == "al", "a receipt written under an alias carries the canonical handle")
    (ledger / "actors.md").unlink()
    (ledger / "install.md").write_text(
        "# Install\n\n- installed by: Alastair Brayne\n- actor handle: al (the handle triggers carry as owner)\n",
        encoding="utf-8")
    due, _ = r.run_json("due", "--at", "2026-09-06T09:00:00Z")
    ids = [e["trigger"] for e in due]
    ok(NOOWNER_ID in ids and ALIAS_ID not in ids,
       "without actors.md the actor handle line names the actor and unregistered names are excluded")
    (ledger / "install.md").write_text("# Install\n\n- installed by: al\n", encoding="utf-8")
    due, _ = r.run_json("due", "--at", "2026-09-06T09:00:00Z")
    ok(NOOWNER_ID in [e["trigger"] for e in due], "with neither record, installed by still names the actor")

    # -- nothing binary inside the library ----------------------------------------
    print("hygiene")
    binary = []
    for p in lib.rglob("*"):
        if p.is_file():
            if p.suffix in (".sqlite", ".db") or p.name.endswith(("-wal", "-shm", "-journal")):
                binary.append(p)
            elif p.read_bytes()[:15] == b"SQLite format 3":
                binary.append(p)
    ok(not binary, "nothing binary under the library root")
    ok(not list(lib.rglob(".*.tmp")), "no temp files left behind")

    shutil.rmtree(scratch, ignore_errors=True)
    print(f"\nAll {checks} checks passed.")


if __name__ == "__main__":
    main()
