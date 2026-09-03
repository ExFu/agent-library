# structured-worklist -- one docket per scope, mixin files, triggers, and a local index

**Status:** Draft, second pass plus audit (2026-09-03, two plan-mode
sittings, then a Codex audit and a two-voice council whose consolidated
findings sit before the open decisions). Rulings Al has taken are marked as
such; the open decisions at the end are the ones still to think about.
Nothing under `src/` changes until the open decisions are ruled. Companion to `library-migrations.md` (this will be the second
shipped migration and the second conventions mint) and to the `durable/`
reasoning there, which already anticipated SQLite arriving.

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

Two more constraints are load-bearing. Claude on a phone or on claude.ai
reaches the library only through the Dropbox connector, which reads and writes
text files by path and can never open a local binary: whatever is canonical has
to be a small text file, or mobile loses it. And the library lives and runs on
the user's desktop (**Al's ruling**): anything else means either vendor lock-in
or cloud infrastructure of our own, and neither is on the table yet.

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

Ids are unique library-wide, not per file (a sortable timestamp plus a short
random suffix), so any file can reference any record by id alone. That is what
makes the mixin convention in decision 6 work.

### 2. The three folder-types collapse into one folder holding three files

**Al's ruling (2026-09-03).** `todo/`, `reminders/` and `inbox/` were three
folder-types that mean "things with an open/done state that agents act on over
time". Putting them in one folder says so, and it simplifies everything that
touched them:

```
scopes/acme/docket/
  agent.md             Follows: exfu/<ts>/ontology.md#docket, plus Local deviations
  todo.jsonl           tasks with a completion state
  reminders.jsonl      nudges with a surface time or condition
  agent-backlog.jsonl  things the user leaves for agents to attend to
  archive.jsonl        compacted done/archived records from all three (carries kind)
  legacy/              the pre-0.11 folders, moved whole by the migration
```

- The ontology goes from ten folder-types to eight, with one `#docket` anchor
  replacing three.
- Store-or-point becomes per file, declared in the one `agent.md`: a line
  `todo: tracked in ClickUp, not stored locally` means there is no `todo.jsonl`
  while the other two files stay local. The example library's ClickUp pointer
  beside local reminders is exactly this case.
- Materialise on demand still holds: a file appears on its first record, the
  folder on its first file.
- One generated personal skill replaces two: `setup-docket` produces
  `<user>-docket`, which captures, reminds, completes, snoozes and runs the
  session-start check on both the filesystem and connector backends.

### 3. The agent-facing file is `agent-backlog`

**Al's ruling (2026-09-03).** The inbox was never the user's in-tray; it is
where the user leaves things for agents to attend to, and the name has to say
so or users will read it as theirs. "Backlog" says a queue of work to pull
from, "agent" says whose. The `inbox-triage` librarian becomes `backlog-sweep`
with its behaviour unchanged: summarise and suggest, never move. The word
"inbox" leaves the vocabulary entirely, which also removes the email
connotation Al flagged.

### 4. The folder is `docket/`

**Al's ruling (2026-09-03, second sitting), from a list of thirty.** A docket
is a court's list of matters to be heard: precise, unclaimed by any existing
vocabulary in the library, and it reads as naturally in `user/` ("my docket")
as in a client scope. Rejected in the same pass: `worklist/` (safe but
corporate), `project-management/` (imports a discipline into a folder that
also holds "call Mum"), `open-loops/` (right idea, needs explaining),
`agenda/`, `actions/` and `tasks/` (each collides with `scheduled/`, the
dashboard's Action Basket, or Claude's own scheduled tasks). `agent-docket/`
was considered and set aside: the file inside already says which entries are
for agents, and the docket as a whole is the user's.

### 5. One record shape for all three files, and it stays deliberately thin

```json
{"id":"20260903-1412-7f3a",
 "title":"Chase the Acme security questionnaire",
 "notes":"Sent 20 Aug, Priya said end of month.",
 "agent_notes":"Only surface after the Acme call has happened. If no reply by Friday, suggest escalating to Mark.",
 "status":"open",
 "created":"2026-09-03T14:12:00Z","updated":"2026-09-03T14:12:00Z",
 "keywords":["acme","security questionnaire","priya"]}
```

- `title`; `notes` for humans; `agent_notes` as freeform instructions for
  agents (timing, conditions, dependencies, "only show when"); `status` one of
  `open | done | archived` (done means completed, archived means closed without
  doing or aged out of view); `created`, `updated`; `id` as above.
- **Al's ruling:** no ontological fields. No priority, tags, dependencies or
  recurrence columns. They live in `agent_notes` as prose, so agents can wire
  things together without the schema having to anticipate them. Anything that
  genuinely needs a structured facet arrives as a mixin (decision 6), never as
  a column.
- `keywords` is optional and agent-authored at save time. It is the semantic
  layer that needs no model (decision 8).
- `done` and `archived` records are compacted into `archive.jsonl` after 30
  days by a nightly librarian, so the three active files stay small enough for
  a phone to read whole.

### 6. Structured facets are mixin files, joined on id

**Al's ruling (2026-09-03, second sitting).** A facet that programs need to
read -- the first is a trigger -- does not become a column on the record. It
lives in its own JSONL file whose rows reference the record they decorate by
id. This is normalisation, and it buys three things:

- The docket schema never grows. Every future "I wish items had X" is a new
  mixin file, not a schema change, which is the general-purpose convention Al
  wanted from the start.
- Programmatic readers read only the mixin. The dispatcher (decision 9) never
  opens `todo.jsonl`; it opens the triggers file and joins on id only when it
  decides to act.
- A mixin can attach to anything with an id, not just docket entries: a
  context document, a database record, a scope. That is what lets triggers
  generalise beyond reminders.

Mixin files are JSONL, not markdown, so the same loader, the same conflict
rule and the same index apply. The cost is referential integrity across files:
when an entry is archived, its mixin rows dangle. The nightly compaction
librarian sweeps rows whose target is closed, and the index flags orphans.
A responsibilities mixin (decision 10) and any later facet follow the same
pattern.

### 7. The derived layer moves outside the synced root; text caches stay

The binary index lives at `~/.exfu/derived/<library-id>/library.sqlite`, where
`library-id` is a short hash of the resolved library root (a moved library
simply rebuilds; it is a cache), with `EXFU_DERIVED_DIR` as an override. The
existing text caches (`index.json`, `agent-registry.json`, `agent-log.json`,
and new `channels.json` and `due.json`) stay in `exfu/derived/` because boot
and mobile sessions read them through the connector. The ontology wording
changes from "search indexes go to `exfu/derived/`" to "text caches in
`exfu/derived/`, binary indexes per machine". This corrects the gap Al
spotted: the text said "outside the synced root" and the folder was inside it.

### 8. Search without embeddings, and never recomputing what has not changed

**Al's ruling (2026-09-03):** the plugin cannot assume a user who can install
Ollama, and cannot add anything that costs per call. Every embedding path
available today fails one of those tests: Ollama and sentence-transformers need
an install, hosted APIs cost and send library text to a third party,
`model2vec` static embeddings are numpy-only but still a `pip install`, and
Apple's NaturalLanguage framework needs Swift tooling. So vectors are deferred,
and the index is designed so they slot in later without a schema break.

What ships instead is stdlib only, verified on Al's machine (Python 3.12.7,
SQLite 3.45.3 with `ENABLE_FTS5`):

- Tables `items` (every docket record across scopes: scope, kind, id, status,
  content hash, raw JSON), `items_fts` (FTS5 over title, notes, agent_notes,
  keywords), `triggers` (decision 9, with `next_at` indexed), `signals`,
  `documents` and `documents_fts` (chunked `context/` markdown), `files`
  (path, mtime, size, hash), with nullable `embedding` and `embedding_model`
  columns reserved on `items` and `documents`.
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

### 9. Triggers, signals and the dispatcher

**Al's ruling (2026-09-03, second sitting), generalising the reminder
question.** A reminder is not a special kind of record; it is a docket entry
with a trigger attached. And a trigger need not point at a docket entry at
all: it is a scope-level statement that at some moment, or on some
occurrence, *something* should be assessed by an agent. Scopes register
triggers; the index knows which are due; one cheap scheduled agent acts as the
library's cron manager and hands each due trigger to whatever it says it
needs. Reminders, email checks, follow-up chasing and "see whether the build
passed" become one mechanism with different weights.

**The trigger record.** `<scope>/triggers.jsonl`, a mixin file in the sense
of decision 6, where `target` is optional:

```json
{"id":"20260903-1502-a91c",
 "target":"20260903-1412-7f3a",
 "assess":"Surface the Acme questionnaire chase if the Acme call has happened; otherwise leave it.",
 "when":{"mode":"cron","spec":"0 9 * * 1-5","next_at":"2026-09-04T09:00:00+01:00"},
 "handler":{"kind":"agent","weight":"light","ref":null},
 "channel":"slack-dm",
 "owner":"al",
 "status":"armed","last_fired_at":null,
 "emits":["acme-chase-surfaced"]}
```

- `assess` is prose: the brief the dispatcher hands to whatever handles the
  trigger. Prose is the source of intent, as everywhere else.
- `when` is the schedule convention (decision 12) with the concrete `next_at`
  the dispatcher actually compares against.
- `handler` says how the trigger is handled, which is the information Al said
  must travel with the trigger, inline or by reference: `kind` is one of
  `surface` (deliver the target entry through the channel), `notify` (send
  `assess` through the channel), `agent` (spin up a sub-agent of the given
  `weight` with `assess` as its brief, joined to the target if any), or
  `definition` (run a registered scheduled-agent or librarian definition
  named by `ref`). `weight` is `light | medium | heavy`, mapped at dispatch to
  the cheapest, a mid, and the strongest available model.
- `channel` names a channel (decision 11); absent means pull.
- `owner` is the actor accountable for it (decision 10).
- `emits` names the signals this trigger produces when it fires (below).

**Signals: the arc between actions.** Al asked whether an email-condition
trigger implies a dependency graph between triggers, and whether there is a
simple, powerful "action, arc, action" model underneath. There is, and it is
not a dependency graph authored by hand. It is a blackboard: a fired trigger
writes a **signal** to `<scope>/signals.jsonl` (`{"id", "name", "at",
"source": <trigger id>, "payload": <small JSON or prose>}`), and any trigger
may be armed on a signal name instead of, or as well as, a time. The arc is the
signal's name. Registering "check email for the Acme reply, emit
`acme-reply-seen`" and "on `acme-reply-seen`, draft the follow-up" creates the
graph without either trigger knowing about the other, an agent can add a third
consumer without editing the producer, and the dashboard renders the implied
graph from the index rather than from a diagram anyone maintains. Explicit
DAGs (trigger B `depends_on` trigger A) are the alternative, and they are
brittle under deletion and forking; if a DAG view is ever wanted it is a
projection over signals, never an authored file.

Two guards the model needs: a trigger cannot fire twice on the same signal id
(the signal id is the idempotency key), and the dispatcher keeps a per-run
fired set with a hop limit so a trigger that emits the signal it listens for
cannot loop. Composition stays deliberately small: a trigger arms on at most
one signal name and one time window (`on: "acme-reply-seen"` plus an optional
`not_before`); anything richer is expressed in `assess` prose and judged by a
light agent, which is the "degenerate case first" path Al asked for.

**The dispatcher.** One scheduled agent, `librarians/dispatcher.md`, cadence
every thirty minutes, the cheapest model available. **Al's ruling:** it must
not boot the library and must not read anything extraneous. Its whole fast
path is: refresh the index incrementally, read the due view (one query, or
`exfu/derived/due.json` where the index is unavailable), and for each due
trigger do what the handler says: deliver, notify, or spawn a sub-agent at the
declared weight with the `assess` brief. It marks the trigger fired, writes
the trigger's `emits` as signals, computes the next `next_at` per the schedule
convention, and exits. Model tiering works in Claude Code (the Agent tool
takes a model override); whether a Cowork scheduled task can choose a
sub-agent's model is an open verification (decision 13). Desktop is the
running assumption throughout.

**What is a signal, ontologically.** A signal is a fact an agent recorded
about the world at a moment, addressed to whoever is listening. It is scope
data (synced, small, compacted by the nightly librarian after consumption),
not `durable/` (it is regenerable in principle, and it is about the world),
and not `exfu/derived/` (it is authored, not rebuilt).

### 10. Actors, ownership and the single dispatcher

Al raised two things at once: two machines running one library, and shared
scopes where different actors may need to act, and asked whether RACI or DACI
conventions belong here from the start.

**Recommendation: ownership plus a claim, not RACI.** Four or five roles per
record is exactly the ontology the docket refuses to carry, and in practice
DACI's Driver is the only role that changes what an agent does; Approver,
Contributor and Informed are communication concerns, and channels already
carry those (a `broadcast` channel *is* the Informed list). So:

- The ontology defines `actor` (a person or an agent, with a handle). Team
  libraries already have a member registry to draw handles from; a solo
  library has one actor, the one `install.md` names.
- Every trigger carries `owner`, defaulting to the library's actor. The
  dispatcher fires only triggers whose owner is the local actor, or `any`.
- A **dispatcher lease**, `exfu/derived/dispatcher-lease.json` (machine,
  actor, expiry), makes one machine the runner at a time; a laptop that sleeps
  hands over when its lease lapses. With one user, one desktop, one library,
  the lease is trivially held; it costs one small file to have the rule from
  day one.
- For shared scopes, a per-trigger **claim** (`claimed_by`, `claimed_until`)
  lets one actor pick up a fired trigger without two agents acting on it. It
  materialises on demand: the field is defined now, written only when a scope
  is actually shared.
- If a scope ever needs the full RACI grid, it is a `responsibilities.jsonl`
  mixin over decision 6, which is the argument for the mixin convention in
  one line.

### 11. Channels are declared by any scope, against an ontological interface

**Al's ruling (2026-09-03, second sitting).** The ontology defines what a
channel is; any scope may declare channels in its `scope.md` against that
interface; `user/` is just the scope where most people will declare their
default `dm`. A trigger names a channel; resolution walks the scope chain
(own scope, parents, `user/`); an unresolvable name degrades to pull, and the
dashboard shows the trigger as undelivered rather than failing it.

```yaml
channels:
  - name: slack-dm
    kind: dm
    via: slack
    target: "@al"
    send: auto
  - name: acme-team
    kind: broadcast
    via: slack
    target: "#acme-project"
    send: draft
```

- `kind`: `pull` (the dashboard and session start; always present, never
  declared), `dm` (reaches one named actor, usually the owner), `broadcast`
  (reaches several people or an unspecified audience). Al proposed these
  three; they hold, with one refinement: a message to a colleague's agent is
  `dm` to that actor, not `broadcast`, so reach is by *who receives*, not by
  medium.
- `via`: the connector that sends (Slack, WhatsApp, Gmail, a custom MCP).
- `target`: the address, never a secret.
- `send`: decision 12's consent attribute.

Which connectors are actually present on this surface is regenerable and lives
in `exfu/derived/channels.json`, refreshed at boot the way the storage backend
is detected today. This is the one thing scope.md gains, and it is
configuration about how the scope reaches people, which is descriptive rather
than state, so the "no state in descriptors" rule is respected.

### 12. Consent is a property of the channel: `draft` by default, elevated to `auto`

**Al's ruling (2026-09-03, second sitting).** Whether the dispatcher may send
unattended is decided per channel, not per send and not per trigger:

- `send: draft` is the default. The handler prepares the message and leaves it
  where the connector keeps drafts (Gmail drafts, a dashboard "ready to send"
  list); a person sends it. Some connectors only allow this anyway.
- `send: auto` means the dispatcher sends without waiting. This is the whole
  point of a `dm` to oneself: a channel whose job is to catch the user's
  attention when they are not looking cannot wait for their permission. It is
  also legitimate for pre-authorised working relationships, such as pinging a
  colleague, or their agent, for information.
- Elevating a channel from `draft` to `auto` is a decision about the library
  that nothing can regenerate, so it is recorded in `durable/ledger/` (who,
  when, which channel), which is precisely the durable membership test.
  Client-facing channels are expected to stay `draft`.

The pros and cons that led here, kept for the record: standing consent makes
automation real but lets an unattended agent send on your behalf and can spam a
channel on one misderived trigger; per-send confirmation is safe but defeats
the dispatcher and piles up unanswered. The split that resolves most of it is
self-directed versus outward reach, which is what `kind` plus `send` encode.

### 13. Schedule conventions: the trigger says how it repeats

**Al's ruling (2026-09-03, second sitting):** define the options first, and
decide implementation per option afterwards. Each trigger's `when.mode` is one
of:

| mode | meaning | who computes `next_at` | after firing |
|---|---|---|---|
| `once` | dump-and-done | the author, at creation | `status: fired`, later swept |
| `cron` | a deterministic spec (`0 9 * * 1-5`) | the dispatcher, from the spec | re-armed |
| `prose` | a natural-language rule ("every other Monday", "first working day of the month") | a light agent at fire time, written back into the record so a person can see and correct it | re-armed |
| `on-complete` | re-arm when the target entry is completed or reopened | the compaction librarian, when it sees the status change | re-armed |
| `on-signal` | fire when a named signal appears (with an optional `not_before`) | none; the signal is the moment | re-armed, idempotent per signal id |

`once`, `cron` and `on-signal` are pure script. `prose` needs the light agent,
which the dispatcher already is. `on-complete` needs the index to notice a
status change, which the incremental rebuild already does. The record carries
`last_fired_at` and `next_at`; that is the watermark, synced so every surface
and machine can see that a trigger has fired, and it is the only mutable field
the dispatcher writes on a trigger.

## Audit and council findings (2026-09-03)

Al asked for a Codex sense-check and a council reflection on decisions 9-13
before ruling on them. Three voices were run the same afternoon: Codex
(`gpt-5.6-sol`, `exfu-auditor` role via PAL clink, read-only, under the
`exfu-delegate` audit contract; verdict **revise**, 9 high, 5 medium, 1 low;
full return in `.exfu/returns/structured-worklist-audit-r1.json`), the Claude
CLI as an independent context (Sonnet, planner role), and a read-only
architect sub-agent in session. Gemini was unavailable (no CLI auth). The
three converged on the same load-bearing points, consolidated here with a
recommended resolution for each. Items marked *adopt* are corrections the
record should simply take; items marked *Al* need a ruling and are carried
into the open decisions below.

**Signals and the blackboard (decision 9).** All three voices judged the
model right and not fatal, and all three found the same holes. Signal names
must be library-global strings with scope as metadata, or the motivating arc
(a `user/` email check feeding an Acme-scope follow-up) cannot fire at all.
"Compacted after consumption" is undefinable in a blackboard because the
producer does not know who listens: `signals.jsonl` is append-only with a
flat retention window (30 days) and each trigger carries a `last_signal_id`
watermark it scans forward from, which also settles the arm-after-fire race.
The dispatcher must not write a trigger's declared `emits` blindly; the
handler returns the signals it actually observed or produced (the email check
emits `acme-reply-seen` only when a reply exists). A typo in a trigger's `on`
name fails silently and forever, so the index flags armed-on-never-emitted
names the way it flags orphaned mixin rows. The per-run loop guard does not
survive across ticks; cap fires per signal name per 24 hours and surface the
suppressed trigger. *Adopt all.*

**Crash-safe firing and the watermark (decisions 9 and 13).** Sending and
then writing `last_fired_at` duplicates on a crash; writing first loses the
send. And `next_at`/`last_fired_at` on the trigger row makes `triggers.jsonl`
the most-written file in the library, synced dozens of times a day while the
conflict fold runs nightly. Resolution: `triggers.jsonl` becomes authored and
near-immutable; fire state moves to an append-only `fires.jsonl` keyed on an
occurrence id (trigger id plus scheduled instant), written as intent before
acting and as result after, with an explicit `failed` state, a
consecutive-failure count that reuses the registry's flag-after-three
convention, and a pass-through idempotency key where a connector supports
one; at-least-once is documented where it does not. This also removes the
`prose` mode's write-back into a synced file and gives the audit trail for
free. *Adopt.* Where `fires.jsonl` lives is *Al* (open decision N).

**The half-hour cadence (decision 9).** The framework validates only
`nightly | weekly | hourly | on-demand` (`ontology.md#scheduled-agents`,
`install-scheduled-agent`), and every cadence is one platform task the user
creates by hand; 48 sessions a day on a laptop that sleeps was never costed.
Resolution proposed by two voices: run the dispatcher on the existing
`hourly` cadence and have the boot skill drain the due view at session start,
which for someone in Claude several times a day beats half-hourly cron and
adds no vocabulary. *Al* (open decision L). Cowork model selection stays
unverified (open decision I).

**Missing cron-manager semantics (decision 13).** No misfire or catch-up
policy (laptop asleep Friday to Monday: fire three times, once, or not at
all?); offsets instead of IANA time zones, so a 9am rule drifts in October;
no failed/retry state; no dry run. Resolution: one global rule, "at most once
per trigger per run, never backfill, record skipped occurrences"; `tz` as an
IANA zone name on every time-based trigger; the `failed` state above;
`exfu-index.py due --at`, `fire <id> --now` and `explain <id>` as the dry-run
surface; and a note that `on-signal` resolves within one cadence tick, not
in real time. *Adopt.*

**Five modes should be three (decision 13).** `on-complete` is `on-signal`
with the compaction librarian emitting `entry-completed:<id>`; delete it as a
mode and get it back free. `prose` is better resolved once, at authoring
time, into a `cron` or `once` spec by the saving agent than by the cheapest
model in the write path of a synced file every run. Ship `once`, `cron`,
`on-signal`. *Adopt*, which rules open decision J.

**Channels in scope.md (decisions 11 and 12).** A list of named instances
with targets and a mutable `send` flag in `scope.md` contradicts the binding
rule that scope.md carries no entity lists or state; and recording an
elevation in the ledger does not enforce it, since editing `send: auto` in
place bypasses consent, with no revocation path. Resolution: channels are a
materialised file with stable ids (open decision M says where); grants are an
append-only grant/revoke record in `durable/ledger/` that the dispatcher
validates before every `auto` send; for 0.11.0, `auto` is permitted only on a
`dm` whose target is the owner; a per-channel daily send cap and a per-run cap
that degrades to `draft` and logs when tripped bound the damage of one
misread rule. Undelivered and suppressed counts surface at session start, not
only on the dashboard. *Adopt*, with the location as *Al*.

**Ownership and the lease are ahead of their scale (decision 10).** The team
member registry the record leans on does not exist under `src/`; a lease file
in `exfu/derived/` on a sync layer with no locking can be acquired twice or
conflicted; and a global lease held by one actor blocks another's owned work.
Resolution: define `actor` in the ontology (channels need it), keep `owner`
optional, and move the lease and the claim to a "when a scope is shared"
paragraph as additive fields, which is decision 6's own argument.
Correctness rests on the fire receipts, never on the lease. *Adopt.*

**Where mixins live.** The ontology's nesting rule says a scope's root holds
folder-types, `scope.md` and `scopes/`; loose `triggers.jsonl` and
`signals.jsonl` at the root break it. Options: inside `docket/` (the docket
is the list of matters; triggers, signals, fires and channels are how matters
get heard and how the docket reaches people), or a new folder-type. *Al*
(open decision M).

**Migration (Enactment 6).** Three separate faults. `library-updater` today
stops any migration whose non-ledger writes are not under `exfu/`, so it
would refuse this one; its contract must be revised to permit declared scope
writes after consent, with inventory, reversible moves and recovery steps.
A single migration id with a per-scope condition has no partial-progress
model: a failure after creating one `docket/` makes the target-absence test
false and strands other scopes; specify an upfront inventory of applicable
scopes, a per-scope progress journal, idempotent steps, and a library-wide
`applied` only when every selected scope verifies, plus updating each
migrated scope's `exfu:` pin and `latest.txt`. And the claim that existing
`<user>-reminders`/`<user>-inbox` skills keep working against `legacy/` is
false: generated skills hard-code their original paths, commonly
`databases/reminders/reminders.md`, which the migration does not even
inventory. Discover real paths from the installed skills and folder pointers
first, preserve originals until the replacement skill is confirmed, and
regenerate the personal skill inside the attended migration. *Adopt all.*

**Smaller matters.** The conflict rule needs a common envelope for mutable
rows (`updated`, an actor/revision tie-breaker, tombstones), with signals and
fires explicitly immutable. Skipping a file on matching mtime and size can
miss same-size edits and metadata-preserving sync writes: treat them as
hints, hash when uncertain, and validate fully on a slow cadence. Ids need
ULID-strength randomness (timestamp plus at least ten random characters),
UTC generation and a collision check. `archive.jsonl` adds `kind` to a shape
that lacks it: specify the archive envelope separately. Mixin targets need a
typed, scope-qualified reference (`{"type": "docket-entry | document |
record | scope", "id": ...}`). `surface` and `notify` are one handler kind,
`deliver`, with an optional target. Chunked `context/` search (decision 8) is
a second product inside a docket release and can wait. Implementation terms
(`cron`, `signal`, `dm`, `broadcast`, `draft`, `auto`) stay internal; setup
and dashboard use plain labels ("reminder rule", "something happened", "tell
me", "tell the team", "prepare only", "send automatically"). *Adopt all.*

**Release shape.** Codex's one medium finding on scope: bundling the docket
migration with an event bus, a scheduler, an actor model, outward delivery
and consent in one release multiplies migration and safety risk. Within the
ruled single release, name a first supported slice (docket, local index,
`pull` delivery, `once`/`cron`/`on-signal` triggers, `auto` on owner `dm`
only) and ship the rest dormant until its mechanism is complete. *Al* (open
decision O).

## Open decisions

- **G. The signal model.** Ruled in principle by the audit: blackboard
  signals, with the corrections above. Al to confirm.
- **H. Ownership.** Owner optional, lease and claim deferred to shared
  scopes, per the audit. Al to confirm.
- **I. Model choice in Cowork.** Whether a Cowork scheduled task can spawn a
  sub-agent at a chosen model. If not, the dispatcher runs where it can pick
  models (Claude Code scheduled tasks) and Cowork sees the results.
- **J. Schedule modes.** Ship `once`, `cron`, `on-signal`; fold
  `on-complete` into `on-signal`; resolve `prose` at authoring time. Al to
  confirm.
- **K. Mixin sweep policy.** How long a dangling mixin row survives its
  archived target before the compaction librarian removes it.
- **L. Dispatcher cadence.** `hourly` plus a boot-time drain (recommended by
  two voices, no new vocabulary) versus a new half-hour cadence end to end
  (registry, installer, task template, runner, health, and a user-created
  platform task).
- **M. Where mixins and channels live.** Inside `docket/` (recommended: one
  folder, one `agent.md`, coherent story) versus a new folder-type such as
  `triggers/`.
- **N. Where fire receipts live.** `fires.jsonl` beside the triggers (travels
  with a shared scope; recommended) versus `durable/ledger/` (the ontology
  already names idempotence watermarks as a plausible tenant, but it is
  root-level and would not travel with a scope).
- **O. The first supported slice.** Whether 0.11.0 ships everything with the
  unfinished mechanisms dormant, or is scoped to the slice named above.

## Enactment

One release, 0.11.0 (**Al's ruling:** one big release, not three), after the
open decisions are ruled:

1. Mint a new conventions version with `build/mint-conventions.sh`; never edit
   `20260724-1910` in place. The new `ontology.md` replaces `#todo`,
   `#reminders` and `#inbox` with `#docket` (three files, record shape,
   per-file store-or-point, conflict and archive rules), adds `#mixins`,
   `#triggers`, `#signals`, `#actors` and `#channels`, extends `#scope-md`
   with the `channels:` list, and rewords the derived-location rule.
2. Templates: `defaults/docket-agent.md` (with a pointer variant) and
   `scope/docket/agent.md` replace the six todo/reminders/inbox defaults and
   three scope folders; one `docket-template.md` replaces
   `reminders-template.md` and `inbox-template.md`.
3. Scripts, stdlib only: new `scheduled-tasks/library-index/index.py` (SQLite
   build, incremental hashing, `query`/`due`/`rebuild`, `due.json` emission,
   dispatcher lease); `substrate-index` learns the one folder-type and
   per-file status; `dashboard-generator.py` renders one Docket section from
   records plus the trigger and signal views, and drops `CHECKBOX_RE`,
   `classify_reminder_date`, `split_reminder_entries` and `POINTER_PHRASES`.
4. Librarians: `inbox-triage` becomes `backlog-sweep`; add `docket-compact`
   (archive, conflicted-copy fold, mixin sweep, signal compaction) and
   `dispatcher` (thirty-minute cadence, cheapest model); register all three in
   `templates/agent-registry.json`.
5. Skills: `exfu-library` Steps 3 and 14 (`channels.json`, JSONL reads,
   index-aware, a one-time nudge to re-run setup); `scope-setup` Steps 3-5
   and channel declaration; new `setup-docket` replacing `setup-reminders`
   and `setup-inbox`; `daily-briefing`; the three install skills;
   `exfu-guides`; `substrate-guide.md` to v14 with its changelog line; the
   primers.
6. Migration `exfu/migrations/<ts>-docket.md`: `requires_user_decision: true`,
   `reversible: true`, `conventions: "20260724-1910 -> <ts>"`, `applies_when:
   <scope>/docket/ absent while any of todo/, reminders/, inbox/ holds content`
   (the target's absence, per the ontology). It creates `docket/agent.md`
   carrying each old folder's pointer lines over as per-file lines, converts
   checkbox lines, reminder entries and inbox files into records with the
   saving agent deriving `keywords` and, for dated reminders, a `once` or
   `prose` trigger, moves the three old folders whole into `docket/legacy/`,
   and records the outcome in the ledger. Existing `<user>-reminders` and
   `<user>-inbox` skills keep working against `legacy/` until the user
   re-runs setup. Rebuild `example/` through it.
7. Bump the three manifests to 0.11.0, write the CHANGELOG entry in house
   style with a link back here, `./build/build.sh all`, capture, commit.
