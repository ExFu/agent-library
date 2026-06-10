# T3 -- Dashboard actions and the trigger mechanism

Buttons that make the dashboard act: re-run the index, regenerate the page, re-run a failing maintenance job. Underneath them, the real problem this plan exists to solve: how a click in a static local HTML file causes agent work, on the user's subscription allowance.

**Parents:** `T2-exfu-dashboard.md` (domain), `M2.1-exfu-dashboard.md` (milestone)
**Prerequisites:** T3-dashboard-generation (the bundle the buttons live in)
**Status:** added 10 June 2026 after Al's review; mechanism research completed the same day (sources inline below). Remaining before build: the end-to-end demos in "Mechanism verification".

---

## Why

The dashboard shows last-known state. The moment it shows something stale or failing, the user's next move is "refresh it" or "re-run that" -- and today that means switching to a Claude conversation and asking. A button collapses that round trip. Without one, the dashboard teaches users that looking at it creates chores.

The constraints that make this hard: ExFu users are non-technical people on Claude subscriptions. Whatever a button triggers must run on their existing plan's allowance -- never metered API billing, never an embedded API key, nothing that phones home. **The Claude Code CLI cannot be assumed to exist on their machines; Claude Desktop is the target platform.** And the dashboard is a static file; it has no server behind it.

---

## How

### Two classes of action

**Deterministic actions** are scripts. Re-running the index (`index.py`) and regenerating the dashboard data are pure script executions -- the librarian inversion already treats these scripts as tools. No agent, no tokens, no allowance question. Anything that can execute a local process can serve these.

**Agent actions** need a Claude session applying judgement: triage the inbox, run a full cadence, investigate a failing job. These are where the trigger problem lives.

### The trigger problem -- researched 10 June 2026

A static page on `file://` cannot execute processes or hold credentials. Something must bridge click to execution. The verified mechanism landscape (sources: code.claude.com docs -- routines.md, deep-links.md, channels.md, changelog.md -- plus the live trigger API confirmed working against Al's account):

1. **Claude Desktop deep links: `claude://`** -- the Desktop app registers its own URL scheme (distinct from Claude Code's `claude-cli://`, which we cannot assume exists). `claude://cowork/new?q=<url-encoded prompt>` opens a new Cowork session with the prompt pre-filled (up to ~14k characters); `claude://claude.ai/new?q=...` does the same for chat. The user confirms by sending -- one click of friction, and they see exactly what they're asking Claude to do. A dashboard button can be a plain `<a href>`: *zero infrastructure, no tokens, no daemon*, and the resulting session is **interactive**, so it runs on the subscription allowance. Folder parameters always trigger a security confirmation; the prompt should tell the session to load the substrate skill rather than pass paths. The v1 mechanism for agent actions. (Source: support.claude.com article "Open Claude Desktop with a link".)

2. **Routines with an API trigger (`/fire`).** First-party cloud automation (research preview since April 2026): a routine can carry a schedule trigger, a GitHub trigger, and an on-demand API trigger -- POST to the routine's `/fire` endpoint with a per-routine scoped bearer token; a fresh cloud session spawns and returns its claude.ai URL. Verified live: the trigger API responds on Al's account. Fully hands-off and needs no CLI, but: the token must not live in the page (it's a file in a synced folder), so this route needs the action server holding the token -- and it bills to the programmatic credit pool, not the subscription allowance (below).

3. **Channels** (research preview since March 2026): push events into an already-running session via Telegram/Discord/iMessage/custom MCP. Powerful, but requires a persistent open session on the user's machine -- wrong shape for non-technical users. Noted, not pursued.

4. **A tiny local action server** ("the helper" -- distinct from `agents.py`, the cadence session's due/record script). A localhost-only process (Python stdlib, shipped with the plugin) serving the dashboard folder plus an allowlisted set of action endpoints. Required for *instant deterministic* actions (click "refresh" -- index re-runs, data file rewrites, page reloads) and for holding the routine token if mechanism 2 is wanted. Lifecycle, verified: Cowork sessions can start local processes via shell, and **child processes survive the session that spawned them** -- so a Cowork session (or the nightly scheduled task) can start the helper and it keeps serving after the session ends. v1 can simply have Al start it manually; later, the install conversation registers it properly (login item or started-by-cadence), with care not to orphan duplicates.

5. **A request-file queue.** A request written into the substrate (e.g. `exfu/derived/requests/<timestamp>-<action>.json`), consumed by the next agent session: the nightly cadence, or any conversation via the substrate skill ("you have 2 pending dashboard requests"). Zero infrastructure, offline-safe, no billing surprises -- but asynchronous. The baseline that always works.

6. **Rejected:** `claude -p` per click (requires the CLI we can't assume, spawns a cold programmatic session per press, and bills to the credit pool); embedded API keys (billing model and secrecy both wrong); any hosted webhook relay (violates "nothing phones home"). Neither Claude Code nor Claude Desktop has inbound webhooks or a local trigger API; routines' API trigger is the first-party equivalent.

### Billing reality (changes 15 June 2026)

Anthropic splits usage into two buckets on 15 June 2026: **interactive** sessions (terminal/IDE Claude Code, claude.ai chat) stay on the subscription allowance; **programmatic** usage (headless `claude -p`, Agent SDK, cloud sessions, routines, GitHub Actions) moves to a separate monthly credit pool included with the plan (reported ~$20 Pro / $100 Max 5x / $200 Max 20x -- figures not yet in an official table), with overage at API rates.

Consequence for this plan (Al's steer, 10 June): the goal is that users are never billed *extra* by default on top of their subscription. The included programmatic credit pool satisfies that -- routine-fired actions draw included credit, and overage requires explicitly enabling usage credits, so there is no silent extra bill. That makes routines a legitimate default-capable path, not just an opt-in: real buttons doing real things is the direction. Deep-link actions (interactive allowance) remain the zero-infrastructure path; the install conversation should say one honest sentence about which pool each kind of button uses.

### The composite (v1 direction, Desktop-first)

- **Deterministic actions** -- the action server runs the script instantly. No server running? The button falls back to a `claude://cowork/new` deep link ("ask Claude to refresh the index").
- **Agent actions** -- a `claude://cowork/new?q=...` deep link with the action prompt pre-filled: interactive, subscription-priced, one confirmation click, fully transparent. Every agent action also writes to the request queue as the no-infrastructure fallback, and the nightly cadence clears anything unactioned.
- **Routine `/fire`** -- the "instant, hands-off" path, default-capable: it draws the plan's included programmatic credit, and overage cannot happen without the user explicitly enabling usage credits. Needs the action server to hold the routine token. This is the direction of travel -- real buttons doing real things.

The dashboard's UI language stays honest about which happened: "refreshed" versus "sent to Claude -- confirm it there" versus "queued for tonight".

### Rendering inside Claude Desktop (parked, promising)

Could the dashboard live *inside* Desktop instead of a browser? Findings (10 June 2026):

- **Artifacts** render full HTML/React in-conversation, but cannot read local files, and buttons cannot invoke Claude's tools -- there is no documented `window.claude` bridge; a button can only stage a message the user sends. An in-chat dashboard would need Claude to inject the data each time it renders. Usable as a party trick ("show me my dashboard"), not as the persistent artefact.
- **MCP Apps** (research preview, January 2026): third-party interactive UI panels inside the chat window, iframe-sandboxed, with *host-managed tool approvals*. A local ExFu MCP server could, in principle, serve the dashboard as an in-chat app whose buttons call MCP tools -- real interaction-to-agent-work, inside Desktop, on subscription. This is the genuinely interesting future path, and exactly the shape of the plug-and-play visualisation question. Parked until the browser dashboard proves the views; revisit as its own T3 when MCP Apps exits research preview.
- **The browser remains the v1 surface**: the substrate is a folder, the dashboard is a file in it, and `file://` plus the action server ask nothing of the user's Claude setup.

### Note on Claude Code hooks

Claude Code "hooks" are outbound lifecycle hooks (events inside a running session triggering local commands). They are not inbound webhooks; a web page cannot call one. They may still help at the edges (e.g. a session-start hook noticing the request queue), but they are not the trigger mechanism.

---

## What to build (once the mechanism verifies)

1. **Action buttons in the dashboard app** -- refresh (deterministic), re-run per maintenance job, "ask Claude to look at this" on failing jobs. Buttons render only when their serving mechanism is present; a plain `file://` open with no helper shows the read-only dashboard unchanged.
2. **The helper** (if the composite stands): stdlib-only, localhost-bound, allowlisted actions, no credentials, logs what it ran into the run log.
3. **The request queue convention**: file format, where it lives under `exfu/derived/`, how sessions acknowledge and clear requests, and how the dashboard renders pending requests.
4. **Trigger wiring** for agent actions per the research outcome.

---

## Mechanism verification (exit criteria)

1. ~~Which invocation modes run on subscription allowance, with sources~~ -- **done, 10 June 2026** (see "Billing reality" above; re-verify the credit-pool figures against official docs once Anthropic publishes the table).
2. A working end-to-end demo of a deterministic action: dashboard button to re-run index to refreshed view, on Al's live substrate (action server path, started manually).
3. A working end-to-end demo of a deep-link agent action: dashboard button to Claude Desktop opening Cowork with the pre-filled prompt to confirmed to work done -- on a machine with no Claude Code CLI installed.
4. The request queue convention exercised once: a queued request consumed and cleared by a nightly session.
5. A decision recorded here after the demos: the composite above confirmed, simplified, or replaced, with reasoning.

---

## Where this plan lives

- This file: `plugin/planning/T3-dashboard-actions.md`
- Domain: `plugin/planning/T2-exfu-dashboard.md`
- Milestone: `plugin/planning/M2.1-exfu-dashboard.md`
- The bundle the buttons live in: `T3-dashboard-generation.md`
