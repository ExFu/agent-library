# structured-worklist -- one folder, three record files, and a local search index

**Status:** Draft, for Al's rulings (2026-09-03, plan-mode session). Rulings
already taken in that session are marked as such below; the open decisions at
the end are the ones Al asked to think about before anything under `src/`
changes. Companion to `library-migrations.md` (this will be the second shipped
migration and the second conventions mint) and to the `durable/` reasoning
there, which already anticipated SQLite arriving.

## Why

Todos, reminders and the inbox are the records agents touch most often, and
they are the least structured thing in the library. Today they are freeform
markdown that a script guesses at: `dashboard-generator.py` takes the first
ISO date it finds anywhere in a line as the reminder's date, decides a folder
is a pointer by substring-matching phrases in `agent.md`, and splits a
reminders file into entries by whether it happens to use headings or bullets.
No record has a stable id, so nothing can say "this one" across a rename or a
sync conflict.

Two generations of format also contradict each other. The generated personal
skills (`reminders-template.md`, `inbox-template.md`) flip checkboxes in place
and store their file at `databases/reminders/reminders.md`; the folder-type
templates move finished items to `done.md` or `archive.md` and store them at
`<scope>/reminders/`. `setup-reminders` and `setup-inbox` still hard-code the
old path. The boot skill's fallback reads the folder-type location. An agent
following either set of instructions is wrong for the other.

The shape is also expensive to read. One markdown file per captured item is
the most token-costly form there is for an agent: a tool call per file, or a
glob-and-batch dance, before any thinking starts. Al's instinct to move to a
queryable store is right; the question is only where the store may live.

The ontology already answers that. `ontology.md#durable` bans SQLite, vector
stores and binary blobs from the synced library, because Dropbox and git sync
`-wal` and `-shm` sidecars independently and two surfaces produce a conflicted
binary copy with no merge, and it prescribes "built per-machine outside the
synced root, rebuilt by the nightly run, never a source of truth" for any fast
lookup. But `exfu/derived/`, the place that text names for indexes, sits inside
the root and therefore inside Dropbox. Nothing today is hashed or incremental;
every nightly run rewalks the whole tree.

One more constraint is load-bearing: Claude on a phone or on claude.ai reaches
the library only through the Dropbox connector, which reads and writes text
files by path and can never open a local binary. Whatever is canonical has to
be a small text file, or mobile loses it.

## Decisions

### 1. Canonical records are JSONL in the synced library; SQLite is derived only

**Al's ruling (2026-09-03).** The synced copy is text, and the database is a
cache. This is the ontology's existing rule applied rather than a new one, and
it is also what makes the sharing story work: sharing a scope's folder shares
its records, with nothing to reconcile against a central store.

JSONL rather than one-file-per-record, because the reading cost Al objected to
is the number of files, not the format: a whole collection is one read from any
surface, including one `get_file_content` on a phone. Conflicts under Dropbox
degrade to a `(conflicted copy)` text sibling, which is recoverable; the
ontology's JSONL merge rule for `durable/` extends here unchanged -- records
carry stable ids, union on id, latest `updated` wins -- and a nightly librarian
does the fold. APV's own `.apv/events.jsonl` beside `.apv/cache.sqlite` is the
same split already running in this ecosystem.

### 2. The three folder-types collapse into one folder holding three files

**Al's ruling (2026-09-03).** `todo/`, `reminders/` and `inbox/` were three
folder-types that mean "things with an open/done state that agents act on over
time". Putting them in one folder says so, and it simplifies everything that
touched them:

```
scopes/acme/worklist/
  agent.md             Follows: exfu/<ts>/ontology.md#worklist, plus Local deviations
  todo.jsonl           tasks with a completion state
  reminders.jsonl      nudges with a surface time or condition
  agent-backlog.jsonl  things the user leaves for agents to attend to
  archive.jsonl        compacted done/archived records from all three (carries kind)
  legacy/              the pre-0.11 folders, moved whole by the migration
```

- The ontology goes from ten folder-types to eight, with one `#worklist`
  anchor replacing three.
- Store-or-point becomes per file, declared in the one `agent.md`: a line
  `todo: tracked in ClickUp, not stored locally` means there is no `todo.jsonl`
  while the other two files stay local. The example library's ClickUp pointer
  beside local reminders is exactly this case.
- Materialise on demand still holds: a file appears on its first record, the
  folder on its first file.
- One generated personal skill replaces two: `setup-worklist` produces
  `<user>-worklist`, which captures, reminds, completes, snoozes and runs the
  session-start check on both the filesystem and connector backends.

### 3. The agent-facing file is `agent-backlog`

**Al's ruling (2026-09-03).** The inbox was never the user's in-tray; it is
where the user leaves things for agents to attend to, and the name has to say
so or users will read it as theirs. "Backlog" says a queue of work to pull
from, "agent" says whose. The `inbox-triage` librarian becomes `backlog-sweep`
with its behaviour unchanged: summarise and suggest, never move. The word
"inbox" leaves the vocabulary entirely, which also removes the email
connotation Al flagged.

### 4. The folder name -- proposed `worklist/`, Al to rule

Al proposed `project-management/`. The recommendation is `worklist/`: it says
the same thing ("this scope's list of work with an open/done state"), it stays
neutral in the `user/` scope, which is not a project, and it avoids importing a
discipline's vocabulary into a folder that also holds "remind me to call Mum".
Everything in this record writes `worklist/`; substituting the other name is a
find-and-replace at mint time. **Open decision B.**

### 5. One record shape for all three files, and it stays deliberately thin

```json
{"id":"20260903-1412-7f3a",
 "title":"Chase the Acme security questionnaire",
 "notes":"Sent 20 Aug, Priya said end of month.",
 "agent_notes":"Only surface after the Acme call has happened. If no reply by Friday, suggest escalating to Mark.",
 "status":"open",
 "created":"2026-09-03T14:12:00Z","updated":"2026-09-03T14:12:00Z",
 "keywords":["acme","security questionnaire","priya"],
 "trigger":{"next_at":"2026-09-10","repeat":null,"channel":null}}
```

- `title`; `notes` for humans; `agent_notes` as freeform instructions for
  agents (timing, conditions, dependencies, "only show when"); `status` one of
  `open | done | archived` (done means completed, archived means closed without
  doing or aged out of view); `created`, `updated`; `id` as a sortable
  timestamp plus a short random suffix.
- **Al's ruling:** no ontological fields. No priority, tags, dependencies or
  recurrence columns. They live in `agent_notes` as prose, so agents can wire
  things together without the schema having to anticipate them.
- `keywords` is optional and agent-authored at save time. It is the semantic
  layer that needs no model (see decision 7).
- `trigger` is optional, agent-derived from prose, and mainly on reminders.
  Whether it exists at all is **Open decision A** (see the reminders section).
- `done` and `archived` records are compacted into `archive.jsonl` after 30
  days by a nightly librarian, so the three active files stay small enough for
  a phone to read whole.

### 6. The derived layer moves outside the synced root; text caches stay

The binary index lives at `~/.exfu/derived/<library-id>/library.sqlite`, where
`library-id` is a short hash of the resolved library root (a moved library
simply rebuilds; it is a cache), with `EXFU_DERIVED_DIR` as an override. The
existing text caches (`index.json`, `agent-registry.json`, `agent-log.json`,
and a new `channels.json`) stay in `exfu/derived/` because boot and mobile
sessions read them through the connector. The ontology wording changes from
"search indexes go to `exfu/derived/`" to "text caches in `exfu/derived/`,
binary indexes per machine". This corrects the gap Al spotted: the text said
"outside the synced root" and the folder was inside it.

### 7. Search without embeddings, and never recomputing what has not changed

**Al's ruling (2026-09-03):** the plugin cannot assume a user who can install
Ollama, and cannot add anything that costs per call. Every embedding path
available today fails one of those tests: Ollama and sentence-transformers need
an install, hosted APIs cost and send library text to a third party,
`model2vec` static embeddings are numpy-only but still a `pip install`, and
Apple's NaturalLanguage framework needs Swift tooling. So vectors are deferred,
and the index is designed so they slot in later without a schema break.

What ships instead is stdlib only, verified on Al's machine (Python 3.12.7,
SQLite 3.45.3 with `ENABLE_FTS5`):

- Tables `items` (every record across scopes: scope, kind, id, status,
  `next_at`, content hash, raw JSON), `items_fts` (FTS5 over title, notes,
  agent_notes, keywords), `documents` and `documents_fts` (chunked `context/`
  markdown), `files` (path, mtime, size, hash), with nullable `embedding` and
  `embedding_model` columns reserved on `items` and `documents`.
- Incremental by construction: a file whose mtime and size are unchanged is
  skipped; otherwise each record or chunk is hashed over its canonical text
  fields and only rows whose hash changed are re-indexed, and rows whose ids
  vanished are deleted. The same rule will govern any future embedding step,
  which is Al's "don't recompute unless something changed" requirement.
- Semantic recall comes from the agent on both sides: `keywords` written at
  save time, query expansion at read time. BM25 through FTS5 is strong at
  personal-corpus scale.
- One bash call for agents: `exfu-index.py query "<terms>" [--scope] [--kind]
  [--status]`, `exfu-index.py due [--at]`, `exfu-index.py rebuild`.
- Mobile sessions read the JSONL files directly and never touch the index.

### 8. Reminders -- the design space, not yet a ruling

Al asked how users actually get reminded before deciding what a reminder must
contain, and whether the consumer is an agent or a program. Laying that out:

| Consumer | Agent or program | Minimally needs |
|---|---|---|
| Session start (`exfu-library` Step 14, via `<user>-worklist`) | Agent | Prose and status; it can judge "is this due" but pays for that every session. |
| Nightly librarians, `daily-briefing` | Agent, across many scopes | A cheap "which are due" filter before reading prose. |
| `dashboard-generator.py` | Program | A literal date to bucket overdue / soon / later; cannot read prose. |
| A future OS-level trigger (launchd, Claude routines) | Program | An exact `next_at`, a channel, an idempotency watermark. |

Only the programmatic consumers force a structured field; every agent consumer
would be fine on rich prose. That is what makes Al's "sidecar generated by
smart agents" the reconciling move: prose in `notes` and `agent_notes` is the
source of intent, and the agent that saves the record derives `trigger.next_at`
(plus `repeat` and `channel` when the prose states them) as a re-derivable
annotation. A nightly pass re-derives it after completion or snooze, and after
any edit no agent made, such as a raw connector write from a phone. The sidecar
has to live inside the synced record rather than only in the local index: the
dashboard script has no model to re-derive it, mobile cannot see a local cache,
and `exfu/derived/` is disposable by definition.

Channels: `dashboard` and `session-start` are always-present pull channels and
need no declaration. Push channels (Slack, WhatsApp, email, a custom MCP) are
declared as `Local deviations:` on `user/worklist/agent.md` for the global
default, or on a scope's `worklist/agent.md` to override, naming the connector
tool and a target and never a secret. Which connectors are actually installed
is regenerable and belongs in `exfu/derived/channels.json`, refreshed at boot
the way the storage backend is detected today. A reminder names a channel in
prose or inherits the default. The "is anything due" loop is a new
`librarians/reminder-dispatch.md` riding the existing `agents.py due` cadence
mechanic, and delivery stays agent-mediated so the connector consent rules
hold.

## Open decisions

These are Al's to rule on; the record proposes, it does not decide.

- **A. The trigger sidecar.** Is an optional, re-derivable `trigger` object
  acceptable under "no ontological fields", given prose stays authoritative?
  Without it, the dashboard and any future programmatic trigger go back to
  guessing dates from prose.
- **B. The folder name.** `worklist/` (recommended) or `project-management/`.
- **C. Dispatch cadence.** Nightly is cheap but cannot fire "3pm today";
  hourly costs an agent session per hour per user.
- **D. Default posture.** Push through a declared channel automatically, or
  pull-only (dashboard, session start) until a reminder opts in? Outbound
  Slack, WhatsApp and email are "explicit permission" actions today.
- **E. Consent.** Does declaring a channel constitute standing consent to
  send, or does every send need confirmation, which defeats the automation?
- **F. Delivered watermark and recurrence.** Where does "last delivered" live
  (proposal: `trigger.delivered_at` in the record)? Does `repeat` introduce
  real recurrence semantics, and who computes the next `next_at`?

## Enactment

One release, 0.11.0 (**Al's ruling:** one big release, not three), after the
open decisions are ruled:

1. Mint a new conventions version with `build/mint-conventions.sh`; never edit
   `20260724-1910` in place. The new `ontology.md` replaces `#todo`,
   `#reminders` and `#inbox` with one `#worklist` section (three files, record
   shape, per-file store-or-point, conflict and archive rules) and rewords the
   derived-location rule.
2. Templates: `defaults/worklist-agent.md` (with a pointer variant) and
   `scope/worklist/agent.md` replace the six todo/reminders/inbox defaults and
   three scope folders; one `worklist-template.md` replaces
   `reminders-template.md` and `inbox-template.md`.
3. Scripts, stdlib only: new `scheduled-tasks/library-index/index.py` (SQLite
   build, incremental hashing, `query`/`due`/`rebuild`); `substrate-index`
   learns the one folder-type and per-file status; `dashboard-generator.py`
   renders one Worklist section from records and drops `CHECKBOX_RE`,
   `classify_reminder_date`, `split_reminder_entries` and `POINTER_PHRASES`.
4. Librarians: `inbox-triage` becomes `backlog-sweep`; add `worklist-compact`
   (archive plus conflicted-copy fold) and `reminder-dispatch` per rulings C-E;
   register all three in `templates/agent-registry.json`.
5. Skills: `exfu-library` Steps 3 and 14 (`channels.json`, JSONL reads,
   index-aware, a one-time nudge to re-run setup); `scope-setup` Steps 3-5;
   new `setup-worklist` replacing `setup-reminders` and `setup-inbox`;
   `daily-briefing`; the three install skills; `exfu-guides`;
   `substrate-guide.md` to v14 with its changelog line; the primers.
6. Migration `exfu/migrations/<ts>-structured-worklist.md`:
   `requires_user_decision: true`, `reversible: true`, `conventions:
   "20260724-1910 -> <ts>"`, `applies_when: <scope>/worklist/ absent while any
   of todo/, reminders/, inbox/ holds content` (the target's absence, per the
   ontology). It creates `worklist/agent.md` carrying each old folder's
   pointer lines over as per-file lines, converts checkbox lines, reminder
   entries and inbox files into records with the saving agent deriving
   `keywords` (and `trigger` if A is ruled in), moves the three old folders
   whole into `worklist/legacy/`, and records the outcome in the ledger.
   Existing `<user>-reminders` and `<user>-inbox` skills keep working against
   `legacy/` until the user re-runs setup. Rebuild `example/` through it.
7. Bump the three manifests to 0.11.0, write the CHANGELOG entry in house
   style with a link back here, `./build/build.sh all`, capture, commit.
