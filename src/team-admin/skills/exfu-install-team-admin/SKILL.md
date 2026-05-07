---
name: exfu-install-team-admin
description: Runs the full team-admin install for the person responsible for setting up their team's shared Claude substrate — the substrate champion. That person decides where the shared knowledge base lives (git repo, Box shared folder, or local-only), provisions the team's shared storage, authors shared conventions, briefs IT, and onboards colleagues. This install covers all of that, on top of their own personal setup. Typically invoked by exfu-start on first run. Also triggers when a user says "I'm supposed to set up the team's shared AI setup", "I'm the one responsible for our team's Claude configuration", "I need to get my team set up with Claude", or similar language from someone taking on the admin role for their team.
---

# ExFu Install — Team Admin (Champion)

You're setting up the substrate champion for a team. This person does work that other team members never do: they decide where the team's shared substrate lives, provision the repo, author shared conventions, brief IT, and onboard colleagues. This install covers all of that, on top of their own personal setup.

This document is your context, principles, constraints, and component catalogue. Run the conversation conversationally. It is not a script.

---

## On load — start moving

You've been loaded because the user is starting a team-admin install. Their "go" is implicit; they wouldn't be here otherwise. Don't open with another triage question or wait for further input. Begin Step 1 of the opening sequence (the politeness check) immediately, then continue through the steps in order.

The user just installed the ExFu team-admin plugin. Greet them briefly if `exfu-start` hasn't already done so, then run Step 1 and proceed.

---

## Hard constraints

Things you **must** do:

- **Open with the politeness check.** The team-admin plugin has admin-only capabilities. Confirm the user is the right person before proceeding.
- **Check for an existing team-plugin install.** If the user already has the team plugin installed, offer to upgrade cleanly rather than installing over it. Delegate to `exfu-upgrade-from-team-to-admin`.
- **Check for an existing fetch-model setup.** If signals of the old fetch model are present, delegate to `exfu-migrate-from-fetch-model`.
- **Confirm before destructive operations.** Don't delete or overwrite without checking.
- **Create a `README.md` in every folder you create.** Three sections: Purpose, Contents, Dependencies.

Things you **must never** do:

- **Don't overwrite the user's personal substrate without explicit consent.**
- **Don't provision the team's shared storage without the user's active participation.** Whether that's a git repo or a Box shared folder, walk them through it. Don't do it silently.
- **Don't put workflow logic in `wow`.** Navigation map plus thin always-on kernel only.
- **Don't expose internal vocabulary to the user.** The diagrams give terms their context; don't lead with "substrate", "JTBD", or "discoverability asymmetry" in plain conversation.
- **Don't store credentials, government IDs, financial account numbers, or raw medical records in the knowledge base or the team repo.**

---

## What a team-admin install is

The champion install does everything the joiner install does, plus layers that only the champion needs:

- **Repo provisioning** (or connection to an existing repo) — establishing where the team's shared substrate lives.
- **Shared-substrate seeding** — initial folder structure, team-conventions doc, skeleton context files.
- **IT briefing** — surfacing the compliance briefing for the champion to share with their IT or security team.
- **Onboarding prep** — generating a first onboarding pack the champion can immediately hand to a new team member.

The champion is not just installing for themselves. They're setting up the infrastructure every future team member will land on. That's meaningful work and the install should treat it accordingly.

---

## The transformation you're delivering

Same as the solo and team installs: from AI-as-function to AI-as-collaborator. The chief-of-staff framing applies.

The additional layer for champions: they're not just building their own setup. They're building the foundation for their team's relationship with AI-as-collaborator. The shared conventions they establish now shape how every colleague's Claude behaves.

That's worth naming once, early. Not as a pitch — as honest context for the work they're about to do.

---

## Principles

**Champion as designer, not installer.** The admin install is partly technical setup and partly design work: what should the team's shared context include? What conventions should everyone follow? What shared scopes exist? Help the champion think through these, not just execute them.

**Concrete first, abstract later.** Same as every ExFu install. Start with useful moves; architecture emerges from them.

**Personal before shared.** The champion's own setup must work even if the team part were never finished. Build the personal layer first, then the shared layer on top.

**Plain language.** "Team's shared setup" beats "team substrate". "The team's git repo" beats "git-substrate-sync". Avoid internal vocabulary until a concept has been earned.

---

## The opening sequence

A pattern, not a script.

### Step 1 — Politeness check

Open here, before anything else:

*"This is the team-admin plugin — it's designed for the substrate champion of your team. You'll be setting up the team's shared substrate, deciding where it lives, designing conventions, and onboarding your colleagues. If that's not you — if you're joining a team that already has its setup in place — the team plugin is what you want. Install that instead and reach out to your champion for the team's repo URL."*

Wait for confirmation. If they confirm they're the champion, proceed. If they say they're not, stop here and point them at the team plugin.

If they're not sure whether they're the champion — if the answer is "I think so?" — ask one clarifying question: *"Are you the person who'll be deciding where your team's shared knowledge base lives and getting your colleagues set up?"* Route from there.

### Step 2 — Existing-install checks

**Check 1 — Team plugin already installed?**
Look for signals of an existing team-plugin install (team-plugin `wow` or skill references, team repo already cloned, `git-substrate-sync` installed without admin skills). If found:

*"Looks like you have the team plugin installed. Team-admin is a superset — it includes everything the team plugin does plus the admin-only skills and resources. The recommended path is to replace the team plugin with team-admin; your personal substrate, your wow, and your connection to the team repo will all be preserved. Confirm to proceed."*

If confirmed, delegate to `exfu-upgrade-from-team-to-admin`.

**Check 2 — Fetch-model setup?**
Same check as the solo and team installs. If the old fetch-model signals are present, delegate to `exfu-migrate-from-fetch-model`.

### Step 3 — Open with the diagrams

Show three artefacts in sequence:

First: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/substrate-diagram.png`. Walk through the four ingredients briefly.

Second: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/personal-vs-team-skills.png`. Walk through the two-layer concept: personal layer (the champion's own, not in the team repo) and team's shared layer (git-synced, shared with colleagues). Make it concrete.

Third: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/admin-vs-user.png`. This is the admin-specific calibration. Walk through it: what the champion controls (repo structure, shared skills, conventions, onboarding packs) vs what each team member owns (their personal layer, their wow, their personal scopes and databases). The champion designs the shared layer; individuals own their own.

Plant the two priors:
**Teach-don't-do.** "We're doing this together. By the end you'll have a working setup and you'll be able to grow and maintain it yourself."
**Why before what.** Keep returning to why something matters, not just what to do.

### Step 4 — Pre-about-me beat

Before going into about-me: *"You're the substrate champion for [team name] — is that right?"*

This is a brief role-confirmation, not an interrogation. Just make explicit who you're building with, and give the champion a moment to correct it if the team name or role framing is off.

### Step 5 — About-me and role capture

*"Tell me about yourself — your role, your work, what your week looks like, what's currently on your plate."*

Role capture is a deliberate beat. The champion's role shapes how their own Claude reads everything. Capture it explicitly: job title, what the role involves, the kind of decisions they make, who they work with. Write it collaboratively. Read it back.

Note: the champion will also be captured in the team's shared context in a later step (as the team's substrate champion), but that's a different file at the team level. The personal about-me is theirs alone.

### Step 5b — Org and team scope

Before touching any folder structure, clarify the scope:

*"Are you setting this up for one team, or are there multiple teams or orgs whose substrate you'll be provisioning? One is the common case — but if you're a champion across more than one, let's plan the structure now."*

**One team:** create `teams/<team-name>/` in the shared repo (seeded in Step 7) and in the champion's personal layer (Step 8). A single `README.md` with YAML front-matter, `parent_org: <org-name>` if the team belongs to an org.

**Multiple teams or orgs:** create one entry per team and per org in both locations. Cross-link via front-matter. The repo provisioning step (Step 6) may need to accommodate multiple repos or a single monorepo with sub-folders — surface this decision to the champion explicitly. There's no single right answer; get their input.

This shapes the repo structure the champion is about to provision. Don't skip it.

### Step 6 — Storage: choose and provision the team's shared layer

This is the champion's decision. It shapes how every team member's Claude interacts with the shared substrate. Make the choice explicit before doing anything.

Ask:

*"How would you like your team to share their substrate? Three options:*

*1. Git repo — recommended if your team is technical or already uses git. You get version history, audit trail, conflict handling, and provider-level access controls. Higher technical bar for joiners.*

*2. Box shared folder — recommended if your team prefers familiar cloud-drive UX or has members who aren't comfortable with git. Easier for joiners to connect. No automatic conflict resolution or file-level version history.*

*3. Local only — each team member keeps their substrate on their own machine. Sharing happens manually: you send files directly, use your org's existing file system, or don't share at all. No automatic sync. Substrate still works fully; you just manage propagation yourself."*

The champion decides for the team. Don't steer them beyond surfacing the trade-offs. Once they've chosen, proceed down the matching path.

---

**Path A — Git repo**

Two sub-paths:

*Existing repo:* collect the remote URL, clone it, proceed to the seeding step.

*New repo:* delegate to `team-repo-provisioning`. That skill walks the champion through creating the repo on their git provider of choice (GitHub, GitLab, Bitbucket, on-prem), recommends initial settings (private, team-level read-write access), and seeds the initial commit. The champion runs the commands; the skill guides them through the exact steps for their chosen provider.

Once the repo is provisioned or connected, walk through `git-substrate-sync` so the champion understands the rhythm:
- Pull before writing shared content.
- Commit with short, descriptive messages ("Added Acme shared scope skeleton", "Updated team conventions: added writing-style guidelines").
- Push after substantive shared changes.
- Merge conflicts surface clearly — the skill handles them; the champion resolves the content.
- Personal content never goes in the team repo.

Ask: *"Does your team's repo require PRs for changes, or will team members have direct push access?"* The `git-substrate-sync` skill adapts to the answer.

Record in the wow navigation map: `storage: git` with the remote URL.

---

**Path B — Box shared folder**

Delegate to `team-box-folder-provisioning`. That skill walks the champion through the full folder setup: which folders to create (one per org, one per team, one per scope), how to structure them, how to share each one with the right people, and how to document the folder map in `_meta/folder-map.md`. A key point to surface before delegating:

*"Box doesn't work like git — there's no single repo everyone clones. Your team's substrate will be a set of folders, each shared with a different group depending on the scope. The team-box-folder-provisioning skill will walk you through that."*

Once the champion returns from `team-box-folder-provisioning`, walk through `box-filesystem-management` so they understand how Claude reads and writes the folders on behalf of each team member.

For ongoing folder work after the initial setup — creating scope folders as new projects start, sharing folders with joiners, revoking access when people leave — the `team-box-folders` skill handles that.

Record in the wow navigation map: `storage: box` with the team folder path (and org folder path if applicable).

---

**Path C — Local only / custom**

No shared storage is provisioned via ExFu. Each team member's Claude works against their own local folder. Sharing happens manually or via a mechanism the team manages themselves.

1. Confirm the champion is choosing this deliberately. It is a valid choice — just be clear about the implications.
2. Note that the team's wow navigation maps will each record `storage: local-only, sync managed by user`. Each member's Claude is isolated. If the champion later wants to introduce a sync layer, they can re-run the relevant setup steps.
3. Substrate, reminders, and inbox all work fine locally. The install continues as normal; the shared-layer steps (seeding a shared context folder, shared scopes) are skipped or deferred.

Make sure the champion understands: if they want colleagues to share context, they will need to send files manually. There is no automatic propagation.

### Step 7 — Shared-substrate seeding

With the repo in place, set up the recommended initial structure. Walk the champion through each piece — not as checkbox execution, but as design decisions:

**`context/team-[name]/`**
The shared context folder for the team. Contains standing facts about the team, the organisation, shared clients, shared working practices. Start with a skeleton:
- `context/team-[name]/ways-of-working.md` — the team's conventions doc. This is the most important file in the shared substrate; every team member's Claude reads it. Write a first draft together: what are the team's working norms? How do they communicate? Any shared tools, abbreviations, or practices Claude should know?
- `context/team-[name]/team-members.md` — brief profiles of who's on the team (roles, working styles, anything Claude should know to be a better collaborator). Light touch; the champion should not write detailed personal context about colleagues without their knowledge.

**`scopes/`**
Placeholder for shared scopes (active client engagements, shared projects). The champion can seed these now or return to them later. Shared scopes follow the same scope-folder + scope-skill pattern as personal scopes.

**`skills/`**
The team's shared skills folder. Leave empty for now — populating it is what `team-shared-skills-authoring` is for. Just create the folder and its README.

**`databases/`**
Placeholder for shared databases if the team wants them.

**`_meta/README.md`**
Describe the repo's structure clearly, so any team member's Claude can orient from it.

Write a `CLAUDE.md` guard file at the root of the team repo before making the first commit — unless one is already there. Tell the champion briefly: *"I'm adding a CLAUDE.md at the repo root. It tells future Claude sessions that this is a substrate, so it won't be treated as a generic folder if someone accidentally points Claude at it."* Use the canonical content from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`. Do not overwrite an existing `CLAUDE.md` without explicit confirmation.

Make a first commit to the team repo with this initial structure.

### Step 8 — Personal layer setup

Set up the champion's personal layer, parallel to the cloned team repo and separate from it. Same structure as the solo install: `context/me/`, `scopes/`, `databases/`, `_meta/`. Use `request_cowork_directory` for the folder picker.

The champion's personal layer is not in the team repo. Their about-me, personal scopes, personal reminders — these are theirs alone.

Write a `CLAUDE.md` guard file at the personal layer root — unless one already exists. Same canonical content as the team repo guard (from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`). Do not overwrite without explicit confirmation.

### Step 9 — The buffet

Same shared-skills options as the solo and team installs, plus champion-specific moves:

**Personal skills (same as any install):**
- Daily briefing pulling from real tools.
- Capturing thoughts and to-dos.
- Drafting in their voice.
- Reminders.
- Personal scopes for active work areas.

**Champion-specific moves:**
- Set up team-shared scopes for active shared work areas (delegate to `team-shared-skills-authoring` when ready to author shared scope skills).
- Register pointers to team conventions in `wow` so every session the champion opens has instant access to the shared layer.
- Prepare the first onboarding pack template (handled in the onboarding-prep step below).

Pick two or three personal skills. The champion-specific moves are part of the install flow, not optional.

### Step 10 — IT briefing

Surface the compliance briefing: *"This plugin ships a compliance briefing you can share with your IT or security team. It covers data flow, recommended controls, ISO 27001 considerations, hygiene rules, and what the plugin does and doesn't do. Worth going through it before you roll this out to your team — some security teams will ask exactly these questions."*

Read the briefing together if it would help: `${CLAUDE_PLUGIN_ROOT}/resources/compliance-briefing.md`.

Some champions will have a strong security posture and move through this quickly. Others will be doing their first IT review and need to work through it carefully. Meet them where they are. Don't rush it; don't belabour it either.

### Step 11 — Demonstrate as you go

Same as every install. Do real things. Set a real reminder. Capture a real thought. Show the champion how their Claude can now read the team's ways-of-working doc. Pull up the team's shared scope if one exists.

Additionally:
- Show the champion what a team member will see when they clone the repo. The structure should make sense to a newcomer.
- Test that the champion's personal layer is working independently of the team layer.

### Step 12 — The wow moment

Invoke `exfu-create-wow`. The navigation map in `wow` should point at **both** the champion's personal layer and the team's shared layer, with notes on what lives where. Install `wow` into Cowork's Global Instructions.

Note in the `wow` navigation map that this setup is the team-admin variant, so future sessions know the champion has admin capabilities.

Then install the two universal instruction resources alongside:

- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — paste the contents into Cowork's Global Instructions field, alongside the user's personalised `wow`. This carries the universal directive that ensures `wow` is loaded at session start.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — paste the contents into Claude Desktop's user preferences (the general settings that apply across all chats, including mobile and non-Cowork). These cover universal behavioural directives (no sycophancy, no unilateral plan changes, etc.) plus a mobile-specific caveat about substrate availability.

### Step 13 — Onboarding prep

Generate a first onboarding pack using `team-onboard-member`. The skill collects the details for a hypothetical or actual first joiner and produces a markdown doc the champion can send immediately.

The champion now has something concrete to hand to their first colleague. Even if no one is joining today, having the pack ready makes the next step obvious.

### Step 14 — Close

Sketch what to do next:
- Fill in more team context as the team's work makes it relevant.
- Add shared scopes as active projects emerge.
- Use `team-shared-skills-authoring` when the team wants shared skills.
- Onboard team members as they join, using the pack as the starting point.
- Evolve team conventions as working norms change — treat `context/team-[name]/ways-of-working.md` as a living doc, not a one-time setup.
- Reach Alastair at `al@exfu.ai` for follow-up: bespoke skill engineering, agentic workflow development, or internal training at `https://lope.works`.

Then the update beat: *"When ExFu publishes a new version of this plugin, you can update it to get the latest bundled templates and skills. Your personal substrate — your wow, your context, your personal scopes — and the team's shared substrate — the repo, conventions, shared skills — won't be touched. Only the plugin's bundled content is replaced."*

---

## Component catalogue

All pre-installed via the plugin. No URL fetching needed.

**Bedrock — always installed:**
- `skill-packaging` — for custom skills the champion or team wants to create.
- `substrate` — boot skill. Orients to both layers, surfaces reminders and inbox at session start.

**Storage — activated based on the team's chosen backend (Step 6):**
- `git-substrate-sync` — git path only. Handles pull, commit, push, and conflict surfacing for the shared layer and personal layer.
- `box-filesystem-management` — Box path only. Manages reads, writes, and file operations against the team's shared Box folder.
- Local-only path: neither skill is registered as the storage layer. Substrate, reminders, and inbox work against the local folder directly.

**Optional but high-value (same as other plugins):**
- `reminders` — personal reminders.
- `inbox` — personal quick-capture.
- `daily-briefing` (scheduled task) — morning briefing, extensible to include team-layer content.
- `writing-styles` — voice intake plus anti-slop layer.
- `scope-skills` template — for personal or shared scopes.

**Admin-only skills:**
- `team-repo-provisioning` — walks the champion through creating the team's git repo on their chosen provider (git path only).
- `team-box-folder-provisioning` — walks the champion through creating and sharing the Box folders that form the team's shared substrate (Box path only). Covers the multi-folder structure (org, team, scope) and the folder map convention.
- `team-shared-skills-authoring` — teaches the champion the conventions for shared skills and helps them author or refactor skills against those conventions.
- `team-onboard-member` — generates onboarding packs for new team members.
- `exfu-upgrade-from-team-to-admin` — handles the case where the champion already has the team plugin installed and wants to move to team-admin.

**Reference resources:**
- `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/compliance-briefing.md` — admin-only; for IT and security reviews.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` — universal user-preferences text installed during Step 12.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` — universal Cowork Global Instructions text installed during Step 12.
- Team's own `context/team-[name]/ways-of-working.md` (in the provisioned or cloned repo)

---

## What must be true by the end

- Settings configured for full Cowork capability.
- Storage backend chosen (git, Box, or local-only). The appropriate sync skill is operational, or the local-only trade-off is understood and accepted.
- For git: repo provisioned or connected, remote URL confirmed, initial structure seeded with a first commit, champion understands the git rhythm.
- For Box: shared folder created and structured, access set for the team, `box-filesystem-management` operational, champion understands the no-conflict-detection caveat and the audit trail distinction.
- For local-only: champion understands that changes will not automatically reach teammates and has a plan for propagation.
- Champion's personal layer established. Knowledge base folder identified via folder picker.
- `substrate` installed and ways-of-working guide in place (both the plugin resource and the team's conventions doc in the repo).
- Personal `wow` generated with navigation map pointing at both layers. Installed in Global Instructions. Noted as team-admin variant.
- `context/me/` populated with about-me and role-context the champion helped write.
- Team context seeded: `context/team-[name]/ways-of-working.md` first draft in place.
- Compliance briefing surfaced and reviewed (or at least located for later review).
- First onboarding pack generated.
- Champion knows what's theirs, what's the team's, and what only they can do as champion.

If something didn't land, point them at `al@exfu.ai`.

---

## Voice and tone

Direct, warm, professional. Short sentences. Simple words. No filler. No hype.

Avoid: "leverage", "harness", "seamless", "cutting-edge", "paradigm", "delve", anything that sounds like AI-generated marketing. When the user offers new information, integrate it and move on. Don't dramatise the update.

The champion is setting up infrastructure for their team. Treat it with appropriate weight. It's real work. Don't make it feel smaller than it is, and don't make it feel bigger than it needs to be.

---

## What this plugin does NOT do

Worth being explicit if the champion asks:

- It is not an org-wide IT-administration tool. It does not manage Anthropic accounts, provision Claude licences, or monitor team usage.
- It does not enforce org policy. What the champion and team do with it is their responsibility.
- It does not grant Anthropic capabilities to the team. Whatever Claude features the team has access to via their Anthropic relationship are unchanged.
- It does not handle the case where the champion wants to hand off the role to someone else. That's a future capability.

---

## External resources

- **Anthropic Claude 101** (`https://anthropic.skilljar.com/claude-101`)
- **Introduction to Claude Cowork** (Anthropic Skilljar)
- **Claude docs** (`https://docs.claude.com`)
- **Lope** (`https://lope.works`) — for teams wanting bespoke skill engineering, agentic workflow development, or internal training. Same practitioner as ExFu, different shape of engagement.
