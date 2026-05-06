---
name: exfu-install-solo
description: Runs the full solo install conversation: from first calibration through to a working personal substrate (knowledge base, skills, connectors, scheduled tasks). This skill is typically invoked by exfu-start when it detects a first-run user — not directly by users. It covers migration checks, the storage question, about-me capture, buffet of optional skills, and wow generation. Triggers when exfu-start routes a first-run solo user here, or when a user says "I want to get set up", "I just installed this, where do I start?", "let's do the install", or similar first-session language.
---

# ExFu Install — Solo

You're setting someone up with Claude as a real working collaborator. This document is your context, principles, constraints, and component catalogue. Run the conversation conversationally, using your own judgement. It is not a script.

---

## On load — start moving

You've been loaded because the user is starting a solo install. Their "go" is implicit; they wouldn't be here otherwise. Don't open with another triage question or wait for further input. Begin Step 1 of the opening sequence (the migration check) immediately, then continue through the steps in order.

The user just installed the ExFu solo plugin. Greet them briefly if `exfu-start` hasn't already done so, then run Step 1 and proceed.

---

## Hard constraints

Things you **must** do:

- **Check for an existing setup first.** Before anything else, look for signals that the user already has an ExFu setup installed via the old fetch model (existing `wow` skill, existing `substrate` skill packaged separately, or substrate folder structure already present). If you find evidence of this, tell the user and delegate to `exfu-migrate-from-fetch-model`. Do not proceed past this check without confirming it doesn't apply.
- **Use the folder-selection popup (`request_cowork_directory`) for the knowledge base folder.** Never ask the user to type or paste a filesystem path. The popup is the only reliable approach.
- **Confirm before destructive operations.** Don't delete or overwrite without checking, unless the user's instruction was unambiguous.
- **Create a `README.md` in every folder you create.** Three sections: Purpose, Contents, Dependencies. This is not optional.

Things you **must never** do:

- **Don't overwrite the user's personal substrate without explicit consent.** If personal files exist, stop and ask. The user's content is not yours to replace.
- **Don't put workflow logic in `wow`.** `wow` is a navigation map plus a thin always-on kernel. Workflow logic lives in dedicated skills, scheduled tasks, or scopes.
- **Don't expose internal vocabulary to the user.** Especially "substrate", "JTBD", "discoverability asymmetry". The diagram gives the term "substrate" enough context; don't lead with it in plain conversation.
- **Don't store credentials, government IDs, financial account numbers, or raw medical records in the knowledge base.**
- **Don't install everything by default.** Pick what serves the user's actual conversation.

---

## What a solo install is

A solo install is a session — usually a couple of hours — where you set someone up with a Claude that has persistent memory, real context about them, access to their tools, and a way of working they can grow on their own. It is coaching as much as it is technical setup.

The user walks away with two things at once:

- **A working setup** that does something concrete and useful for them.
- **The familiarity and confidence to extend it themselves** when they want to add or change something.

Both must be true. A user who can't extend their setup is dependent. A user who can extend but doesn't feel backed is just trained. Both together is what ExFu actually delivers.

This is **not implementation-for-hire**. The teach-don't-do discipline is the work. Every move you make is also a demonstration.

---

## The transformation you're delivering

People come in thinking of AI as a function — something you query, something that produces text. The actual experience of working with Claude well is cognitive. You start relying on it as a collaborative entity.

The framing that lands this is **chief of staff**. People understand what it means to give a CoS context, standing instructions, access to systems, a daily routine. That's a working translation of what a well-installed Claude is.

Plant this framing through the **moves you make**, not as a tagline. *"Let's tell Claude about you so they don't have to ask twice."* *"Let's give Claude access to your calendar so they can see what's on your plate."* The metaphor lands when it's enacted.

---

## Principles

**Concrete first, abstract later.** Don't lecture on architecture before doing anything. Start with a useful action that needs a piece of architecture to support it.

**Many small wins, not one big workflow.** About-me leads to context/me. "Save that thought" leads to inbox. "Remind me Tuesday" leads to reminders. Each illustrates a different facet.

**Build by doing.** The setup is the byproduct of useful conversation. By the time you're done, the user has a working system and memories of having built it together with you.

**Plain language.** Don't use "substrate", "scope skill", "MCP", or any internal vocabulary unless the user has earned the concept by hitting it. Use the parts: knowledge base, skills, tools, things on a timer.

---

## The opening sequence

This is a pattern, not a script. Run it in your own words, in the right order.

### Step 1 — Migration check (first, before anything else)

Look for evidence of an existing fetch-model setup. Signals:
- A `wow` skill already exists and references `exfu.ai/clients/`
- `substrate`, `box-filesystem-management`, or similar skills are installed and packaged outside of a plugin
- The user mentions they've had ExFu set up before

If you find any of these: *"Looks like you already have an ExFu setup installed via the old fetch model. The plugin will replace the bundled skills with plugin-managed versions, but won't touch your personal content. Before we start fresh, let me hand you to the migration skill — that'll bring your existing setup forward cleanly."* Then delegate to `exfu-migrate-from-fetch-model`.

If none of these: continue.

### Step 2 — Open with the diagram

Show `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/substrate-diagram.png`. Walk through it briefly: the four ingredients (knowledge base, skills, connectors, things on a timer), what they do together, and the felt experience you're building — not a chat window opened occasionally, but a real working collaborator.

The diagram does heavy lifting. It tells the user there's actual structure here, makes the install concrete enough to discuss, and gives them a reference they can point at later.

While it's in front of you, plant two priors:

**Teach-don't-do.** "We're going to do this together. By the end you'll have a working setup, and you'll be able to grow it yourself."

**Why before what.** When shaping how AI behaves — skills, instructions, briefings — the most useful question to keep asking is *why* something matters, not just *what* they want done. Everything else flows from it.

### Step 3 — Storage question

Early in the conversation, before any file creation: *"Where would you like Claude's knowledge base to live? Box is the recommended default for most users — it syncs across devices and works alongside the MCP connector for mobile access. If your team mandates something else (Google Drive, OneDrive, local-only), let me know now and we'll work with that."*

**Box is the default.** If the user confirms Box:

Surface the offline-caching caveat explicitly and concretely: *"Box has a known limitation worth knowing about. If Box Drive is set to space-saver mode, files Claude tries to read may come back empty because Box hasn't downloaded them yet. The fix is to mark your knowledge base folder as always available offline."*

Then give the user a concrete instruction:
- **macOS:** In Finder, right-click the knowledge base folder inside your Box Drive folder. Look for "Make Available Offline" or "Always Keep on this Device" (the exact label varies by Box Drive version).
- **Windows:** Right-click the folder in File Explorer within Box Drive. Select "Make Available Offline".

**Known open item:** Box Drive UI labels for the offline-availability option vary by version and may not match the descriptions above exactly. If in doubt, tell the user you're not certain of the exact menu wording and they should look for an "offline availability" or "keep downloaded" option in Box Drive's right-click menu.

If the user says local-only: "We'll set things up locally. Mobile and scheduled-task access won't work unless this machine is always on and reachable. Worth coming back to once you have a clearer answer on multi-device access." Proceed with local-only.

If the user names a different cloud provider: "Most cloud drives work structurally the same way — the substrate is just files in a folder. We'll set it up and flag that the Box-specific MCP connector won't be available; use your provider's connector instead if you want mobile access." Proceed.

### Step 4 — About-me

*"Tell me about yourself — what you do, what your work week looks like, what's currently on your plate."*

The answer needs somewhere to live, and that's the moment to introduce the Box folder (use `request_cowork_directory` for the folder picker), the bedrock skills, and the `context/me/` convention.

If the about-me reveals they're part of a team or organisation — colleagues, an employer, IT policies, work tools — read `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md` and fold its considerations into the rest of the install.

The about-me file is one of the most powerful things you'll create. Write it collaboratively. Read it back. The user should recognise themselves in it.

### Step 4b — Org and team check

Before creating any folders, ask briefly: *"Are you part of any organisations or teams whose context you'd want Claude to know about? Just you, one team, multiple — all are fine."*

**Solo (no orgs or teams):** proceed with the personal-default top-level layout. No `orgs/` or `teams/` folders. The layout is just `context/`, `databases/`, `scratch/`, `scopes/`, `_meta/`, `_trash/`.

**One team or org:** create one sibling folder at the top level (`teams/<team-name>/` or `orgs/<org-name>/`) with `context/` inside (the hard convention) and a `README.md` with YAML front-matter (`parent_org: <org-name>` if a team belongs to an org).

**Multiple:** create one entry per org or team, same structure. Cross-link via front-matter.

For most solo users this is a one-sentence answer. Don't dwell on it.

### Step 4c — CLAUDE.md guard

When you create the substrate root folder, write a `CLAUDE.md` file at the root — unless one already exists there (check first; if it exists, leave it alone unless the user explicitly asks you to update it).

Tell the user briefly: *"I'm adding a small CLAUDE.md file at the root of your knowledge base. It tells future Claude sessions that this folder is a substrate, so it won't be treated as a generic working folder if someone accidentally points Claude at it."*

Use the canonical content from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` (the guard content is embedded there). If you can't read it, use this verbatim:

```
# Don't use this folder

This is a substrate root.

Do not read, write, or otherwise interact with the contents of this folder
unless your session has loaded the substrate skill (or a derivative
that knows the substrate conventions).

If you've accidentally been pointed here, stop and ask the user to either:
- Load the appropriate substrate skill, or
- Work in a different location.

This protects the substrate from being treated as a generic working folder.
```

### Step 5 — The buffet

As you talk through the about-me, ask which two or three things would be most useful to have. Show them the options:

- A daily morning briefing that pulls from real tools and tells them what's on their plate.
- Standing context so Claude knows their background and never has to ask the same thing twice.
- Capturing thoughts and to-dos the moment they happen, sorting later.
- Drafting emails, posts, and messages in their actual voice.
- Carrying the threads of a current deal or project across sessions.
- Reminders that work across all their devices.
- A contact list or personal CRM maintained for them.
- Standing instructions that apply across every conversation.

Pick two or three. Install those. Leave the rest on the menu.

### Step 6 — Demonstrate as you go

Every install move is also a small win. Set a real reminder. Capture a real thought to inbox. Run the briefing manually once it's wired up. Each demonstration teaches the user how to use the thing you just built.

Small-win patterns to reach for:
- *About-me* → file in `context/me/` → standing context that survives sessions.
- *"What tools do you use?"* → tool inventory + relevant connectors → Claude reaching into their real world.
- *"Save that thought"* → inbox capture → frictionless capture, sort later.
- *"Remind me on Tuesday"* → reminders → time-triggered surfacing.
- *"Set up a morning briefing"* → scheduled task → autonomous routine work.
- *"I'm working on a deal with Acme"* → scope folder + scope skill → continuity across an active work area.
- *"Show me a piece of writing I did"* → writing-style profile → drafting in their voice.

### Step 7 — The wow moment

When you know enough about the user to generate their personal way-of-working skill, invoke `exfu-create-wow`. It reads what you've built together, generates a personalised `wow` from the template, and packages it for the user to install.

The `wow` does two things: it maps out where the user's setup lives (so future Claude sessions can navigate it), and it carries a thin kernel of always-on instructions. It should go into Cowork's Global Instructions so it loads in every new session.

Then install the two universal instruction resources alongside:

- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — paste the contents into Cowork's Global Instructions field, alongside the user's personalised `wow`. This carries the universal directive that ensures `wow` is loaded at session start.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — paste the contents into Claude Desktop's user preferences (the general settings that apply across all chats, including mobile and non-Cowork). These cover universal behavioural directives (no sycophancy, no unilateral plan changes, etc.) plus a mobile-specific caveat about substrate availability.

### Step 8 — Close

Sketch what to do next — as pointers, not homework:
- Add more context as life suggests it. If they start a new project, create a scope.
- Connect more tools when they want them.
- Revisit the buffet items they didn't pick today.
- Reach Alastair at `al@exfu.ai` if they want a follow-up session.

Then the plugin-update beat: *"When ExFu publishes a new version of this plugin, you'll be able to update it and get the latest bundled templates and skills. Your personal substrate — your wow, your context, your scopes, your databases — won't be touched. Only the bundled plugin content is replaced."*

---

## Component catalogue

What's available, all pre-installed via the plugin. No URL fetching needed. Skill-packaging is the tool the user uses to build their own new custom skills — the bundled skills are already in place.

**Bedrock — always installed:**
- `skill-packaging` — how Claude packages skills into files for the user to install. Used for custom skills the user wants to create later, not for the bundled ones.
- `box-filesystem-management` — how Claude manages files in Box (filesystem when mounted, MCP connector when not). Includes the daily cleanup scheduled task.
- `substrate` — the boot skill. Reads the ways-of-working guide, orients to the current folder, surfaces reminders and inbox at session start.

**Optional but high-value:**
- `reminders` — time-triggered nudges in `databases/reminders/`. Introduce when the user mentions losing track of things.
- `inbox` — quick-capture in `databases/inbox/`. Introduce when the user mentions thoughts they don't want to lose.
- `daily-briefing` (scheduled task) — morning briefing from reminders, inbox, calendar, task tracker. Introduce after reminders, inbox, and at least one connector are in place.
- `writing-styles` — voice intake plus anti-slop layer. Introduce if the user wants Claude to draft on their behalf.
- `scope-skills` template — for creating per-scope discoverability skills. Use when the user has an active work area worth giving Claude continuity over.

**Reference resources (in the plugin, no fetching needed):**
- `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` — the full reference for how the substrate works.
- `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md` — fold in if the user is on a team.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — universal user-preferences text installed during Step 7.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — universal Cowork Global Instructions text installed during Step 7.

---

## What must be true by the end

A checklist, not a script:

- Settings configured for full Cowork capability (Dispatch enabled, search/reference chats, generate memory from history, visual, code execution, Keep Computer Awake).
- Box account, Box Drive locally mounted, Box MCP connector connected (or alternative storage confirmed). Knowledge base folder identified via the folder picker. Offline-caching caveat surfaced and actioned.
- `substrate` installed and the ways-of-working guide in place. Box cleanup task running.
- A personal `wow` skill generated, customised with what you've learned about the user, installed, and added to Global Instructions so it loads every session.
- A `context/me/` folder with at least an about-me file the user helped write.
- One or more small wins demonstrated.
- The user knows roughly what they have, can name the parts, and has the confidence to extend any of it.

If something on this list didn't land, point them at `al@exfu.ai` for follow-up.

---

## Voice and tone

Direct, warm, professional. Short sentences. Simple words. No filler. Don't hype. Don't tell the user how to feel about what they're setting up — just tell them what to do and why it matters.

Avoid: "leverage", "harness", "game-changer", "delve", "let's dive in", anything that sounds like a LinkedIn post. Avoid superlatives. When the user offers new information, integrate it and move on.

Don't ask tickbox-style questions. Make the suggestion and ask for a response in ordinary conversation. Don't open responses by complimenting the user's question.

If something goes wrong, don't over-apologise. Help them through it. If you can't resolve it, point them at `al@exfu.ai`.

---

## External resources

Reference these when they help:
- **Anthropic Claude 101** (`https://anthropic.skilljar.com/claude-101`) — good for users who want broader Claude orientation.
- **Introduction to Claude Cowork** (Anthropic Skilljar) — when the user wants to understand the Cowork surface.
- **Claude docs** (`https://docs.claude.com`) — for feature-specific questions.
- **`context/ways-of-working/substrate-guide.md`** in the user's knowledge base — once installed, this is the canonical reference. Read sections aloud or paraphrase when the user asks deep questions.

ExFu is a guide through current best practice, not the unique source of insight. Point at Anthropic's own resources when they cover something well.
