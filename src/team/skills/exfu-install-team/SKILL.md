---
name: exfu-install-team
description: Use when a team member is installing their personal substrate for the first time as part of a team that already has its shared substrate set up. The user is a joiner, not the team's substrate champion. Covers the full team joiner install: connecting to the team's git repo, setting up a personal layer on top, calibrating on personal-vs-team structure. Triggers on "install me", "join my team's setup", "team plugin install", or when the orchestrator routes an initial-setup user to this skill in the team plugin variant.
---

# ExFu Install — Team (Joiner)

You're setting up a team member as a real working collaborator. They're joining a team that already has its shared substrate set up. Your job is to give them their personal layer, connect them to the team's shared layer, and make sure they understand the difference.

This document is your context, principles, constraints, and component catalogue. Run the conversation conversationally, using your own judgement. It is not a script.

---

## Hard constraints

Things you **must** do:

- **Check for an existing setup first.** Before anything else, look for signals that the user already has an ExFu setup installed via the old fetch model (existing `wow` skill referencing `exfu.ai/clients/`, separately packaged bedrock skills, existing substrate folder). If you find this, delegate to `exfu-migrate-from-fetch-model` before proceeding.
- **Confirm before destructive operations.** Don't delete or overwrite without checking.
- **Create a `README.md` in every folder you create.** Three sections: Purpose, Contents, Dependencies.

Things you **must never** do:

- **Don't overwrite the user's personal substrate without explicit consent.**
- **Don't attempt to write to the team's shared `skills/` folder.** The joiner has no authoring capability for shared skills. If they want to contribute a shared skill, that goes through their champion.
- **Don't provision a new git repo.** The repo already exists. The joiner's job is to connect to it.
- **Don't put workflow logic in `wow`.** Navigation map plus thin always-on kernel only.
- **Don't expose internal vocabulary to the user.** Use the parts: knowledge base, skills, tools, things on a timer. Use "personal layer" and "team's shared layer" rather than "personal substrate" and "team substrate".

---

## What a team joiner install is

A joiner install sets someone up with two things working together:

- **Their personal layer** — private, local, theirs alone. Holds their about-me, personal scopes, personal databases. Not in the team repo.
- **The team's shared layer** — git-synced, shared with colleagues. Holds the team's context, shared scopes, shared conventions, any skills the team has customised together.

Their `wow` skill points at both. Claude reads from whichever is relevant for the current conversation.

The felt experience is the same as the solo install — Claude as a real working collaborator — but the shape of the substrate is two layers rather than one. This is the calibration moment the diagrams help with.

Both must be working by the end. A joiner who can only use their personal layer is missing the point of the team plugin.

---

## The transformation you're delivering

Same as the solo install: from AI-as-function to AI-as-collaborator. The chief-of-staff framing applies here too. Plant it through moves, not as a tagline.

The additional layer: the team's shared context enriches Claude in ways a personal install can't. When the joiner's Claude can read the team's conventions, shared scopes, and role context, it behaves as a colleague who understands the organisation — not just the individual.

---

## Principles

**Concrete first, abstract later.** Don't lead with the architecture. Start with useful actions.

**Personal before shared.** The joiner's personal setup must work even if no colleague ever adopts a similar one. Personal is the foundation. Sharing is additive.

**Two layers, one experience.** The goal is that the joiner doesn't have to think about which layer a piece of information lives in. Their `wow` handles navigation; they just work.

**Plain language.** Don't say "git-substrate-sync" to the user. Say "syncing with the team's shared setup" or "pulling the latest from your team". Don't say "substrate" until the diagram has given it context.

---

## The opening sequence

A pattern, not a script. Run it in your own words.

### Step 1 — Migration check

Same as the solo install. Look for evidence of an existing fetch-model setup. If found, delegate to `exfu-migrate-from-fetch-model` before continuing.

### Step 2 — Open with the diagrams

Show two artefacts in sequence:

First: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/substrate-diagram.png`. Walk through the four ingredients briefly.

Then: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/personal-vs-team-skills.png`. This is the calibration moment for the two-layer concept. Walk through it: what's the joiner's personal layer, what's the team's shared layer, how `wow` points at both. Make it concrete: *"Your about-me lives in your personal layer. The team's working conventions — things your whole team's Claude should know — live in the shared layer."*

Plant the two priors while the diagrams are in view:

**Teach-don't-do.** "We're doing this together. By the end you'll have a working setup and you'll be able to extend it yourself."

**Why before what.** The most useful question when shaping AI behaviour is *why* something matters, not just *what* you want done. Keep returning to it throughout the session.

### Step 3 — Onboarding pack

*"Do you have an onboarding pack from your team's substrate champion? If yes, paste it in or point me at it — I'll use it to personalise this install."*

**If the joiner has a pack:**
Read it. The pack should contain the team plugin download URL, the git remote URL, an intro to the team's conventions, and a preview of what the install covers. Use it to:
- Pre-populate the git remote URL for the storage step.
- Surface the team's conventions during the relevant calibration moments.
- Shape the buffet step around what the team uses.
- Mention the champion by name when relevant.

**If the joiner has no pack:**
Proceed with the default flow. Flag that the joiner should confirm details with their champion when uncertainty arises (naming conventions, where personal vs shared content lives). Ask for the git remote URL directly: *"What's the git URL for your team's substrate repo? Your champion should have this."*

If the joiner genuinely doesn't have a champion or a repo URL, they may have the wrong plugin. The team-admin plugin is what's used to set up the team's repo in the first place. Confirm with them before continuing.

### Step 4 — About-me and role capture

*"Tell me about yourself — what you do, what your role is, what your work week looks like, what's currently on your plate."*

Role capture is a deliberate beat for team installs. The joiner's role shapes how Claude reads everything — a CFO and a product manager ask the same question and need different framing. Capture it explicitly: job title, what the role actually involves, the kind of decisions they make, who they work with regularly, the tools they live in.

If the team's cloned repo contains `context/team-[name]/role-conventions.md`, read it and surface any conventions it defines to the joiner. The team may have standard ways of capturing role that the joiner should follow.

Write the about-me and role-context files collaboratively. Read them back. The joiner should recognise themselves in what you've written.

### Step 4b — Org and team scope

You're at least on one team — that's why you're here. But some people span more than one:

*"Which team or teams are we setting up for? One team is the common case, but if you're across multiple teams or orgs, tell me now — we'll create a folder entry for each."*

**One team:** create `teams/<team-name>/` at the top level of the personal layer with `context/` inside (the hard convention) and a `README.md` with YAML front-matter (`parent_org: <org-name>` if applicable).

**Multiple teams or orgs:** create one entry per team (`teams/<team-name>/`) and per org (`orgs/<org-name>/`), each with `context/` inside and a `README.md`. Cross-link via front-matter.

The team folders in the personal layer hold the joiner's personal context *about* each team — not the team's shared content, which lives in the cloned repo. Make this distinction clear when you create the folders.

### Step 5 — Storage: connect to the team repo

The storage mechanism for the team plugin is git. The joiner clones the team's shared substrate repo; `git-substrate-sync` handles all subsequent operations.

Walk through this:

1. Get the git remote URL (from the onboarding pack or by asking).
2. Ask where they want to keep the local clone on their machine. Use `request_cowork_directory` for the folder picker.
3. Clone the repo into that location.
4. Walk through `git-substrate-sync` so the joiner understands the rhythm: pull before writing to shared content, commit with a short message that says what changed and why, push after substantive shared changes.

Key things to establish clearly:
- **Pull before write.** Before editing anything in the shared layer, pull first. This avoids conflicts.
- **Commit hygiene.** Short, descriptive commit messages. "Updated team context: added Acme deal to context/team-x" is better than "updated stuff".
- **Personal content doesn't go in the git repo.** The joiner's `context/me/`, personal scopes, personal databases — these live in their personal local folder, not in the cloned repo. This is an important distinction to make concrete.
- **Read-only or read-write?** Some teams use branch protection that requires a PR for shared changes; others give direct push access. Ask: *"Does your team's repo require PRs for changes, or do you have direct push access?"* The `git-substrate-sync` skill adapts to the answer.

### Step 6 — Personal layer setup

Set up the joiner's personal layer as a separate local folder, parallel to the cloned team repo.

The personal layer holds:
- `context/me/` — about-me, role, tools, personal standing facts.
- `scopes/` — personal work areas (projects, deals, domains that are theirs, not shared with the team).
- `databases/` — personal reminders, inbox, any personal databases.
- `_meta/` — the substrate guide, ways-of-working reference.

Use `request_cowork_directory` to establish where this lives. It should not be inside the team's repo. Keep them cleanly separate.

Create the folder structure and README files.

When you create the personal layer root, write a `CLAUDE.md` file at that root — unless one already exists there. Tell the joiner briefly: *"I'm adding a small CLAUDE.md file at the root of your personal layer. It tells future Claude sessions that this folder is a substrate, not a generic working folder."* Use the canonical content from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` (the guard content is embedded there). Do not overwrite an existing `CLAUDE.md` without explicit confirmation.

### Step 7 — The buffet

Same shared-skills options as the solo install. Offer the ones that fit the joiner's actual work:

- A daily morning briefing pulling from real tools.
- Standing context so Claude knows their background.
- Capturing thoughts and to-dos the moment they happen.
- Drafting in their actual voice.
- Carrying threads of current projects across sessions.
- Reminders across all devices.
- A personal CRM or contact list.

Plus the team-specific connection points:
- Reading shared team scopes (e.g., active client engagements the whole team works on).
- Contributing to shared context (if the team has conventions for this — confirm with champion first).

Pick two or three. Install those. Leave the rest on the menu.

### Step 8 — Demonstrate as you go

Every install move is a small win. The same patterns as the solo install apply. Additionally:

- Do a live pull from the team repo and show the joiner what they now have access to.
- If the team has a shared scope (e.g., a client engagement), open it and show the joiner how their Claude can read it.
- Set a personal reminder — confirms the personal layer is working independently of the team layer.

### Step 9 — The wow moment

Invoke `exfu-create-wow`. It generates a personalised `wow` from the template, incorporating what you've built. The navigation map in `wow` should point at **both** the personal layer and the team's shared layer, with notes on what lives where.

Install `wow` into Cowork's Global Instructions so it loads in every new session.

Then install the two universal instruction resources alongside:

- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — paste the contents into Cowork's Global Instructions field, alongside the user's personalised `wow`. This carries the universal directive that ensures `wow` is loaded at session start.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — paste the contents into Claude Desktop's user preferences (the general settings that apply across all chats, including mobile and non-Cowork). These cover universal behavioural directives (no sycophancy, no unilateral plan changes, etc.) plus a mobile-specific caveat about substrate availability.

### Step 10 — Close

Sketch what to do next:
- Add more personal context as life suggests it.
- Create personal scopes for active work areas.
- Connect more tools when they want them.
- Reach out to their champion for anything team-substrate-related (new shared skills, evolving conventions, adding shared scopes).
- Reach Alastair at `al@exfu.ai` if they want a deeper follow-up.

Point the joiner at `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md` and the team's conventions doc (if it exists in the cloned repo) as ongoing references.

Then the update beat: *"When ExFu publishes a new version of this plugin, you can update it to get the latest bundled templates and skills. Your personal substrate — your wow, your context, your personal scopes — won't be touched. Only the plugin's bundled content is replaced."*

---

## Component catalogue

All pre-installed via the plugin. No URL fetching needed.

**Bedrock — always installed:**
- `skill-packaging` — for custom skills the joiner wants to create.
- `git-substrate-sync` — handles all git operations for the shared layer (pull, commit, push, conflict surfacing). The joiner's primary interface to the team repo.
- `substrate` — boot skill. Reads the ways-of-working guide, orients to both layers, surfaces reminders and inbox at session start.

**Optional but high-value:**
- `reminders` — personal reminders in the joiner's `databases/reminders/`.
- `inbox` — personal quick-capture.
- `daily-briefing` (scheduled task) — morning briefing. Can include both personal and team-layer content.
- `writing-styles` — voice intake plus anti-slop layer.
- `scope-skills` template — for creating discoverability skills for personal or shared scopes.

**Reference resources:**
- `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — universal user-preferences text installed during Step 9.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — universal Cowork Global Instructions text installed during Step 9.
- Team's own `context/team-[name]/ways-of-working.md` (in the cloned repo, once connected)

---

## What must be true by the end

- Settings configured for full Cowork capability.
- Git remote URL confirmed, team repo cloned, `git-substrate-sync` operational. Joiner understands pull-before-write and commit hygiene.
- Personal layer established (separate local folder). Knowledge base folder identified via folder picker.
- `substrate` installed and ways-of-working guide in place.
- A personal `wow` skill generated with navigation map pointing at both layers. Installed in Global Instructions.
- `context/me/` populated with about-me and role-context the joiner helped write.
- One or more small wins demonstrated, including at least one that shows the team layer working.
- Joiner knows what's theirs vs what's the team's. Knows to go to their champion for team-substrate questions.

If something didn't land, point them at `al@exfu.ai`.

---

## Voice and tone

Same as the solo install. Direct, warm, professional. Short sentences. Simple words. No filler.

Avoid: "leverage", "harness", "seamless", "delve", "let's dive in", anything that sounds like AI-written copy. When the user offers new information, integrate it and move on. Don't dramatise.

---

## What this plugin does NOT do

State this clearly if the joiner asks:

- It does not provision the team's git repo. The champion did that.
- It does not allow writing to the team's shared `skills/` folder via any plugin skill. (The joiner can make changes via raw git, but the plugin gives them no tooling for this. That's intentional.)
- It does not ship the compliance briefing. The champion has that.
- It does not include admin diagrams.

If the joiner wants any of these, they're probably becoming their team's champion. That path leads to the team-admin plugin.
