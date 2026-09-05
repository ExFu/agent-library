---
name: setup-docket
description: First-time setup for the user's personal docket skill -- the one place for their reminders, quick captures and things they leave for their agents. Run this when the user wants to set up reminders or capture for the first time -- "set up reminders for me", "give me a way to nudge myself later", "I keep forgetting things, fix that", "give me somewhere to capture stuff", "I keep losing thoughts", "set up quick-capture", "set up my docket", or any first-time reminder or capture setup intent. Also run it when a user with an older personal reminders or inbox skill asks to move to the docket. Not for creating individual reminders, capturing a thought, or checking what's due (those are handled by the user's personal docket skill, typically named after them, e.g. al-docket).
---

# Setup -- Docket

## Why this exists

Reminders and quick captures are the things people most want Claude to hold for them: "remind me to check on this next Monday", "don't let that slip", "save this, I'll sort it later", "have my agents look at this". They all have the same shape -- something open, and a moment or a condition when it should be heard -- so they live together in the user's docket (`ontology.md#docket`): one folder, one line per entry, read whole from any surface including a phone.

This setup skill is a one-shot conversation. By the end the user has a personal `<username>-docket` skill installed in their Claude. That skill knows where their docket lives, their time zone, where they want reminders to reach them, and what to say at session start. After that, they never need to run this setup again. Everything ongoing -- setting reminders, capturing, completing, snoozing, reviewing what has piled up, the session-start check -- happens through their personal skill.

**If the user already has a `<username>-reminders` or `<username>-inbox` skill**, say plainly that this one replaces both, and that their old reminders and inbox files are read by the docket migration (offered by the library-updater), not by the new skill. Nothing they wrote is lost: the migration converts it and keeps the originals in `docket/legacy/`. Don't run the migration from here; if their library still has the old folders, tell them the tidy-up is available and their librarian can run it when they are ready.

---

## The intake

Walk through these in conversation. Don't present them as a list. Pick up the thread naturally based on what the user says, and use plain words: "your docket" only once they have one, "reminder rule" not "trigger", "send automatically" or "prepare only" not "auto" or "draft".

### Where the docket lives

The standard location is `user/docket` inside their library -- their personal space, where most people keep their own reminders and captures. Confirm that's where to put it. If they want a different scope's docket to be their everyday one (rare; a solo consultant whose one client scope is where everything happens), capture that path instead.

If the folder doesn't exist yet, create it now through `scope-setup` Flow B (it scaffolds `docket/agent.md` and `readme.md`; entry files appear on first entry). Note the scope's name from its `scope.md` -- `user` for the personal space -- because the generated skill writes it into trigger targets and signals.

### Time zone

Every reminder rule carries an IANA zone name (`Europe/London`, `America/New_York`) so a 9am reminder stays at 9am when the clocks change. Ask once, in plain terms: "Which time zone should reminders use? I'll take London unless you say otherwise." Infer it from what they have told you (their about-me, their city) and confirm rather than asking cold. Capture the IANA name, never an offset.

### Where reminders should reach them

By default, reminders surface in the session and on the dashboard: the user opens Claude, and what's due is there. Ask whether they want more than that:

> "Want reminders to reach you somewhere too -- Slack, WhatsApp, email? Or is telling you when you open Claude enough?"

If they name one, ask the consent question, and explain it before they answer:

> "Should your agents send there automatically, or only prepare the message for you to send? Automatic means they can message you at that address on your behalf without asking each time; you can take that back later."

- **Prepare only** is the default. Record a channel row in `<docket path>/channels.jsonl` per `ontology.md#channels`: a library-wide id, a `name` (e.g. `slack-dm`), `kind: dm`, `via` the connector, `target` their address (never a secret), `send: draft`, and the envelope (`created`, `updated`, `revision: 1`).
- **Automatic**: the same row with `send: auto`, **and** a grant appended to `durable/ledger/grants.md` in the shape of `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/grants.md` -- channel id, name and scope; the date; who granted it, on which surface, at which plugin version; and what they said in their words. The grant is what authorises sending; the flag alone grants nothing. Only a message to the user themself is sent automatically in this release; if they ask for automatic sending to someone else, record it, and say it will be prepared rather than sent until a later release.

If the connector they name isn't available in this session (see `exfu/derived/channels.json`), record the channel anyway and say the dispatcher will use it where the connector exists; here, reminders fall back to the session. If they don't want a channel, don't press; the session and the dashboard are always there.

### Surface on load

The docket check runs at session start. The default: surface what's due or overdue, the count of things waiting for their agents, and anything stuck; say nothing if there is nothing. Ask if they want to adjust it:

- Some prefer: "always tell me how many open reminders I have, even if nothing's due."
- Some prefer: "only mention something once it's overdue by more than a day."
- Some prefer: "don't mention the backlog at session start; I'll ask."

Capture the preference as one short paragraph in their words. If they're fine with the default, leave it empty.

### Anything else

Any other preferences? A default reminder time other than 09:00, a habit of leaving things for agents with instructions attached, a task tool the docket should hand tasks to. Keep this brief. If nothing comes up, move on.

---

## Generate the per-user skill

Once you have the intake answers:

### 1. Determine the username

Read `durable/ledger/actors.md` first: if it has a record, its first heading is the handle, and the username is that handle. Otherwise read `user/context/about-me.md`, look for their name, and default to first-name-lowercase (e.g. "Alastair" becomes `al`, or whatever handle is clear from the file). If the name is ambiguous or neither file exists, ask: "What should we call your docket skill? Something like `al-docket` or `sarah-docket` -- first name or nickname is fine."

**Record the actor if no record exists.** Triggers carry the handle as `owner`, and the dispatcher fires only what resolves to the library's actor, so the handle needs a home before the first trigger is written. Append a record to `durable/ledger/actors.md` in the shape of `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/actors.md`: the handle as heading, their display name, the aliases they go by (ask: "Any other names you go by that an agent might write down? First name, nickname, initials?"), and the ids of any channel that reaches them directly (the Slack member id behind a `dm` channel, their email). Every name listed there resolves to the handle, so a trigger written under "Alastair" fires for `al` instead of failing silently.

The per-user skill will be named `<username>-docket`.

### 2. Read the template

Read the docket template from `${CLAUDE_PLUGIN_ROOT}/templates/docket-template.md`. It contains all the operational logic for the docket skill. Fill every placeholder with what the intake captured:

- `{{username}}` -> the resolved username
- `{{docket_path}}` -> the confirmed path, relative to the library root (e.g. `user/docket`)
- `{{scope_name}}` -> the name of the scope that docket belongs to, from its `scope.md` (e.g. `user`); it goes into trigger targets and signals
- `{{tz}}` -> the IANA zone name
- `{{conventions}}` -> any custom preferences from the intake, phrased as brief bullet points (a default reminder time, a task tool, a capture habit). If nothing unusual, leave it empty so the template's default conventions apply.
- `{{surface_on_load}}` -> the surface-on-load preference as a short paragraph, or empty for the default

Read the filled skill back once. Every `{{` must be gone.

### 3. Package and present

Use `skill-packaging` to package the filled-in template as a `.skill` file named `<username>-docket`. Present the install link to the user. Walk them through installing it if this is their first time with skill packaging. Keep the source in `user/skills/<username>-docket/` so it can be regenerated later; `skills/` materialises at that moment if it hasn't already.

---

## Hand-off

Once the skill is installed, this setup is done. Going forward:

- Setting reminders ("remind me to X on Y", "don't let me forget Z") -> `<username>-docket`
- Capturing ("save this", "jot this down", "leave this for my agents") -> `<username>-docket`
- Session-start check for what's due, called by `exfu-library` -> `<username>-docket`
- Completing, snoozing, dropping, reviewing the backlog -> `<username>-docket`
- Firing reminders through a channel on a schedule -> the `dispatcher` librarian, once registered (`install-scheduled-agent`); until then, reminders surface when the user opens Claude

If the user ever wants a fresh setup -- a different location, time zone, channel or surface-on-load behaviour -- they can re-run `setup-docket`. It regenerates the skill. Their docket files and everything in them are never touched by a re-run; a channel change is a new row or a revoked grant, appended, never rewritten.

---

## Dependencies

- `skill-packaging` -- used to package and present the generated skill.
- `scope-setup` -- creates the docket folder if it doesn't exist yet (Flow B).
- `exfu-library` calls the user's docket skill (by name) at session start if it is installed.
- The template at `${CLAUDE_PLUGIN_ROOT}/templates/docket-template.md` contains the operational logic.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/grants.md` -- the shape of a grant entry, when a channel is set to send automatically.
- `${CLAUDE_PLUGIN_ROOT}/substrate/templates/durable/ledger/actors.md` -- the actor record: the handle triggers carry as `owner`, and the names that resolve to it.
- `exfu/<version>/ontology.md#docket`, `#triggers`, `#channels` and `#grants` -- the contract the generated skill follows.
