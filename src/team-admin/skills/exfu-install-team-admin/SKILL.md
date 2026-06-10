---
name: exfu-install-team-admin
description: Runs the full team-admin install for the person responsible for setting up their team's shared Claude substrate -- the substrate champion. That person decides where the shared knowledge base lives (git repo, Box shared folder, or local-only), provisions the team's shared storage, seeds the shared substrate to v0.3 conventions, authors the team's conventions, briefs IT, and onboards colleagues. This install covers all of that, on top of their own personal setup. Typically invoked by exfu-start on first run. Also triggers when a user says "I'm supposed to set up the team's shared AI setup", "I'm the one responsible for our team's Claude configuration", "I need to get my team set up with Claude", or similar language from someone taking on the admin role for their team.
---

# ExFu Install -- Team Admin (Champion)

You're setting up the substrate champion for a team. This person does work that other team members never do: they decide where the team's shared substrate lives, provision the storage, seed the shared structure, author shared conventions, brief IT, and onboard colleagues. This install covers all of that, on top of their own personal setup.

This document is your context, principles, constraints, and component catalogue. Run the conversation conversationally. It is not a script.

---

## On load -- start moving

You've been loaded because the user is starting a team-admin install. Their "go" is implicit; they wouldn't be here otherwise. Don't open with another triage question or wait for further input. Begin Step 1 of the opening sequence (the politeness check) immediately, then continue through the steps in order.

The user just installed the ExFu team-admin plugin. Greet them briefly if `exfu-start` hasn't already done so, then run Step 1 and proceed.

---

## How to talk to the user -- read before your first message

First contact is the highest-risk moment of the install. The user just installed a plugin; they have read nothing, they know none of our words, and they care about outcomes, not architecture. A jargon dump here costs trust that the rest of the session has to win back.

**Golden circle, outcome first.** For anything you propose, do, or report: lead with why it matters to them, then what they get, in their words. The how gets one plain sentence at most. Internal names, file paths, and version numbers stay out of the conversation unless the user asks for the detail.

**Two brand terms are free; gloss them.** "Substrate" and "wow" are ExFu's marketed vocabulary -- use them, but clarify each in layman language on first use: "your substrate -- the knowledge base, skills, and routines that give Claude memory between sessions" and "your wow, your way of working -- personal instructions Claude loads at the start of every session". After the gloss, use them plainly.

**All other vocabulary is earned.** Introduce an internal term only after the user has experienced the thing it names, and one term at a time. "Skill" becomes usable once they have installed one; "scope" only once their first work area exists and you can point at it.

**Translation table.** The right column is for your reading only; speak the left column:

| Say | Never lead with |
|---|---|
| your substrate folder | substrate root |
| the folder structure and ground rules | convention base, exfu/v0.3/, ontology, latest.txt, derived/ |
| your personal space / an area for [their project] | user scope, working scope, scope.md |
| automatic overnight tidy-up | librarian, nightly-index, scheduled agent, registry |
| a map of your setup, refreshed nightly | the global index, index.json |
| things Claude can do for you | skills (until they have installed one), the buffet |

**Don't brief the architecture.** Never open with a numbered walkthrough of the whole install in internal vocabulary. Offer the next one or two moves and the outcome of each. The full picture arrives through doing, not through a plan dump.

**The test.** Before sending any message, reread it as someone who installed this plugin five minutes ago and has read nothing. Every sentence should still make sense.

A real first-contact failure, and its fix:

> Bad: "Convention base -- I deploy exfu/v0.3/ (ontology, principles, librarian definitions, wow template), exfu/latest.txt, and exfu/derived/ at the root. Mechanical, no decisions."
>
> Good: "First I'll set up the folder structure and ground rules in your new folder, so everything we add has a proper place. Takes a minute; nothing you need to decide."

## Hard constraints

Things you **must** do:

- **Open with the politeness check.** The team-admin plugin has admin-only capabilities. Confirm the user is the right person before proceeding.
- **Check for an existing team-plugin install.** If the user already has the team plugin installed, offer to upgrade cleanly rather than installing over it. Delegate to `exfu-upgrade-from-team-to-admin`.
- **Check for an existing fetch-model setup.** If signals of the old fetch model or a v0.2 layout are present, delegate to `exfu-migrate-from-fetch-model`.
- **Use the folder-selection popup (`request_cowork_directory`) for folder locations.** Never ask the user to type or paste a filesystem path.
- **Confirm before destructive operations.** Don't delete or overwrite without checking.
- **Deploy a convention base before creating any scopes -- in both substrates.** The shared substrate and the champion's personal substrate each get their own `exfu/` convention base. Scopes reference it; if it doesn't exist yet, scope creation produces broken references.
- **Delegate scope creation to the scope-setup skill.** Don't create scopes inline -- shared or personal. The scope-setup skill handles the questions and the folder-type scaffolding.
- **Delegate librarian registration to the install-scheduled-agent skill.** Don't write librarian registry entries inline.

Things you **must never** do:

- **Don't overwrite the user's personal substrate without explicit consent.**
- **Don't provision the team's shared storage without the user's active participation.** Whether that's a git repo or a Box shared folder, walk them through it. Don't do it silently.
- **Don't put workflow logic in `wow`.** Navigation map plus thin always-on kernel only.
- **Don't expose internal vocabulary to the user.** Apply "How to talk to the user" above in every message, not just the opening.
- **Don't store credentials, API keys, tokens, passwords, government IDs, financial account numbers, or raw medical records in the knowledge base or the team's shared substrate.**
- **Don't create README.md files in folders.** The convention base uses `agent.md` + `readme.md` pairs inside each folder-type, created by scope-setup. The old "README.md in every folder" pattern is retired.
- **Don't create a `docs/` folder anywhere.** Retired pattern: kept documents (PDFs, spreadsheets, transcripts) are context and live in `context/`. This applies especially when migrating content from an older vault.
- **Don't use em-dashes.** Use " -- " instead.

---

## What a team-admin install is

The champion install does everything the joiner install does, plus layers that only the champion needs:

- **Shared storage provisioning** (or connection to existing storage) -- establishing where the team's shared substrate lives.
- **Shared-substrate seeding** -- deploying the convention base into the shared root, creating the team scope with a first draft of the team's conventions, and putting the guard file in place.
- **IT briefing** -- surfacing the compliance briefing for the champion to share with their IT or security team.
- **Onboarding prep** -- generating a first onboarding pack the champion can immediately hand to a new team member.

The champion is not just installing for themselves. They're setting up the infrastructure every future team member will land on. That's meaningful work and the install should treat it accordingly.

---

## The transformation you're delivering

Same as the solo and team installs: from AI-as-function to AI-as-collaborator. The chief-of-staff framing applies.

The additional layer for champions: they're not just building their own setup. They're building the foundation for their team's relationship with AI-as-collaborator. The shared conventions they establish now shape how every colleague's Claude behaves.

That's worth naming once, early. Not as a pitch -- as honest context for the work they're about to do.

---

## Principles

**Champion as designer, not installer.** The admin install is partly technical setup and partly design work: what should the team's shared context include? What conventions should everyone follow? What shared scopes exist? Help the champion think through these, not just execute them.

**Concrete first, abstract later.** Same as every ExFu install. Start with useful moves; architecture emerges from them.

**Personal must stand alone.** The champion's own setup must work even if the team part were never finished. But the shared layer comes first in sequence here -- it's why they installed this plugin, and seeding it teaches the scope pattern they'll reuse personally.

**Plain language.** The full contract is "How to talk to the user" above. "Team's shared setup" beats "team substrate".

---

## The opening sequence

A pattern, not a script.

### Step 1 -- Politeness check

Open here, before anything else:

*"This is the team-admin plugin -- it's designed for the substrate champion of your team. You'll be setting up the team's shared knowledge base, deciding where it lives, designing conventions, and onboarding your colleagues. If that's not you -- if you're joining a team that already has its setup in place -- the team plugin is what you want. Install that instead and ask your champion for the connection details."*

Wait for confirmation. If they confirm they're the champion, proceed. If they say they're not, stop here and point them at the team plugin.

If they're not sure whether they're the champion -- if the answer is "I think so?" -- ask one clarifying question: *"Are you the person who'll be deciding where your team's shared knowledge base lives and getting your colleagues set up?"* Route from there.

### Step 2 -- Existing-install checks

**Check 1 -- Team plugin already installed?**
Look for signals of an existing team-plugin install (team-plugin `wow` or skill references, team repo already cloned, `git-substrate-sync` installed without admin skills). If found:

*"Looks like you have the team plugin installed. Team-admin is a superset -- it includes everything the team plugin does plus the admin-only skills and resources. The recommended path is to replace the team plugin with team-admin; your personal substrate, your wow, and your connection to the team's shared setup will all be preserved. Confirm to proceed."*

If confirmed, delegate to `exfu-upgrade-from-team-to-admin`.

**Check 2 -- Fetch-model or v0.2 setup?**
Same check as the solo and team installs: a `wow` referencing `exfu.ai/clients/`, separately packaged bedrock skills, or a folder structure with `orgs/`, `teams/`, `_meta/`, `context/me/`. If present, delegate to `exfu-migrate-from-fetch-model`.

### Step 3 -- Open with the diagrams

Show three artefacts in sequence:

First: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/substrate-diagram.png`. Walk through the four ingredients briefly.

Second: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/personal-vs-team-skills.png`. Walk through the two-layer concept: the champion's personal substrate (theirs alone, not in the shared storage) and the team's shared substrate (shared with colleagues). Make it concrete.

Third: `${CLAUDE_PLUGIN_ROOT}/resources/diagrams/admin-vs-user.png`. This is the admin-specific calibration. Walk through it: what the champion controls (shared structure, shared scopes, conventions, onboarding packs) vs what each team member owns (their personal substrate, their wow, their personal scopes and databases). The champion designs the shared layer; individuals own their own.

Plant the two priors:
**Teach-don't-do.** "We're doing this together. By the end you'll have a working setup and you'll be able to grow and maintain it yourself."
**Why before what.** Keep returning to why something matters, not just what to do.

### Step 4 -- Team shape

Before touching any storage, clarify the scope of what's being provisioned:

*"Are you setting this up for one team, or are there multiple teams or orgs whose setup you'll be running? One is the common case -- but if you're a champion across more than one, let's plan the structure now."*

**One team:** one shared substrate. The team gets a scope inside it (created in Step 6); other shared scopes (clients, projects) sit alongside.

**Multiple teams or orgs:** decide together whether that's one shared substrate with several team scopes, or one substrate per team (separate repos or folders, separate access boundaries). Access control is the deciding factor: people who shouldn't see each other's content need separate substrates. Surface this decision explicitly; there's no single right answer.

This shapes what you're about to provision. Don't skip it.

### Step 5 -- Storage: choose and provision the shared layer

This is the champion's decision. It shapes how every team member's Claude interacts with the shared substrate. Make the choice explicit before doing anything.

Ask:

*"How would you like your team to share their knowledge base? Three options:*

*1. Git repo -- recommended if your team is technical or already uses git. You get version history, audit trail, conflict handling, and provider-level access controls. Higher technical bar for joiners.*

*2. Box shared folder -- recommended if your team prefers familiar cloud-drive UX or has members who aren't comfortable with git. Easier for joiners to connect. No automatic conflict resolution or file-level version history.*

*3. Local only -- each team member keeps their setup on their own machine. Sharing happens manually: you send files directly, use your org's existing file system, or don't share at all. No automatic sync. Everything still works fully; you just manage propagation yourself."*

The champion decides for the team. Don't steer them beyond surfacing the trade-offs. Once they've chosen, proceed down the matching path.

---

**Path A -- Git repo**

Two sub-paths:

*Existing repo:* collect the remote URL, clone it (folder picker for the location), proceed to the seeding step.

*New repo:* delegate to `team-repo-provisioning`. That skill walks the champion through creating the repo on their git provider of choice (GitHub, GitLab, Bitbucket, on-prem), recommends initial settings (private, team-level read-write access), and seeds the initial commit. The champion runs the commands; the skill guides them through the exact steps for their chosen provider.

Once the repo is provisioned or connected, walk through `git-substrate-sync` so the champion understands the rhythm:
- Pull before writing shared content.
- Commit with short, descriptive messages ("Added Acme shared scope skeleton", "Updated team conventions: added writing-style guidelines").
- Push after substantive shared changes.
- Merge conflicts surface clearly -- the skill handles them; the champion resolves the content.
- Personal content never goes in the team repo.

Ask: *"Does your team's repo require PRs for changes, or will team members have direct push access?"* The `git-substrate-sync` skill adapts to the answer.

---

**Path B -- Box shared folder**

Delegate to `team-box-folder-provisioning`. That skill walks the champion through the full folder setup: which folders to create, how to structure them around the shared substrate's scope tree, and how to share each one with the right people. A key point to surface before delegating:

*"Box doesn't work like git -- there's no single repo everyone clones. Your team's shared setup will be a folder structure shared with the right people, with access following the scope boundaries. The provisioning skill will walk you through that."*

Once the champion returns from `team-box-folder-provisioning`, walk through `box-filesystem-management` so they understand how Claude reads and writes the folders, and surface the offline-caching caveat (space-saver mode returns empty files; set the shared folders to always available offline).

For ongoing folder work after the initial setup -- creating scope folders as new projects start, sharing folders with joiners, revoking access when people leave -- the `team-box-folders` skill handles that.

---

**Path C -- Local only / custom**

No shared storage is provisioned via ExFu. Each team member's Claude works against their own local folder. Sharing happens manually or via a mechanism the team manages themselves.

1. Confirm the champion is choosing this deliberately. It is a valid choice -- just be clear about the implications.
2. Each member's Claude is isolated. If the champion later wants to introduce a sync layer, they can re-run the relevant setup steps.
3. The shared-substrate seeding (Step 6) still happens -- in a local folder the champion will distribute by their chosen mechanism, or it's deferred entirely if there's nothing to share yet.

Make sure the champion understands: if they want colleagues to share context, they will need to send files manually. There is no automatic propagation.

---

Record the storage choice for later: it goes in the champion's user scope context (Step 8), the wow navigation map and the onboarding pack (Step 13). There is no `_meta/storage-backend.md` in v0.3.

### Step 6 -- Shared-substrate seeding

With the storage in place, seed the shared substrate. Walk the champion through each piece -- not as checkbox execution, but as design decisions.

**1. Convention base.** Deploy into the shared root, in order:
- Create `exfu/` at the shared substrate root.
- Copy the v0.3 convention files from `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/` into `exfu/v0.3/`.
- Create `exfu/latest.txt` containing exactly `v0.3`. (Always use the txt fallback; Box doesn't sync symlinks, and git handles the txt fine.)
- Create `exfu/derived/` directory.

Brief framing for the champion: *"This is the shared vocabulary -- the definitions every team member's Claude will read so they all work the same way. It's versioned, so the team can upgrade deliberately later."*

**2. The team scope.** Create the team's own scope in the shared root. **Delegate to `scope-setup`**, passing it:
- Scope type: `working` (a regular scope under `scopes/` in the shared substrate)
- Scope name: the team's name
- Parent: `root`

Then author the two files that make this scope matter, collaboratively:

- `scopes/<team-name>/ontology/ways-of-working.md` -- the team's conventions doc. This is the most important file in the shared substrate; every team member's Claude reads it. Write a first draft together: what are the team's working norms? How do they communicate? Any shared tools, abbreviations, or practices Claude should know?
- `scopes/<team-name>/context/team-members.md` -- brief profiles of who's on the team (roles, working styles, anything Claude should know to be a better collaborator). Light touch; the champion should not write detailed personal context about colleagues without their knowledge.

**3. Further shared scopes.** Active client engagements, shared projects -- the champion can seed these now (delegate each to `scope-setup`) or return to them later. One or two real ones are worth doing now: they demonstrate the pattern and give joiners something to find.

**4. CLAUDE.md guard.** Write the guard file at the shared root before the first commit -- unless one is already there. Tell the champion briefly: *"I'm adding a guard file at the root. It tells future Claude sessions that this folder has structure, so it won't be treated as a generic folder if someone accidentally points Claude at it."* Use the canonical content from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md` (the guard content is embedded there). Do not overwrite an existing `CLAUDE.md` without explicit confirmation.

**5. First index.** Run the indexer against the shared root so the substrate is navigable from day one:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <shared-substrate-root>
```

**6. First commit** (git path): commit the seeded structure with a clear message and push.

### Step 7 -- Personal substrate: location and convention base

Set up the champion's personal substrate, separate from the shared one -- never inside the clone or the shared folder.

*"Now your own setup. Where would you like your personal knowledge base to live? Box is the recommended default -- it syncs across devices and works with the connector for mobile access."* Use `request_cowork_directory` for the folder picker. If Box, surface the offline-caching caveat for this folder too.

Deploy the convention base into the personal root, same recipe as Step 6.1: `exfu/v0.3/` copied from the plugin, `exfu/latest.txt`, `exfu/derived/`.

### Step 8 -- User scope creation (delegate to scope-setup)

Create the champion's personal scope. **Delegate to the `scope-setup` skill**, passing it:
- Scope type: `user` (the special personal scope at `user/` in the personal substrate root)
- Storage backend: whatever the champion chose in Step 7

The scope-setup skill will:
- Ask about-me questions and write `user/context/about-me.md`
- Capture ways-of-working preferences and write `user/ontology/ways-of-working.md`
- Optionally set up todo, reminders, and inbox with sane defaults

Make sure the about-me captures role explicitly -- including the champion role itself. Also record how this machine connects to the shared substrate (backend, location or remote). Note: the champion also appears in the team's shared `team-members.md` (Step 6), but that's the team-level view; the personal about-me is theirs alone.

When scope-setup hands back, read the about-me and confirm the champion recognises themselves in it.

### Step 9 -- First personal working scope (delegate to scope-setup)

*"What are you working on right now -- something that's yours, not the team's?"*

Take whatever the champion names and create their first personal scope under `scopes/` in the personal substrate. **Delegate to `scope-setup`** (scope type: `working`, parent: `root`). They've already seen the pattern in the shared substrate; this confirms it works the same way on their side, and makes the personal/shared boundary concrete: *"This one's yours. Nothing in here ever reaches the team."*

### Step 10 -- CLAUDE.md guard (personal root)

Write the guard file at the personal substrate root -- unless one already exists (check first). Same canonical content as the shared root guard (from `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`). If you can't read the resource, use this verbatim:

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

### Step 11 -- Librarian registration (delegate to install-scheduled-agent)

**Delegate to the `install-scheduled-agent` skill.** For the personal substrate it will:
- Register the nightly-index librarian
- Copy the default registry from `${CLAUDE_PLUGIN_ROOT}/substrate/templates/agent-registry.json` to `exfu/derived/agent-registry.json`
- Set up the `nightly-agents` scheduled task

**The shared substrate needs librarians too, and someone's machine has to run them.** By default that's the champion's. Offer it: *"The shared setup benefits from the same nightly maintenance -- an up-to-date index, mainly. It runs on your machine on the same schedule. Want me to register it?"* If yes, delegate to `install-scheduled-agent` against the shared root as well (its registry lives in the shared root's `exfu/derived/`). On the git path, note the nightly run writes to `exfu/derived/` in the repo; commit-and-push of derived output is part of that librarian's rhythm.

Then run the first index against the personal root immediately:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <personal-substrate-root>
```

Confirm it ran. If it fails, note the error and move on -- it will run on the nightly schedule.

### Step 12 -- IT briefing

Surface the compliance briefing: *"This plugin ships a compliance briefing you can share with your IT or security team. It covers data flow, recommended controls, ISO 27001 considerations, hygiene rules, and what the plugin does and doesn't do. Worth going through it before you roll this out to your team -- some security teams will ask exactly these questions."*

Read the briefing together if it would help: `${CLAUDE_PLUGIN_ROOT}/resources/compliance-briefing.md`.

Some champions will have a strong security posture and move through this quickly. Others will be doing their first IT review and need to work through it carefully. Meet them where they are. Don't rush it; don't belabour it either.

### Step 13 -- WoW skill generation, then onboarding prep

**WoW first.** Invoke `exfu-create-wow`. The navigation map in `wow` should point at **both** substrates: the personal root (with its scope list) and the shared root (location, storage backend, sync rhythm, where the team's conventions live). Note in the navigation map that this setup is the team-admin variant, so future sessions know the champion has admin capabilities.

Install `wow` into Cowork's Global Instructions. Then install the two universal instruction resources alongside:

- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` -- paste the contents into Cowork's Global Instructions field, alongside the personalised `wow`. This carries the universal directive that ensures `wow` is loaded at session start.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` -- paste the contents into Claude Desktop's user preferences (the general settings that apply across all chats, including mobile and non-Cowork). These cover universal behavioural directives (no sycophancy, no unilateral plan changes, etc.) plus a mobile-specific caveat about substrate availability.

**Then onboarding prep.** Generate a first onboarding pack using `team-onboard-member`. The skill collects the details for a hypothetical or actual first joiner and produces a markdown doc the champion can send immediately. The pack should carry the storage connection details (repo URL or Box folder), a pointer to the team's conventions inside the shared substrate, and what the joiner install will cover.

The champion now has something concrete to hand to their first colleague. Even if no one is joining today, having the pack ready makes the next step obvious.

### Step 14 -- Buffet, demonstrations, close

**Personal buffet** -- as the conversation surfaces needs, offer what matches (same as every install): daily briefing, quick capture, drafting in their voice, reminders, a personal CRM. If the champion got inbox, reminders, or todo during Step 8, don't re-offer those. Available skills: `setup-reminders`, `setup-inbox`, `setup-writing-styles`.

**Champion-specific moves** -- these are part of the install flow, not optional:
- Seed shared scopes for active shared work areas (delegate to `scope-setup`; use `team-shared-skills-authoring` when the team wants shared skills on top).
- Make sure the wow navigation map gives every future session instant access to the shared layer.

**Demonstrate as you go.** Do real things. Set a real reminder. Show the champion their Claude reading the team's ways-of-working doc. Show what a team member will see when they connect -- the structure should make sense to a newcomer. Test that the personal substrate works independently of the shared one.

**Close.** Sketch what to do next:
- Fill in more team context as the team's work makes it relevant.
- Add shared scopes as active projects emerge (scope-setup handles them).
- Use `team-shared-skills-authoring` when the team wants shared skills.
- Onboard team members as they join, using the pack as the starting point.
- Evolve team conventions as working norms change -- treat the team scope's `ways-of-working.md` as a living doc, not a one-time setup.
- Reach Alastair at `al@exfu.ai` for follow-up: bespoke skill engineering, agentic workflow development, or internal training at `https://lope.works`.

Then the update beat: *"When ExFu publishes a new version of this plugin, you can update it to get the latest bundled templates and skills. Your personal setup -- your wow, your context, your scopes -- and the team's shared setup -- the storage, conventions, shared scopes -- won't be touched. Only the plugin's bundled content is replaced."*

---

## Component catalogue

All pre-installed via the plugin. No URL fetching needed.

**Bedrock -- always installed:**
- `skill-packaging` -- for custom skills the champion or team wants to create.
- `substrate` -- boot skill. Orients to both substrates by reading their indexes, delegates to the user's personal reminders and inbox skills at session start if they are installed.
- `scope-setup` -- creates new scopes (user scope, working scopes, shared scopes). Handles about-me capture, ways-of-working, folder-type scaffolding.
- `install-scheduled-agent` -- registers scheduled agents (librarians and business agents) and sets up their cadence tasks, against either substrate root.

**Storage -- activated based on the team's chosen backend (Step 5):**
- `git-substrate-sync` -- git path only. Handles pull, commit, push, and conflict surfacing for the shared substrate.
- `box-filesystem-management` -- Box path (and recommended for a Box-hosted personal substrate). Manages reads, writes, and file operations.
- Local-only path: neither skill is registered as the storage layer; everything works against local folders directly.

**Optional but high-value (same as other plugins):**
- `setup-reminders` -- one-time intake that generates the champion's personal `<username>-reminders` skill.
- `setup-inbox` -- one-time intake that generates the champion's personal `<username>-inbox` skill.
- `daily-briefing` (scheduled task) -- morning briefing, extensible to include team-layer content.
- `setup-writing-styles` -- voice intake from writing samples that generates the champion's personal `<username>-writing-styles` skill.

**Admin-only skills:**
- `team-repo-provisioning` -- walks the champion through creating the team's git repo on their chosen provider (git path only).
- `team-box-folder-provisioning` -- walks the champion through creating and sharing the Box folders that form the team's shared substrate (Box path only).
- `team-shared-skills-authoring` -- teaches the champion the conventions for shared skills and helps them author or refactor skills against those conventions.
- `team-onboard-member` -- generates onboarding packs for new team members.
- `exfu-upgrade-from-team-to-admin` -- handles the case where the champion already has the team plugin installed and wants to move to team-admin.

**Reference resources:**
- `${CLAUDE_PLUGIN_ROOT}/resources/substrate-guide.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/team-considerations.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/compliance-briefing.md` -- admin-only; for IT and security reviews.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-general-instructions.md` -- universal user-preferences text installed during Step 13.
- `${CLAUDE_PLUGIN_ROOT}/resources/claude-desktop-cowork-global-instructions.md` -- universal Cowork Global Instructions text installed during Step 13.
- The team's own conventions, inside the shared substrate's team scope (once seeded).

---

## What must be true by the end

- Settings configured for full Cowork capability.
- Storage backend chosen (git, Box, or local-only). The appropriate sync skill is operational, or the local-only trade-off is understood and accepted.
- For git: repo provisioned or connected, remote URL confirmed, seeded structure committed and pushed, champion understands the git rhythm.
- For Box: folders created and shared, access set for the team, `box-filesystem-management` operational, champion understands the no-conflict-detection caveat and the offline-caching fix.
- Shared substrate seeded to v0.3: convention base at its `exfu/v0.3/` with `latest.txt`, team scope created with `scope.md`, first-draft `ways-of-working.md` and `team-members.md` in place, CLAUDE.md guard at the shared root, first index generated.
- Champion's personal substrate established in a separate folder: convention base deployed, user scope at `user/` with `scope.md`, `context/about-me.md`, and `ontology/ways-of-working.md`, at least one personal working scope, CLAUDE.md guard at the personal root.
- Agent registry at the personal root with nightly-index registered; `nightly-agents` scheduled task created. Shared-substrate librarians registered too, or deliberately deferred.
- First index generated at the personal root's `exfu/derived/index.json`.
- Compliance briefing surfaced and reviewed (or at least located for later review).
- Personal `wow` generated with a navigation map pointing at both substrates, noted as team-admin variant, installed in Global Instructions.
- `substrate` skill installed and operational.
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
- **Lope** (`https://lope.works`) -- for teams wanting bespoke skill engineering, agentic workflow development, or internal training. Same practitioner as ExFu, different shape of engagement.
