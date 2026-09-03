# structured-worklist -- one docket per scope, mixin files, triggers, and a local index

**Status:** Adopted (Al, 2026-09-03, in session, after three passes, a Codex
audit and a two-voice council). Every open decision is ruled and folded into
the decisions below; the audit's corrections are applied in place rather than
listed separately. Enacted as release 0.11.0 on 2026-09-03 (conventions
`20260903-1743`); the attended migration's first real run and the phone-side
connector check are the two verifications still owed. Companion to
`library-migrations.md` (this will be the second shipped migration and the
second conventions mint) and to the `durable/` reasoning there, which already
anticipated SQLite arriving.

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

Three more constraints are load-bearing. Claude on a phone or on claude.ai
reaches the library only through the Dropbox connector, which reads and writes
text files by path and can never open a local binary: whatever is canonical has
to be a small text file, or mobile loses it. The library lives and runs on the
user's desktop (**Al's ruling**): anything else means vendor lock-in or cloud
infrastructure of our own, and neither is on the table yet. And about half a
dozen people are already using the library at different stages, and Al is
already sharing scopes with one of them (**Al's ruling**): the change has to
be kind to existing libraries and has to work when two people act on one
scope.

## Decisions

### 1. Canonical records are JSONL in the synced library; SQLite is derived only

**Al's ruling.** The synced copy is text, and the database is a cache. This
is the ontology's existing rule applied rather than a new one, and it is also
what makes the sharing story work: sharing a scope's folder shares its
records, with nothing to reconcile against a central store.

JSONL rather than one-file-per-record, because the reading cost Al objected to
is the number of files, not the format: a whole collection is one read from any
surface, including one `get_file_content` on a phone. APV's own
`.apv/events.jsonl` beside `.apv/cache.sqlite` is the same split already
running in this ecosystem.

Three rules make JSONL safe under sync, all applied by the audit:

- **Ids are library-wide.** A UTC timestamp to the second plus at least ten
  random base32 characters (ULID strength), generated with a collision check
  against the index. Any file can reference any record by id alone, which is
  what the mixin convention (decision 6) needs.
- **Mutable rows carry a common envelope**: `id`, `created`, `updated`,
  `revision` (an integer the writer increments), and an optional
  `deleted: true` tombstone. Conflicts under Dropbox degrade to a
  `(conflicted copy)` text sibling; the nightly fold unions on `id` and keeps
  the row with the highest `revision`, then the latest `updated`, then the
  lexically lowest writer handle, and removes the sibling. Conflicted copies
  of a trigger file are folded before the dispatcher acts on it.
- **Immutable rows never fold.** Signals and fire receipts (decisions 10 and
  11) are append-only; a conflicted copy is unioned by id and that is the
  whole rule.

### 2. The three folder-types collapse into one folder holding three files

**Al's ruling.** `todo/`, `reminders/` and `inbox/` were three folder-types
that mean "things with an open/done state that agents act on over time".
Putting them in one folder says so:

```
scopes/acme/docket/
  agent.md             Follows: exfu/<ts>/ontology.md#docket, plus Local deviations
  todo.jsonl           tasks with a completion state
  reminders.jsonl      nudges with a surface time or condition
  agent-backlog.jsonl  things the user leaves for agents to attend to
  archive.jsonl        compacted done/archived records (archive envelope adds kind)
  triggers.jsonl       when and how matters get heard        (decision 9)
  signals.jsonl        facts agents recorded for whoever listens (decision 10)
  fires.jsonl          receipts of triggers firing            (decision 11)
  channels.jsonl       how this scope reaches people          (decision 14)
  legacy/              the pre-0.11 folders, moved whole if the scope migrates
```

- One `#docket` anchor. The old anchors stay, deprecated (decision 17).
- Store-or-point becomes per file, declared in the one `agent.md`: a line
  `todo: tracked in ClickUp, not stored locally` means there is no `todo.jsonl`
  while the other files stay local. The example library's ClickUp pointer
  beside local reminders is exactly this case.
- Materialise on demand still holds: a file appears on its first record, the
  folder on its first file. The mixin files live here because the ontology's
  nesting rule allows only folder-types, `scope.md` and `scopes/` at a scope's
  root, and because the docket is the list of matters and these files are how
  matters get heard and how the docket reaches people (**Al's ruling**, M).
- One generated personal skill replaces two: `setup-docket` produces
  `<user>-docket`, which captures, reminds, completes, snoozes and runs the
  session-start check on both the filesystem and connector backends.

### 3. The agent-facing file is `agent-backlog`

**Al's ruling.** The inbox was never the user's in-tray; it is where the user
leaves things for agents to attend to, and the name has to say so or users
will read it as theirs. "Backlog" says a queue of work to pull from, "agent"
says whose. The `inbox-triage` librarian becomes `backlog-sweep` with its
behaviour unchanged: summarise and suggest, never move. The word "inbox"
leaves the vocabulary of new libraries, which also removes the email
connotation Al flagged.

### 4. The folder is `docket/`

**Al's ruling, from a list of thirty.** A docket is a court's list of matters
to be heard: precise, unclaimed by any existing vocabulary in the library, and
it reads as naturally in `user/` ("my docket") as in a client scope. Rejected
in the same pass: `worklist/` (safe but corporate), `project-management/`
(imports a discipline into a folder that also holds "call Mum"),
`open-loops/` (right idea, needs explaining), `agenda/`, `actions/` and
`tasks/` (each collides with `scheduled/`, the dashboard's Action Basket, or
Claude's own scheduled tasks). `agent-docket/` was set aside: the file inside
already says which entries are for agents, and the docket as a whole is the
user's.

### 5. One record shape for all three files, and it stays deliberately thin

```json
{"id":"20260903T141200Z-7F3A9QK2MB",
 "title":"Chase the Acme security questionnaire",
 "notes":"Sent 20 Aug, Priya said end of month.",
 "agent_notes":"Only surface after the Acme call has happened. If no reply by Friday, suggest escalating to Mark.",
 "status":"open",
 "created":"2026-09-03T14:12:00Z","updated":"2026-09-03T14:12:00Z","revision":1,
 "keywords":["acme","security questionnaire","priya"]}
```

- `title`; `notes` for humans; `agent_notes` as freeform instructions for
  agents (timing, conditions, dependencies, "only show when"); `status` one of
  `open | done | archived` (done means completed, archived means closed without
  doing or aged out of view); the common envelope from decision 1.
- **Al's ruling:** no ontological fields. No priority, tags, dependencies or
  recurrence columns. They live in `agent_notes` as prose, so agents can wire
  things together without the schema having to anticipate them. Anything that
  genuinely needs a structured facet arrives as a mixin (decision 6), never as
  a column.
- `keywords` is optional and agent-authored at save time. It is the semantic
  layer that needs no model (decision 8).
- `done` and `archived` records are compacted into `archive.jsonl` after 30
  days by the nightly compaction librarian. The archive envelope is the record
  plus `kind: todo | reminder | agent-backlog`, specified separately so the
  active files stay thin and small enough for a phone to read whole.

### 6. Structured facets are mixin files, joined on id

**Al's ruling.** A facet that programs need to read does not become a column
on the record. It lives in its own JSONL file whose rows reference the record
they decorate. This is normalisation, and it buys three things: the docket
schema never grows (every future "I wish items had X" is a new file, not a
schema change); programmatic readers read only the mixin (the dispatcher never
opens `todo.jsonl`); and a mixin can attach to anything with an id.

- A mixin row's `target` is typed and scope-qualified: `{"type":
  "docket-entry | document | record | scope", "scope": "<scope name>", "id":
  "<record id or path>"}`. Documents and database records are addressed by
  path relative to the scope; scopes by name.
- Referential integrity across files is the cost. The nightly compaction
  librarian removes a mixin row 30 days after its target closes or disappears
  (**Al's ruling**, K), and the index flags orphans until then.
- A responsibilities mixin, if a shared scope ever needs the full RACI grid,
  follows the same pattern (decision 13).

### 7. The derived layer moves outside the synced root; text caches stay

The binary index lives at `~/.exfu/derived/<library-id>/library.sqlite`, where
`library-id` is a short hash of the resolved library root (a moved library
simply rebuilds; it is a cache), with `EXFU_DERIVED_DIR` as an override. The
existing text caches (`index.json`, `agent-registry.json`, `agent-log.json`,
and new `channels.json` and `due.json`) stay in `exfu/derived/` because boot
and mobile sessions read them through the connector. `due.json` carries the
index generation and the source files' hashes it was computed from, and the
dispatcher rejects it when those no longer match. The ontology wording changes
from "search indexes go to `exfu/derived/`" to "text caches in
`exfu/derived/`, binary indexes per machine". This corrects the gap Al
spotted: the text said "outside the synced root" and the folder was inside it.

### 8. Search without embeddings, and never recomputing what has not changed

**Al's ruling:** the plugin cannot assume a user who can install Ollama, and
cannot add anything that costs per call. Every embedding path available today
fails one of those tests: Ollama and sentence-transformers need an install,
hosted APIs cost and send library text to a third party, `model2vec` static
embeddings are numpy-only but still a `pip install`, and Apple's
NaturalLanguage framework needs Swift tooling. So vectors are deferred, and
the index is designed so they slot in later without a schema break.

What ships is stdlib only, verified on Al's machine (Python 3.12.7, SQLite
3.45.3 with `ENABLE_FTS5`):

- Tables `items` (every docket record across scopes: scope, kind, id, status,
  content hash, raw JSON), `items_fts` (FTS5 over title, notes, agent_notes,
  keywords), `triggers` (with `next_at` indexed), `signals`, `fires`,
  `channels`, `files` (path, mtime, size, hash), with nullable `embedding` and
  `embedding_model` columns reserved on `items`. Chunked `context/` document
  search is a second product inside a docket release and waits for the next
  one; its tables are designed, not built.
- Incremental by construction, hash first: mtime and size are hints that a
  file *may* be unchanged, not proof; any file whose hints match is still
  hashed on a slow cadence (the nightly run validates everything, the hourly
  run trusts hints), and only rows whose content hash changed are re-indexed,
  rows whose ids vanished are deleted. The same rule will govern any future
  embedding step, which is Al's "don't recompute unless something changed"
  requirement.
- Semantic recall comes from the agent on both sides: `keywords` written at
  save time, query expansion at read time. BM25 through FTS5 is strong at
  personal-corpus scale.
- One bash call for agents: `exfu-index.py query "<terms>" [--scope] [--kind]
  [--status]`, `exfu-index.py due [--at <time>]` (the dry run: what would
  fire), `exfu-index.py explain <trigger id>`, `exfu-index.py fire <trigger
  id> --now`, `exfu-index.py rebuild`.
- Mobile sessions read the JSONL files directly and never touch the index.

### 9. Triggers: a scope says when and how a matter gets heard

**Al's ruling, generalising the reminder question.** A reminder is a docket
entry with a trigger attached, and a trigger need not point at a docket entry
at all: it is a scope-level statement that at some moment, or on some
occurrence, something should be assessed by an agent, together with how that
assessment should be handled. Reminders, email checks, follow-up chasing and
"see whether the build passed" become one mechanism with different weights.

```json
{"id":"20260903T150200Z-A91CQ7ZP4R",
 "target":{"type":"docket-entry","scope":"acme","id":"20260903T141200Z-7F3A9QK2MB"},
 "assess":"Surface the Acme questionnaire chase if the Acme call has happened; otherwise leave it.",
 "when":{"mode":"cron","spec":"0 9 * * 1-5","tz":"Europe/London"},
 "on":null,
 "handler":{"kind":"agent","weight":"light","ref":null},
 "channel":"slack-dm",
 "owner":"al",
 "status":"armed",
 "created":"2026-09-03T15:02:00Z","updated":"2026-09-03T15:02:00Z","revision":1}
```

- `assess` is prose: the brief handed to whatever handles the trigger. Prose
  is the source of intent, as everywhere else.
- `when` is one of the schedule modes in decision 16, with `tz` as an IANA
  zone name on every time-based trigger so a 9am rule does not drift in
  October. `on` names a signal (decision 10) for signal-armed triggers; a
  trigger may have both, meaning "on that signal, but not outside this
  schedule's window".
- `handler.kind` is `deliver` (send the target entry, or `assess` when there
  is no target, through the channel), `agent` (spin up a sub-agent of the
  given `weight` with `assess` as its brief), or `definition` (run a
  registered scheduled-agent or librarian definition named by `ref`).
  `weight` is `light | medium | heavy`, mapped at dispatch to the cheapest, a
  mid, and the strongest available model. This is the information Al said
  must travel with the trigger, inline or by reference.
- `channel` names a channel (decision 14); absent means pull. `owner` is the
  actor accountable (decision 13). `status` is `armed | paused | disarmed`;
  a `once` trigger is disarmed by the dispatcher after its receipt is
  written, and a trigger is paused, not disarmed, after three consecutive
  failed fires.
- A trigger row is authored, and near-immutable: the dispatcher never writes
  to it except to disarm a `once` or pause a failing one. Everything that
  happens to a trigger is a receipt (decision 11). This is the audit's central
  correction: watermarks on the trigger row would make `triggers.jsonl` the
  most-written file in the library, synced dozens of times a day while the
  conflict fold runs nightly.

### 10. Signals: the arc between actions

Al asked whether an email-condition trigger implies a dependency graph
between triggers, and whether there is a simple, powerful "action, arc,
action" model underneath. There is (**Al's ruling**, G), and it is not a
dependency graph authored by hand. It is a blackboard: a fired trigger's
handler reports the signals it actually observed or produced, the dispatcher
appends them to `signals.jsonl`, and any trigger may be armed on a signal
name. The arc is the name. "Check email for the Acme reply, and report
`acme-reply-seen` if there is one" plus "on `acme-reply-seen`, draft the
follow-up" creates the graph without either trigger knowing about the other,
an agent can add a third consumer without editing the producer, and the
dashboard renders the implied graph from the index rather than from a diagram
anyone maintains. Explicit DAGs are brittle under deletion and forking; if a
DAG view is ever wanted it is a projection over signals, never an authored
file.

The rules that make the blackboard sound, all from the audit:

- **Names are library-global strings**; the row carries the scope that
  emitted it as metadata. Otherwise the motivating arc, a `user/` email check
  feeding an Acme-scope follow-up, could never fire.
- **Signals are append-only and immutable**, with a flat 30-day retention
  window swept by the compaction librarian. Nothing is "consumed": in a
  blackboard the producer does not know who listens.
- **Each trigger watermarks the signals it has seen** through its receipts
  (decision 11) and scans forward from the last one, so a trigger armed after
  a signal was written, or on a machine whose Dropbox had not yet pulled it,
  behaves by a stated rule rather than a race. A signal id is the idempotency
  key: one trigger fires at most once per signal.
- **The handler reports, the dispatcher never assumes.** A trigger declares
  nothing about what it emits; the handler's result names the signals it
  produced, so the email check emits `acme-reply-seen` only when a reply
  exists. Payload is prose plus optional small JSON; shape changes are more
  prose.
- **Silent failure is designed out**: the index flags a trigger armed on a
  name that nothing has ever emitted, the way it flags orphaned mixin rows.
- **Loops are bounded across ticks**: at most five fires per signal name per
  24 hours; beyond that the dispatcher suppresses and surfaces the trigger as
  "suppressed, check for a loop".
- **Latency is stated**: an `on` trigger resolves within one dispatcher
  cadence tick, not in real time; a three-hop chain can take three ticks.

A signal is a fact an agent recorded about the world at a moment, addressed
to whoever is listening: scope data, synced and small; not `durable/` (it is
about the world and regenerable in principle), not `exfu/derived/` (it is
authored, not rebuilt).

### 11. Fire receipts: the crash-safe record of what happened

`fires.jsonl` beside the triggers (**Al's ruling**, N: it has to be shared
with everyone who has the scope, so it cannot live at the root in `durable/`).
Append-only, immutable rows, one occurrence per row pair:

```json
{"id":"...","occurrence":"20260903T150200Z-A91CQ7ZP4R@2026-09-04T09:00+01:00","trigger":"20260903T150200Z-A91CQ7ZP4R","phase":"intent","actor":"al","machine":"al-mbp","at":"2026-09-04T09:03:11Z"}
{"id":"...","occurrence":"20260903T150200Z-A91CQ7ZP4R@2026-09-04T09:00+01:00","trigger":"20260903T150200Z-A91CQ7ZP4R","phase":"result","status":"delivered","signals":["acme-chase-surfaced"],"idempotency_key":"...","at":"2026-09-04T09:03:40Z"}
```

- The occurrence id is trigger id plus scheduled instant (or plus signal id
  for `on` triggers). The dispatcher writes `intent` **before** acting and
  `result` after, so a crash between the two leaves a visible half-receipt
  that the next run treats as "attempted, outcome unknown" and does not
  blindly repeat. Where a connector accepts an idempotency key it is passed
  and recorded; where it does not, the record states at-least-once delivery.
- `status` is `delivered | drafted | failed | skipped | suppressed`. Three
  consecutive `failed` results pause the trigger, reusing the registry's
  flag-after-three convention; the pause surfaces at session start.
- **Misfire policy, one rule**: at most once per trigger per dispatcher run,
  never backfill; a run that finds several elapsed occurrences fires the most
  recent and records the rest as `skipped`. This matches what Claude Code
  Desktop itself does for a scheduled task that missed its slot.
- Receipts are the audit trail, the "last delivered" watermark, the
  per-trigger signal watermark, and the basis for the claim in decision 13.
  Retention: 90 days, then swept by the compaction librarian.

### 12. The dispatcher

One scheduled agent, `librarians/dispatcher.md`, the cheapest model
available. **Al's ruling:** it must not boot the library and must not read
anything extraneous. Its whole fast path is: refresh the index incrementally,
read the due view (one query, or `exfu/derived/due.json` where the index is
unavailable, rejecting a stale one), and for each due trigger whose owner is
the local actor or `any`: write the intent receipt, do what the handler says
(deliver through the channel, or spawn a sub-agent at the declared weight
with the `assess` brief), write the result receipt with the signals the
handler reported, and exit. It never reads `todo.jsonl`, `context/`, or the
user's wow.

**Where it runs (Al's ruling, I, resolved by the documentation):** as a
Claude Code Desktop *local* scheduled task. The docs give it a one-minute
minimum interval, a model picker, a per-sub-agent model override (so
`weight` maps to Haiku, Sonnet, and Opus or Fable), local filesystem access,
and "runs only while the app is open and the machine is awake, with exactly
one catch-up run for a missed slot", which is the misfire rule in decision
11 already. Cowork's scheduled tasks run in the cloud with no local
filesystem and undocumented sub-agent model choice, and cloud routines are
hourly-minimum on a fresh clone with no local files; neither can run the
dispatcher. A Cowork-only user therefore gets the boot-time drain and the
dashboard, and the record says so plainly.

**Cadence (Al's ruling, L):** the existing `hourly` cadence, plus a
boot-time drain: when any session loads `exfu-library`, Step 14 runs the
same due-view check and delivers pull-channel items in the session. For
someone in Claude several times a day this beats a half-hour cron on a laptop
that sleeps, and it adds no cadence vocabulary. A half-hour cadence is
possible later (Desktop allows it) and needs only a registry entry and a
task template.

### 13. Actors, ownership, and the lease

Al is already sharing scopes, so the two-actor case is real now (**Al's
ruling**, H), and the audit's objection to a *global* lease file in
`exfu/derived/` stands: a disposable cache on a sync layer with no locking
can be acquired twice, and a lease held by one actor would block another's
owned work. The resolution keeps the lease concept and re-homes it:

- The ontology defines `actor`: a person or an agent, with a handle. A solo
  library's actor is the one `install.md` names; in a shared scope each
  participant's handle is whatever their own library's `install.md` says, and
  the scope's `agent.md` lists the participants under `Local deviations:`
  until the team plugins gain a member registry.
- Every trigger carries `owner` (a handle or `any`), defaulting to the
  library's actor. The dispatcher fires only triggers it owns or that are
  `any`. Ownership is the first line of defence against double-firing and
  needs no coordination at all.
- For `any` triggers in a shared scope, the **claim is the intent receipt**.
  Before acting, a dispatcher appends `intent` naming its actor and machine;
  it then re-reads `fires.jsonl` and, if another actor's `intent` for the
  same occurrence is present, the lexically lower handle proceeds and the
  other records `skipped`. Dropbox sync latency leaves a small window in which
  both may act; dispatcher start times are jittered by actor handle to shrink
  it, and the residual risk is documented as at-least-once for `any`
  triggers, which is why outward `auto` channels are not `any`-fireable.
- Full RACI, if a scope ever needs it, is a `responsibilities.jsonl` mixin
  over decision 6.

### 14. Channels are declared by any scope, against an ontological interface

**Al's ruling.** The ontology defines what a channel is; any scope may
declare channels; `user/` is just the scope where most people declare their
default `dm`. The audit moved the declaration out of `scope.md`, which the
ontology says carries no entity lists or state, into `docket/channels.jsonl`
with stable ids:

```json
{"id":"20260903T160000Z-CH4NN3LQ2A","name":"slack-dm","kind":"dm","via":"slack","target":"@al","send":"auto","created":"...","updated":"...","revision":1}
{"id":"20260903T160100Z-CH4NN3LQ2B","name":"acme-team","kind":"broadcast","via":"slack","target":"#acme-project","send":"draft","created":"...","updated":"...","revision":1}
```

- `kind`: `pull` (the dashboard and session start; always present, never
  declared), `dm` (reaches one named actor), `broadcast` (reaches several
  people or an unspecified audience). Reach is by who receives, not by
  medium: a message to a colleague's agent is `dm` to that actor.
- `via` is the connector that sends; `target` the address, never a secret;
  `send` is decision 15's consent attribute.
- A trigger names a channel; resolution walks the scope chain (own scope,
  parents, `user/`). An unresolvable name degrades to pull, and the
  undelivered count surfaces at session start as well as on the dashboard,
  so a renamed Slack channel cannot silently stop a `dm` that exists to catch
  the user's attention.
- Which connectors are actually present on this surface is regenerable and
  lives in `exfu/derived/channels.json`, refreshed at boot the way the
  storage backend is detected today.

### 15. Consent is a property of the channel, and grants are a ledger

**Al's ruling.** Whether the dispatcher may send unattended is decided per
channel: `send: draft` by default (the handler prepares the message where the
connector keeps drafts, or on the dashboard's "ready to send" list, and a
person sends it; some connectors only allow this anyway), `send: auto` when
the user elevates it, which is the whole point of a `dm` to oneself and is
legitimate for pre-authorised working relationships such as pinging a
colleague or their agent. Client-facing channels are expected to stay
`draft`.

The audit's enforcement corrections:

- **Grants are authoritative, not the flag.** Elevation is recorded as an
  append-only grant in `durable/ledger/grants.md` (who, when, which channel
  id, revoked when); the dispatcher validates an active grant before every
  `auto` send, so editing `send: auto` in place grants nothing.
- **Caps bound one misread rule**: a per-channel daily send cap and a per-run
  cap; a tripped cap degrades to `draft` and records `suppressed`.
- **In 0.11.0, `auto` is honoured only on a `dm` whose target is the trigger's
  owner.** Outward `auto` (a `dm` to someone else, any `broadcast`) is
  declared, granted and shown, but the dispatcher drafts until the next
  release finishes the outward mechanism.

The pros and cons that led here, kept for the record: standing consent makes
automation real but lets an unattended agent send on your behalf; per-send
confirmation is safe but defeats the dispatcher and piles up unanswered. The
split that resolves most of it is self-directed versus outward reach, which
is what `kind` plus `send` plus the grant encode.

### 16. Schedule modes: three, fully specified

**Al's ruling (J):** ship `once`, `cron` and `on-signal`; the other two fold
in.

| mode | meaning | next occurrence | after firing |
|---|---|---|---|
| `once` | dump-and-done | `when.at`, an instant with `tz` | disarmed |
| `cron` | a 5-field cron spec (minute hour day-of-month month day-of-week, standard ranges and lists, no seconds, no `@` aliases), evaluated in `when.tz` | computed by the dispatcher from the spec and the last `result` receipt | armed |
| `on-signal` | fire when a signal named by `on` appears (optionally only inside a `when` window) | none; the signal is the moment | armed, at most once per signal id |

- "Every other Monday" or "first working day of the month" is resolved
  **once, at authoring time**, by the agent that saves the trigger, into a
  `cron` spec or a `once` instant, and the original prose is kept in
  `assess` so a person can see what was meant and correct the spec.
- "Re-arm when the task is completed" is `on-signal` on
  `entry-completed:<entry id>`, which the compaction librarian and the
  personal skill emit whenever an entry's status changes. No mode needed.
- Misfire policy is decision 11's. DST is handled by the zone; an
  occurrence that does not exist on a spring-forward day is skipped, one that
  exists twice on a fall-back day fires once.

### 17. Backwards compatibility: deprecate, never wipe

**Al's ruling (O).** Everything here is a new approach, so nothing historical
needs to be removed; half a dozen people are using the library at different
stages and the change must be kind to them. So there is no "first slice" and
no dormant machinery beyond what decision 15 states; instead:

- The old folder-types `todo/`, `reminders/` and `inbox/` **stay in the
  ontology, marked deprecated**: no new scaffolding creates them, `scope-setup`
  offers only `docket/`, but a scope that has them keeps working and every
  reader (boot Step 14, the dashboard, the index, the daily briefing) keeps
  its legacy parser for them. The regex parsers therefore stay as a clearly
  labelled legacy path rather than being deleted.
- The migration is **offered, not imposed**: `requires_user_decision: true`,
  and the managing agent judges per scope whether conversion is doable
  (parseable content, a recognised shape, the user present); a scope it
  declines is recorded `skipped` and stays on the old folders indefinitely.
- The migration is **per scope with a journal**: an upfront inventory of
  every candidate scope, a progress journal in `durable/ledger/`, idempotent
  steps, originals preserved in `docket/legacy/` and a count-and-hash
  reconciliation before anything moves, each migrated scope's `exfu:` pin and
  `latest.txt` updated, and the library-wide outcome recorded `applied` only
  when every selected scope verifies.
- The migration **discovers real paths first**: generated personal skills
  hard-code their file, commonly `databases/reminders/reminders.md`, so the
  agent reads the installed `<user>-reminders` and `<user>-inbox` skills and
  folder pointers before converting anything, and regenerates the personal
  skill as `<user>-docket` inside the attended migration rather than
  promising the old one keeps working.
- `library-updater`'s contract is revised: today it stops any migration whose
  non-ledger writes are not under `exfu/`; it will permit writes the migration
  declares under `writes:` inside `user/` and `scopes/`, after consent, with
  the journal, reversibility and recovery steps above.

### 18. Plain language at the surface

`cron`, `signal`, `trigger`, `dm`, `broadcast`, `draft`, `auto` and `docket`
are schema values and internal vocabulary. Setup conversations and the
dashboard use plain labels: "reminder rule", "something happened", "tell me",
"tell the team", "prepare only", "send automatically", "your docket" only
after the user has the thing it names. This is T1's plain-language principle
applied, and the audit's one low finding.

## Open verification

None blocking. Two facts to confirm during enactment rather than before it:
that Claude Code Desktop's per-sub-agent model override behaves the same
inside a local scheduled task as in an interactive session (the docs state it
for sessions and are silent for tasks), and that Python's bundled SQLite on a
fresh macOS install, not only Al's, has FTS5 compiled in.

## Enactment

One release, 0.11.0 (**Al's ruling:** one big release), after Al accepts this
record:

1. Mint a new conventions version with `build/mint-conventions.sh`; never
   edit `20260724-1910` in place. The new `ontology.md` adds `#docket` (three
   record files, the record shape and common envelope, per-file
   store-or-point, the archive envelope, the mixin files), `#mixins`,
   `#triggers`, `#signals`, `#fires`, `#actors`, `#channels` and `#grants`;
   marks `#todo`, `#reminders` and `#inbox` deprecated with a pointer to
   `#docket`; rewords the derived-location rule; and extends the migrations
   section with the per-scope journal convention.
2. Templates: `defaults/docket-agent.md` (with a pointer variant) and
   `scope/docket/agent.md`; the six todo/reminders/inbox defaults and three
   scope folders remain for deprecated scopes but are no longer offered; one
   `docket-template.md` replaces `reminders-template.md` and
   `inbox-template.md`.
3. Scripts, stdlib only: new `scheduled-tasks/library-index/index.py` (SQLite
   build, hash-first incremental rebuild, `query`/`due`/`explain`/`fire`/
   `rebuild`, `due.json` emission with generation and source hashes, the
   conflict fold, receipts and signals); `substrate-index` learns `docket`
   and per-file status beside the deprecated three; `dashboard-generator.py`
   renders a Docket section from records with trigger, signal-graph and
   receipt views, keeps the legacy renderer for deprecated folders, and
   labels it as such.
4. Librarians: `inbox-triage` becomes `backlog-sweep`; add `docket-compact`
   (archive after 30 days, conflicted-copy fold, mixin sweep at 30 days,
   signal sweep at 30, receipt sweep at 90, `entry-completed` signals) on the
   nightly cadence and `dispatcher` on the hourly cadence; register both in
   `templates/agent-registry.json`; ship a Claude Code Desktop local task
   template for the hourly run with the cheapest model selected;
   `install-scheduled-agent` learns the model picker.
5. Skills: `exfu-library` Steps 3 and 14 (`channels.json`, JSONL reads,
   index-aware, the boot-time drain, undelivered and paused counts, a
   one-time nudge to re-run setup); `scope-setup` Steps 3-5 (one "active
   work, then `docket/`" mapping, per-file pointer question, channel
   declaration in plain language); new `setup-docket` replacing
   `setup-reminders` and `setup-inbox`; `daily-briefing`; the three install
   skills; `exfu-guides`; `substrate-guide.md` to v14 with its changelog
   line; the primers.
6. `library-updater`: revise its contract per decision 17 (declared scope
   writes after consent, per-scope journal, reversibility, recovery).
7. Migration `exfu/migrations/<ts>-docket.md`: `requires_user_decision:
   true`, `reversible: true`, `conventions: "20260724-1910 -> <ts>"`,
   `applies_when: any scope holds todo/, reminders/ or inbox/ content and has
   no docket/` (the target's absence). Per decision 17: discover real paths
   from installed personal skills and folder pointers; inventory candidate
   scopes; for each, the managing agent judges doability, reconciles counts
   and hashes, creates `docket/agent.md` carrying pointer lines over,
   converts checkbox lines, reminder entries and inbox files into records
   with `keywords` and, for dated reminders, a `once` or `cron` trigger,
   moves the old folders whole into `docket/legacy/`, updates the scope pin,
   journals the step; regenerates `<user>-docket` in the same sitting;
   records `applied` only when every selected scope verifies, `skipped` per
   declined scope. Rebuild `example/` through it so it shows the lived-in
   shape (the example keeps one deprecated scope on purpose).
8. Bump the three manifests to 0.11.0, write the CHANGELOG entry in house
   style with a link back here, `./build/build.sh all`, capture, commit.
